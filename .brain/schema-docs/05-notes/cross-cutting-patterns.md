[← Back to index](../README.md)

# Cross-cutting patterns explained



## Time-bounded relationships instead of deletions

`tenant_membership`, `membership_grant`, `clinical_assignment`, `clinical_supervision` and `supervisory_operational_scope` all follow one pattern: a row is valid while its end column is `NULL`, and ending it never deletes it. This yields:

- A history of who could see what and when.
- Safe re-granting (a new row, not an un-delete).
- Partial unique indexes that enforce "only one active" without blocking history.

## Partial unique indexes

`CREATE UNIQUE INDEX ... WHERE <active condition>` is used repeatedly. It enforces uniqueness only among rows that satisfy the `WHERE`. That is how the schema says "one active primary therapist per patient" while keeping any number of ended ones.

## Tenant isolation at the database level

Every cross-table link between tenant-owned rows uses a composite `(id, tenant_id)` FK. Tenant isolation is therefore not purely an application convention; the database rejects cross-tenant links. The exceptions are the single-column references from `session.tenant_context_id`, `tenant_membership.tenant_id`, `invitation.tenant_id` and `patient.tenant_id` to `tenant(id)`, which are the roots of the tenant relationship itself.

## What lives outside the schema

| Concern | Where it is enforced |
|---|---|
| Email normalization | Application (implementation requirement; [application-level rules](../03-enforcement/application-level-rules.md)) |
| "Set `ended_at` once" on assignments | Trigger (`enforce_assignment_ended_once`, [trigger summary](../03-enforcement/triggers/README.md)) |
| Clinical vs operational access | Access predicate |
| Platform roles never grant clinical access | Access predicate |
| Invitation responses must not leak account existence | Application |
| Field-level encryption and keys | Application / key management |
| `updated_at` refresh | Application logic |
