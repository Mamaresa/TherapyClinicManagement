[← Trigger summary](README.md) · [← Back to index](../../README.md)

# set_updated_at

| | |
|---|---|
| Table | Tables with updated_at |
| Fires on | BEFORE UPDATE |
| Rule | Set NEW.updated_at = now(). |

## Explanation

Keeps updated_at current on every UPDATE. Note that the Part 1 conventions say updated_at is refreshed by application logic; the two statements disagree (see the review notes on Part 2).

## Applies to

every table that has an updated_at column (see each table page)

## Requirements for all triggers

Trigger declarations must be ENABLE ALWAYS, and the trigger functions must be owned by a role the runtime role does not belong to (D12). Migration tests must confirm each trigger survives fresh setup, upgrades, and restoration. See the [trigger summary](README.md).
