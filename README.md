# Sales Library Starter

[中文说明](README.zh-CN.md)

A reusable AI skill and empty database schema for building your own knowledge, product/SKU, and price libraries, with an Odoo operating workflow. Bring your own documents, accounts, and authorized tools. No company data, private source links, credentials, or preconfigured ERP connection are included.

The skill instructions are currently in Chinese. This English guide covers setup and capabilities; an AI assistant can translate the workflow when needed.

## What works

- A local SQLite schema with seven empty tables, initialized using Python's standard library.
- A read-only Lark/Feishu document and spreadsheet snapshot reader using an existing `lark-cli` installation.
- AI instructions for source attribution, product variants, discontinued SKUs, price validity, and business-data review.
- An Odoo workflow for lookup, quotation preparation, explicitly authorized operations, and readback verification.

The Odoo component is an agent workflow, not an API connector. It needs your existing browser or connector and instance-specific field mappings. PDF price extraction and structured business-data ingestion are review steps, not automatic features of the refresh script.

## Quick start

Download the repository using **Code → Download ZIP**, or clone it, then open its folder in your AI coding client. Install Python 3.10+ and run:

```sh
python scripts/library.py init
python scripts/library.py status
```

The status should show zero rows in all seven tables. Initialization refuses to overwrite an existing database. Runtime databases are ignored by Git; each user creates their own.

Copy `skills/sales-library-workspace` to your client's skill directory, or ask your assistant to read its `SKILL.md` directly. Keep this project folder available: it contains the scripts, schema, and configuration templates used by the skill.

Try this prompt:

> Use sales-library-workspace in this project. Help me build my own knowledge, SKU, and price libraries from the sources I provide. Inspect available tools first, configure one source, and verify a read. For Odoo, start with read-only capability discovery. Explain results in English. Do not populate the database with example business records.

## Connect your sources

Copy `config/sources.example.json` to `config/sources.json`. Its source list starts empty. See [source configuration](skills/sales-library-workspace/references/sources.md) for the required fields.

For Lark/Feishu, use your own working `lark-cli` login and source permissions. After configuration:

```sh
python scripts/library.py refresh --source YOUR_SOURCE_ID
```

For Odoo, copy `config/odoo.example.json` to `config/odoo.json` and let the assistant inspect your authorized instance and tools. Keep passwords, API keys, and session credentials in your existing credential system, not these files.

Users outside the original organization can download and adapt this project. Downloading it does not grant access to any organization's Feishu documents or Odoo instance. Without Feishu, you can still use the local schema and AI workflows with your own files or available readers; the bundled automatic refresh supports Lark/Feishu only.

## Freshness and limitations

Refresh is on demand, not a background synchronization service. A source snapshot is separate from reviewed knowledge, product, and price records. A successful download does not make an expired price valid. Refresh failures preserve the previous snapshot and record an error; partial responses are rejected.

Local behavior tests and live document/bounded spreadsheet reads have passed in one Windows environment. This does not certify your account, operating system, Odoo fields, or production operations. Use a test environment before authorizing writes. Do not commit a populated workspace or private configuration.

## Project contents

`skills/` contains the workflow; `scripts/library.py` handles database initialization and source snapshots; `schema.sql` defines the empty library; `config/` contains blank configuration templates. See [public-package review](PUBLIC_REVIEW.md) for release scope.

## License status

No open-source license has been selected. Public visibility alone does not grant general redistribution or modification rights. A license must be chosen before presenting this as an open-source release.
