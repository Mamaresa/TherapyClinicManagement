[← Back to index](../../README.md)

# TreatmentGoal

> `treatment_goal` · Group F: treatment

**Purpose:** a goal inside a treatment plan.

```sql
CREATE TABLE treatment_goal (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id          UUID NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
    patient_id         UUID NOT NULL,
    treatment_plan_id  UUID NOT NULL,
    description        TEXT NOT NULL,
    status             TEXT NOT NULL DEFAULT 'open'
                       CHECK (status IN ('open','met','abandoned')),
    target_date        DATE,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_tg_plan
        FOREIGN KEY (treatment_plan_id, patient_id, tenant_id)
        REFERENCES treatment_plan (id, patient_id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT uq_tg_id_patient_tenant UNIQUE (id, patient_id, tenant_id)
);
CREATE INDEX ix_tg_plan_status
    ON treatment_goal (treatment_plan_id, status);
```

**Source notes (verbatim):**

> Notes: the goal's patient is enforced to match its plan's patient by the (treatment_plan_id, patient_id, tenant_id) composite FK (X-1).

**Column guide and constraints explained**

| Item | Meaning |
|---|---|
| `status` | `open`, `met` or `abandoned`. |
| `target_date` | Optional date the goal is aimed at. |
| `fk_tg_plan` | The goal's `patient_id` must equal the plan's `patient_id` (and tenant). `patient_id` is stored on the goal *only* so this check is possible. |
| `uq_tg_id_patient_tenant` | The key that `progress_entry` targets. |
| `ix_tg_plan_status` | Goals of a plan, by status. |

## Relationships

**Depends on (this table references):** [Tenant](../a-tenancy-identity/tenant.md), [TreatmentPlan](treatment-plan.md)

**Referenced by:** [ProgressEntry](progress-entry.md)

## Triggers on this table

- [enforce_archived_read_only](../../03-enforcement/triggers/enforce_archived_read_only.md): applies to this table through the child-table check for archived patients
- [set_updated_at](../../03-enforcement/triggers/set_updated_at.md): BEFORE UPDATE

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[← TreatmentPlan](treatment-plan.md) · [Group overview](README.md) · [ProgressEntry →](progress-entry.md)
