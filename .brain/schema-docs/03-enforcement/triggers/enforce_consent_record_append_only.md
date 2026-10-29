[← Trigger summary](README.md) · [← Back to index](../../README.md)

# enforce_consent_record_append_only

| | |
|---|---|
| Table | ConsentRecord |
| Fires on | BEFORE UPDATE, BEFORE DELETE |
| Rule | Reject UPDATE and DELETE. Current state is derived from the chain. |

## Explanation

Consent rows are never edited. A patient's current consent state is derived by reading the chain of grants and withdrawals, so changing an old row would rewrite history. The trigger rejects every UPDATE and DELETE.

## Applies to

[ConsentRecord](../../02-tables/c-consent/consent-record.md)

## Requirements for all triggers

Trigger declarations must be ENABLE ALWAYS, and the trigger functions must be owned by a role the runtime role does not belong to (D12). Migration tests must confirm each trigger survives fresh setup, upgrades, and restoration. See the [trigger summary](README.md).
