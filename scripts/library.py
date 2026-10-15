"""Empty local library and read-only Lark snapshot refresh. Python 3.10+."""
import argparse
import json
import re
import shutil
import sqlite3
import subprocess
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

TABLES = ('sources', 'snapshots', 'knowledge', 'products', 'prices', 'annotations', 'operations')


def now():
    return datetime.now(timezone.utc).isoformat()


def connect(path):
    if not path.is_file():
        raise ValueError('Database missing; run init first.')
    db = sqlite3.connect(path)
    db.execute('PRAGMA foreign_keys=ON')
    return db


def initialize(root, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents replacing an existing personal library.
    with path.open('xb'):
        pass
    with closing(sqlite3.connect(path)) as db:
        db.executescript((root / 'schema.sql').read_text(encoding='utf-8-sig'))
    return {'created': str(path), 'business_rows': 0}


def read_sources(path):
    config = json.loads(path.read_text(encoding='utf-8-sig'))
    sources = config['sources']
    if not isinstance(sources, list):
        raise ValueError('sources must be an array')
    ids = set()
    for src in sources:
        sid = src.get('id', '')
        if not re.fullmatch(r'[A-Za-z0-9_-]+', sid) or sid in ids:
            raise ValueError('Source IDs must be unique letters/digits/_/-')
        ids.add(sid)
        if src.get('library') not in ('knowledge', 'products', 'prices'):
            raise ValueError('Invalid library')
        if src.get('kind') not in ('lark_doc', 'lark_sheet', 'manual'):
            raise ValueError('Invalid source kind')
        if not isinstance(src.get('enabled', True), bool):
            raise ValueError('enabled must be true or false')
        url = src.get('url', '')
        if not isinstance(url, str) or not url:
            raise ValueError('Source URL is required')
        if src['kind'].startswith('lark_'):
            # No commands or auth query strings in URL configuration.
            if not re.fullmatch(r'https://[A-Za-z0-9.-]+/(wiki|docx|sheets|spreadsheets)/[A-Za-z0-9]+', url):
                raise ValueError('Use a clean HTTPS document URL without query parameters')
        if src['kind'] == 'lark_sheet':
            if not re.fullmatch(r'[A-Za-z0-9]+', src.get('sheet_id') or ''):
                raise ValueError('sheet_id is required')
            if not re.fullmatch(r'[A-Z]+[1-9][0-9]*:[A-Z]+[1-9][0-9]*', src.get('range') or ''):
                raise ValueError('A bounded sheet range such as A1:M100 is required')
    return sources


def register(db, sources):
    with db:
        for s in sources:
            row = (s['library'], s['kind'], s['url'], s.get('sheet_id'), s.get('range'))
            existing = db.execute('SELECT library,kind,url,sheet_id,range_a1 FROM sources WHERE id=?', (s['id'],)).fetchone()
            if existing and existing != row:
                raise ValueError('Source binding changed; use a new source ID to preserve provenance')
            db.execute('INSERT INTO sources(id,library,kind,url,sheet_id,range_a1,enabled) VALUES(?,?,?,?,?,?,?) '
                       'ON CONFLICT(id) DO UPDATE SET enabled=excluded.enabled', (s['id'], *row, int(s.get('enabled', True))))


def lark_call(args):
    executable = shutil.which('lark-cli')
    if not executable:
        raise RuntimeError('lark-cli is not installed or not on PATH')
    result = subprocess.run([executable, *args], capture_output=True, text=True, encoding='utf-8', timeout=120, shell=False)
    # Do not echo tool stderr; it may contain authentication details.
    if result.returncode:
        raise RuntimeError('Lark read failed; inspect authentication/permissions using the official CLI')
    try:
        value = json.loads(result.stdout.lstrip('\ufeff'))
    except ValueError as exc:
        raise RuntimeError('CLI did not return JSON; check installed CLI compatibility') from exc
    if value.get('ok') is not True:
        raise RuntimeError('Lark response is not successful')
    return value


def incomplete(value):
    if isinstance(value, dict):
        if any(value.get(k) for k in ('has_more', 'truncated', 'is_truncated')):
            return True
        return any(incomplete(v) for v in value.values())
    if isinstance(value, list):
        return any(incomplete(v) for v in value)
    return False


def refresh(db, source, caller=lark_call):
    sid, attempt = source['id'], now()
    if not source.get('enabled', True):
        raise ValueError('Source is disabled')
    try:
        if source['kind'] == 'lark_doc':
            payload = caller(['docs', '+fetch', '--as', 'user', '--doc', source['url'], '--detail', 'with-ids'])
            document = payload['data']['document']
            if not isinstance(document.get('content'), str):
                raise ValueError('Missing document content')
            revision = document['revision_id']
        elif source['kind'] == 'lark_sheet':
            info = caller(['sheets', '+workbook-info', '--as', 'user', '--url', source['url']])
            sheets = info['data']['sheets']
            if not any(x['sheet_id'] == source['sheet_id'] for x in sheets):
                raise ValueError('Configured sheet no longer exists')
            payload = caller(['sheets', '+csv-get', '--as', 'user', '--url', source['url'],
                              '--sheet-id', source['sheet_id'], '--range', source['range']])
            if not isinstance(payload['data'].get('annotated_csv'), str):
                raise ValueError('Missing sheet content')
            revision = payload['data']['revision']
        else:
            raise ValueError('Manual source: use its authorized reader; automatic refresh is unsupported')
        if incomplete(payload):
            raise ValueError('Partial response rejected; narrow range or finish pagination separately')
        if revision is None:
            raise ValueError('Missing source revision')
        with db:
            db.execute('INSERT INTO snapshots VALUES(?,?,?,?) ON CONFLICT(source_id) DO UPDATE SET '
                       'revision=excluded.revision,fetched_at=excluded.fetched_at,payload_json=excluded.payload_json',
                       (sid, str(revision), attempt, json.dumps(payload['data'], ensure_ascii=False)))
            db.execute("UPDATE sources SET last_attempt_at=?,last_status='ok' WHERE id=?", (attempt, sid))
        return {'source': sid, 'status': 'ok', 'revision': str(revision), 'fetched_at': attempt,
                'scope': source.get('range') or 'document', 'business_records_updated': False}
    except Exception:
        with db:
            db.execute("UPDATE sources SET last_attempt_at=?,last_status='error' WHERE id=?", (attempt, sid))
        raise


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('init', 'status', 'register', 'refresh'))
    parser.add_argument('--db', type=Path, default=root / 'data/library.sqlite')
    parser.add_argument('--config', type=Path, default=root / 'config/sources.json')
    parser.add_argument('--source')
    args = parser.parse_args()
    try:
        if args.command == 'init':
            output = initialize(root, args.db)
        else:
            with closing(connect(args.db)) as db:
                if args.command == 'status':
                    output = {'integrity': db.execute('PRAGMA integrity_check').fetchone()[0],
                              'counts': {t: db.execute('SELECT count(*) FROM ' + t).fetchone()[0] for t in TABLES},
                              'sources': db.execute('SELECT id,last_status,last_attempt_at FROM sources').fetchall()}
                else:
                    sources = read_sources(args.config)
                    register(db, sources)
                    if args.command == 'register':
                        output = {'registered': len(sources)}
                    else:
                        matches = [s for s in sources if s['id'] == args.source]
                        if len(matches) != 1:
                            raise ValueError('Specify --source with an ID in the config')
                        output = refresh(db, matches[0])
        print(json.dumps(output, ensure_ascii=False, indent=2))
    except (ValueError, RuntimeError, OSError, KeyError, sqlite3.Error, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'status': 'error', 'message': str(exc)}, ensure_ascii=False))
        raise SystemExit(1)


if __name__ == '__main__':
    main()
