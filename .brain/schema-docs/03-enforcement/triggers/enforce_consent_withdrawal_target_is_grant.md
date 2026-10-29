[← Trigger summary](README.md) · [← Back to index](../../README.md)

# enforce_consent_withdrawal_target_is_grant

| | |
|---|---|
| Table | ConsentRecord |
| Fires on | BEFORE INSERT |
| Rule | When status = 'withdrawal', verify that withdraws_consent_id refers to a row whose status = 'grant' in the same patient and tenant. |

## Explanation

The self-referencing foreign key proves that a withdrawal points at a row of the same patient and tenant, but not that the target is a grant. This trigger looks up the target row and rejects the insert if its status is not grant.

## Applies to

[ConsentRecord](../../02-tables/c-consent/consent-record.md)

## Requirements for all triggers

Trigger declarations must be ENABLE ALWAYS, and the trigger functions must be owned by a role the runtime role does not belong to (D12). Migration tests must confirm each trigger survives fresh setup, upgrades, and restoration. See the [trigger summary](README.md).
