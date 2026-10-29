[← Trigger summary](README.md) · [← Back to index](../../README.md)

# enforce_audit_membership_tenant_match

| | |
|---|---|
| Table | AuditEvent |
| Fires on | BEFORE INSERT |
| Rule | When actor_membership_id IS NOT NULL and tenant_id IS NOT NULL, verify the membership belongs to the tenant. |

## Explanation

audit_event.tenant_id can be NULL, so a composite foreign key cannot tie the membership to the tenant. The trigger checks the match only when both a membership and a tenant are present.

## Applies to

[AuditEvent](../../02-tables/i-audit/audit-event.md)

## Requirements for all triggers

Trigger declarations must be ENABLE ALWAYS, and the trigger functions must be owned by a role the runtime role does not belong to (D12). Migration tests must confirm each trigger survives fresh setup, upgrades, and restoration. See the [trigger summary](README.md).
