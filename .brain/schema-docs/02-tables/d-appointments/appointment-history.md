[← Back to index](../../README.md)

# AppointmentHistory

> `appointment_history` · Group D: appointments

**Purpose:** an append-only log of changes to appointments (who changed what, and why). Implements A-6.

```sql
CREATE TABLE appointment_history (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id             UUID NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
    appointment_id        UUID NOT NULL,
    changed_fields        JSONB NOT NULL,
    actor_membership_id   UUID NOT NULL,
    reason                TEXT NOT NULL,
    changed_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_ah_appointment
        FOREIGN KEY (appointment_id, tenant_id)
        REFERENCES appointment (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_ah_actor
        FOREIGN KEY (actor_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT uq_ah_id_tenant UNIQUE (id, tenant_id),
    CONSTRAINT ck_ah_reason CHECK (length(trim(reason)) > 0),
    CONSTRAINT ck_ah_fields_json CHECK (jsonb_typeof(changed_fields) = 'object')
);
CREATE INDEX ix_ah_appointment_time
    ON appointment_history (appointment_id, changed_at);
```

**Source notes (verbatim):**

> Notes: implements A-6. Append-only by trigger (Section 15). changed_fields contains only the columns that changed, with old and new values, so history rows are self-describing without joining to the current Appointment.

**Column guide**

| Column | Meaning |
|---|---|
| `changed_fields` | A JSON object listing only the columns that changed, each with its old and new value. |
| `actor_membership_id` | The member who made the change. |
| `reason` | Why it was changed. Required and must not be blank. |
| `changed_at` | When. |

**Constraints and indexes explained**

- `ck_ah_reason`: `length(trim(reason)) > 0` rejects an empty string and a string of only spaces.
- `ck_ah_fields_json`: `changed_fields` must be a JSON **object** (not an array, string or number).
- `fk_ah_appointment`, `fk_ah_actor`: composite FKs keep the history, the appointment and the actor in one tenant.
- `ix_ah_appointment_time`: read an appointment's history in time order.

**Design notes:** `appointment_history` rows can be read on their own because they hold the changed columns and old/new values; no join to the current appointment is needed to understand a change. The table is append-only through the trigger `enforce_appointment_history_append_only` ([trigger summary](../../03-enforcement/triggers/README.md)).

## Relationships

**Depends on (this table references):** [Appointment](appointment.md), [Tenant](../a-tenancy-identity/tenant.md), [TenantMembership](../a-tenancy-identity/tenant-membership.md)

**Referenced by:** no table

## Triggers on this table

- [enforce_appointment_history_append_only](../../03-enforcement/triggers/enforce_appointment_history_append_only.md): fires on BEFORE UPDATE, BEFORE DELETE

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[← Appointment](appointment.md) · [Group overview](README.md)
