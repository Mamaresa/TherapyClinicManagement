[← Back to index](../../README.md)

# TreatmentPlan

> `treatment_plan` · Group F: treatment

**Purpose:** a patient's treatment plan, with a status and a time span.

```sql
CREATE TABLE treatment_plan (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id             UUID NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
    patient_id            UUID NOT NULL,
    created_by_membership_id UUID NOT NULL,
    title                 TEXT NOT NULL,
    status                TEXT NOT NULL DEFAULT 'active'
                          CHECK (status IN ('active','completed','archived')),
    started_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at              TIMESTAMPTZ,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_tp_patient
        FOREIGN KEY (patient_id, tenant_id)
        REFERENCES patient (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_tp_creator
        FOREIGN KEY (created_by_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT uq_tp_id_patient_tenant UNIQUE (id, patient_id, tenant_id),
    CONSTRAINT ck_tp_dates CHECK (ended_at IS NULL OR ended_at >= started_at),
    CONSTRAINT ck_tp_status_ended CHECK (
        (status IN ('completed','archived') AND ended_at IS NOT NULL)
        OR status = 'active'
    )
);
CREATE INDEX ix_tp_patient_status
    ON treatment_plan (patient_id, status);
```

**Constraints and indexes explained**

- `ck_tp_dates`: the end cannot precede the start.
- `ck_tp_status_ended`: a `completed` or `archived` plan must have an end timestamp. An `active` plan is unconstrained, so it may have `ended_at` set.
- `uq_tp_id_patient_tenant`: the key that `treatment_goal` targets, so a goal's patient always matches its plan's patient.
- `ix_tp_patient_status`: a patient's plans by status.

**Design notes:** the source gives no separate notes for this table. Unlike the assignment tables, there is no partial unique index here, so the schema allows a patient to have several active plans at once.

## Relationships

**Depends on (this table references):** [Patient](../b-patients-assignments/patient.md), [Tenant](../a-tenancy-identity/tenant.md), [TenantMembership](../a-tenancy-identity/tenant-membership.md)

**Referenced by:** [TreatmentGoal](treatment-goal.md)

## Triggers on this table

- [enforce_archived_read_only](../../03-enforcement/triggers/enforce_archived_read_only.md): applies to this table through the child-table check for archived patients
- [set_updated_at](../../03-enforcement/triggers/set_updated_at.md): BEFORE UPDATE

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[Group overview](README.md) · [TreatmentGoal →](treatment-goal.md)
