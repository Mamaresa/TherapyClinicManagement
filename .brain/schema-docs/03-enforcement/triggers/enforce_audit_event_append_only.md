[← Trigger summary](README.md) · [← Back to index](../../README.md)

# enforce_audit_event_append_only

| | |
|---|---|
| Table | AuditEvent |
| Fires on | BEFORE UPDATE, BEFORE DELETE |
| Rule | Reject UPDATE and DELETE. |

## Explanation

The audit trail must be tamper-resistant. The trigger rejects every UPDATE and DELETE; in addition, the runtime role is not granted UPDATE or DELETE on the table.

## Applies to

[AuditEvent](../../02-tables/i-audit/audit-event.md)

## Requirements for all triggers

Trigger declarations must be ENABLE ALWAYS, and the trigger functions must be owned by a role the runtime role does not belong to (D12). Migration tests must confirm each trigger survives fresh setup, upgrades, and restoration. See the [trigger summary](README.md).
