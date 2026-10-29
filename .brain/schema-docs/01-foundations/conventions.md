[← Back to index](../README.md)

# Conventions

These apply to every table.

| Convention | Detail |
|---|---|
| Primary keys | `UUID`, default `gen_random_uuid()`. |
| Timestamps | `TIMESTAMPTZ` (timezone-aware). |
| Business dates | `DATE`. |
| Local times | `TIME`. |
| Tenant ownership | Tenant-owned tables carry `tenant_id UUID NOT NULL`. |
| Foreign keys | All are `ON DELETE RESTRICT` and `ON UPDATE RESTRICT` unless noted. There are no cascades for clinical or audit data. |
| `updated_at` | Defaults to `now()` and is refreshed by application logic. No trigger is assumed. |

## The composite foreign key pattern

A normal FK such as `patient_id REFERENCES patient(id)` only guarantees the patient exists. It does **not** guarantee the patient belongs to the same tenant as the child row. A bug or an attack could then link a row in tenant A to a patient in tenant B.

The schema prevents this as follows:

1. The parent table exposes a unique key that includes the tenant: `UNIQUE (id, tenant_id)` or `UNIQUE (id, patient_id, tenant_id)`.
2. The child references that whole tuple: `FOREIGN KEY (patient_id, tenant_id) REFERENCES patient (id, tenant_id)`.

Now the database itself rejects any cross-tenant link.

**Why NULL does not bypass this.** PostgreSQL uses `MATCH SIMPLE` by default: if any column of the child's FK tuple is `NULL`, the check is skipped. This is fine here for two reasons:

- A **nullable** reference column (for example `supervisor_membership_id`) being `NULL` means "no supervisor", so skipping the check is the desired behaviour.
- `tenant_id` is `NOT NULL` on tenant-owned tables, so the tenant half of the tuple can never be `NULL`. Nobody can use a `NULL` tenant to dodge the match.

## Why RESTRICT everywhere

Cascading deletes on clinical or audit data are dangerous: one deletion could silently remove records that must be retained. `RESTRICT` forces any removal to be deliberate and explicit. The schema uses end-dating (`ended_at`, `revoked_at`, `archived_at`) instead of deletion.
