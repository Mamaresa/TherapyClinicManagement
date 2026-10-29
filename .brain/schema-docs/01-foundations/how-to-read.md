[← Back to index](../README.md)

# How to read this document

The original message is a schema specification. This version keeps every table definition and rule from it and adds, for each table:

- **Purpose:** what the table is for in the product.
- **Column guide:** what each non-obvious column means.
- **Constraints and indexes explained:** what each rule enforces and why.
- **Design notes:** the rationale and the traps to avoid.

The schema targets **PostgreSQL**. It models a multi-tenant (multi-clinic) clinical practice system where therapists, supervisors, assistants and admins work with patient records, and where tenant isolation and auditability are central.

Terms used throughout:

| Term | Meaning |
|---|---|
| Tenant | One clinic or practice. All clinical data belongs to exactly one tenant. |
| Membership | A user's participation in a tenant, with roles. A user can have memberships in several tenants over time. |
| Active | A row whose `ended_at` (or `revoked_at`) is `NULL`. |
| Composite FK | A foreign key over `(id, tenant_id)` or `(id, patient_id, tenant_id)` so a child row cannot point to a parent in a different tenant. |
