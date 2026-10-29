[← Back to index](../../README.md)

# AuditEvent

> `audit_event` · Group I: audit

**Purpose:** the append-only record of who did what, to which resource, with what outcome. Implements U-1.

```sql
CREATE TABLE audit_event (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID REFERENCES tenant(id) ON DELETE RESTRICT,
    actor_type          TEXT NOT NULL CHECK (actor_type IN ('user','system','platform')),
    actor_user_id       UUID REFERENCES app_user(id) ON DELETE RESTRICT,
    actor_membership_id UUID REFERENCES tenant_membership(id) ON DELETE RESTRICT,
    action              TEXT NOT NULL,
    resource_type       TEXT NOT NULL,
    resource_id         UUID,
    outcome             TEXT NOT NULL CHECK (outcome IN ('success','denied','error')),
    occurred_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata            JSONB NOT NULL DEFAULT '{}'::JSONB,
    correlation_id      UUID,
    CONSTRAINT ck_ae_actor_consistency CHECK (
        (actor_type = 'user' AND actor_user_id IS NOT NULL)
        OR (actor_type IN ('system','platform') AND actor_user_id IS NULL)
    ),
    CONSTRAINT ck_ae_membership_requires_user CHECK (
        actor_membership_id IS NULL OR actor_type = 'user'
    ),
    CONSTRAINT ck_ae_tenant_for_clinical_resources CHECK (
        resource_type NOT IN (
            'patient','clinical_assignment','clinical_supervision',
            'supervisory_operational_scope','consent_record','appointment',
            'appointment_history','clinical_note_draft','clinical_note',
            'note_appointment_link','treatment_plan','treatment_goal',
            'progress_entry','assessment_result','patient_file',
            'tenant_membership','membership_grant','invitation'
        )
        OR tenant_id IS NOT NULL
    ),
    CONSTRAINT ck_ae_metadata_json CHECK (jsonb_typeof(metadata) = 'object')
);
CREATE INDEX ix_ae_tenant_time
    ON audit_event (tenant_id, occurred_at);
CREATE INDEX ix_ae_actor_time
    ON audit_event (actor_user_id, occurred_at);
CREATE INDEX ix_ae_resource
    ON audit_event (resource_type, resource_id);
CREATE INDEX ix_ae_action_time
    ON audit_event (action, occurred_at);
```

**Source notes (verbatim):**

> Notes: implements U-1. tenant_id NULL means platform-scoped; the ck_ae_tenant_for_clinical_resources CHECK enforces that any event about a tenant-owned resource must carry a tenant (U-3). The cross-table "actor_membership_id belongs to tenant_id when tenant is set" is not expressible as a composite FK because tenant_id can be NULL; enforced by trigger (Section 15). Append-only: no UPDATE or DELETE grants on the table to the runtime role. metadata must not contain clinical content, patient names, free text, credentials, or signed URLs; this is a policy enforced by code review and a JSON schema validator at write time, not by the database.

**Column guide**

| Column | Meaning |
|---|---|
| `tenant_id` | The clinic the event belongs to. `NULL` means platform-scoped. |
| `actor_type` | `user` (a person), `system` (an automated process) or `platform` (platform staff). |
| `actor_user_id` | The account, when the actor is a user. |
| `actor_membership_id` | The membership the user was acting through, if any. |
| `action` | What was done (free text; the source calls it an action enum in the mapping, but the column has no CHECK). |
| `resource_type`, `resource_id` | What was acted on. |
| `outcome` | `success`, `denied` or `error`. |
| `occurred_at` | When it happened. |
| `metadata` | Extra details as a JSON object. |
| `correlation_id` | Groups events belonging to one request or workflow. |

**Constraints and indexes explained**

- `ck_ae_actor_consistency`: a `user` event must name a user; a `system` or `platform` event must **not**.
- `ck_ae_membership_requires_user`: a membership may be recorded only on a `user` event.
- `ck_ae_tenant_for_clinical_resources`: if the `resource_type` is on the list of tenant-owned resources, then `tenant_id` must be set. Events about other resource types (for example platform-level ones) may have no tenant. This is the check mentioned in the Part 1 cardinality notes.
- `ck_ae_metadata_json`: `metadata` must be a JSON object.
- Four indexes: by tenant and time, by actor and time, by resource, and by action and time.
- **Plain foreign keys.** `actor_membership_id` references `tenant_membership(id)` with a plain FK, not a composite one, because `tenant_id` can be `NULL` and a composite FK would skip its check in that case.

**Design notes**

- **Tenant match.** The rule "the membership belongs to the event's tenant, when a tenant is set" is enforced by the trigger `enforce_audit_membership_tenant_match` ([trigger summary](../../03-enforcement/triggers/README.md)).
- **Append-only.** The trigger `enforce_audit_event_append_only` rejects `UPDATE` and `DELETE`, and the runtime role has no `UPDATE` or `DELETE` grants on the table.
- **What must never go into `metadata`:** clinical content, patient names, free text, credentials or signed URLs. This is a **policy**, enforced by code review and a JSON schema validator at write time. The database does not check it.

## Relationships

**Depends on (this table references):** [User](../a-tenancy-identity/app-user.md), [Tenant](../a-tenancy-identity/tenant.md), [TenantMembership](../a-tenancy-identity/tenant-membership.md)

**Referenced by:** no table

## Triggers on this table

- [enforce_audit_event_append_only](../../03-enforcement/triggers/enforce_audit_event_append_only.md): fires on BEFORE UPDATE, BEFORE DELETE
- [enforce_archived_read_only](../../03-enforcement/triggers/enforce_archived_read_only.md): applies to this table through the child-table check for archived patients
- [enforce_audit_membership_tenant_match](../../03-enforcement/triggers/enforce_audit_membership_tenant_match.md): fires on BEFORE INSERT

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[Group overview](README.md)
