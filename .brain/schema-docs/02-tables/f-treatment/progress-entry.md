[← Back to index](../../README.md)

# ProgressEntry

> `progress_entry` · Group F: treatment

**Purpose:** a dated progress record for a patient, optionally tied to a goal.

```sql
CREATE TABLE progress_entry (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id              UUID NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
    patient_id             UUID NOT NULL,
    treatment_goal_id      UUID,
    recorded_by_membership_id UUID NOT NULL,
    recorded_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    score                  NUMERIC,
    notes                  TEXT,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_pe_patient
        FOREIGN KEY (patient_id, tenant_id)
        REFERENCES patient (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_pe_goal
        FOREIGN KEY (treatment_goal_id, patient_id, tenant_id)
        REFERENCES treatment_goal (id, patient_id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_pe_recorder
        FOREIGN KEY (recorded_by_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT uq_pe_id_patient_tenant UNIQUE (id, patient_id, tenant_id),
    CONSTRAINT ck_pe_notes_length CHECK (notes IS NULL OR length(notes) <= 8000)
);
CREATE INDEX ix_pe_patient_time
    ON progress_entry (patient_id, recorded_at);
CREATE INDEX ix_pe_goal_time
    ON progress_entry (treatment_goal_id, recorded_at)
    WHERE treatment_goal_id IS NOT NULL;
```

**Source notes (verbatim):**

> Notes: treatment_goal_id is nullable. When NULL, MATCH SIMPLE skips the composite FK; that is the intended behaviour for a progress note not yet tied to a goal. When set, all three columns must match, so a goal from another patient cannot be referenced.

**Column guide and constraints explained**

| Item | Meaning |
|---|---|
| `treatment_goal_id` | Optional link to a goal. |
| `score` | An optional numeric score (`NUMERIC`, no range check in the schema). |
| `notes` | Optional free text, at most 8000 characters (`ck_pe_notes_length`). |
| `fk_pe_patient` | Always checks the patient and tenant, whether or not a goal is linked. |
| `fk_pe_goal` | When a goal is given, the goal must belong to the same patient and tenant. |
| `ix_pe_goal_time` | Partial index, only over entries that have a goal. |

## Relationships

**Depends on (this table references):** [Patient](../b-patients-assignments/patient.md), [Tenant](../a-tenancy-identity/tenant.md), [TenantMembership](../a-tenancy-identity/tenant-membership.md), [TreatmentGoal](treatment-goal.md)

**Referenced by:** no table

## Triggers on this table

- [enforce_archived_read_only](../../03-enforcement/triggers/enforce_archived_read_only.md): applies to this table through the child-table check for archived patients

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[← TreatmentGoal](treatment-goal.md) · [Group overview](README.md)
