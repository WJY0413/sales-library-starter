PRAGMA foreign_keys=ON;
CREATE TABLE sources (
 id TEXT PRIMARY KEY, library TEXT NOT NULL CHECK(library IN ('knowledge','products','prices')),
 kind TEXT NOT NULL CHECK(kind IN ('lark_doc','lark_sheet','manual')), url TEXT NOT NULL,
 sheet_id TEXT, range_a1 TEXT, enabled INTEGER NOT NULL DEFAULT 1 CHECK(enabled IN (0,1)),
 last_attempt_at TEXT, last_status TEXT NOT NULL DEFAULT 'never' CHECK(last_status IN ('never','ok','error'))
);
CREATE TABLE snapshots (
 source_id TEXT PRIMARY KEY REFERENCES sources(id), revision TEXT NOT NULL,
 fetched_at TEXT NOT NULL, payload_json TEXT NOT NULL
);
CREATE TABLE knowledge (
 id TEXT PRIMARY KEY, title TEXT NOT NULL, summary TEXT NOT NULL,
 source_id TEXT NOT NULL REFERENCES sources(id), source_locator TEXT NOT NULL,
 source_revision TEXT NOT NULL, verified_at TEXT NOT NULL
);
CREATE TABLE products (
 id TEXT PRIMARY KEY, sku TEXT NOT NULL, name TEXT NOT NULL, market TEXT,
 variant TEXT, unit TEXT, lifecycle TEXT NOT NULL DEFAULT 'unknown', bundle_rules TEXT,
 source_id TEXT NOT NULL REFERENCES sources(id), source_locator TEXT NOT NULL,
 source_revision TEXT NOT NULL, verified_at TEXT NOT NULL
);
CREATE TABLE prices (
 id TEXT PRIMARY KEY, product_id TEXT NOT NULL REFERENCES products(id),
 amount TEXT, currency TEXT, unit TEXT, market TEXT, warehouse TEXT, incoterm TEXT,
 price_type TEXT, min_qty TEXT, max_qty TEXT, tax_basis TEXT, valid_from TEXT, valid_to TEXT,
 review_state TEXT NOT NULL DEFAULT 'unverified' CHECK(review_state IN ('unverified','verified','retired')),
 source_id TEXT NOT NULL REFERENCES sources(id), source_locator TEXT NOT NULL,
 source_revision TEXT NOT NULL, verified_at TEXT NOT NULL
);
CREATE TABLE annotations (
 id TEXT PRIMARY KEY, entity_type TEXT NOT NULL, entity_id TEXT NOT NULL,
 note TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE operations (
 id TEXT PRIMARY KEY, instance_url TEXT NOT NULL, action TEXT NOT NULL,
 target TEXT NOT NULL, remote_id TEXT, authorization_reference TEXT,
 state TEXT NOT NULL, readback_json TEXT, updated_at TEXT NOT NULL
);
PRAGMA user_version=1;
