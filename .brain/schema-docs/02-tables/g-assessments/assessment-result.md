[← Back to index](../../README.md)

# AssessmentResult

> `assessment_result` · Group G: assessments

**Purpose:** a recorded result of a clinical assessment (questionnaire, scale or test), optionally with an attached file.

```sql
CREATE TABLE assessment_result (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id              UUID NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
    patient_id             UUID NOT NULL,
    assessment_type        TEXT NOT NULL,
    recorded_at            TIMESTAMPTZ NOT NULL,
    scores                 JSONB NOT NULL,
    recorded_by_membership_id UUID NOT NULL,
    file_id                UUID,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_ar_patient
        FOREIGN KEY (patient_id, tenant_id)
        REFERENCES patient (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_ar_recorder
        FOREIGN KEY (recorded_by_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_ar_file
        FOREIGN KEY (file_id, patient_id, tenant_id)
        REFERENCES patient_file (id, patient_id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT uq_ar_id_patient_tenant UNIQUE (id, patient_id, tenant_id),
    CONSTRAINT ck_ar_scores_json CHECK (jsonb_typeof(scores) = 'object')
);
CREATE INDEX ix_ar_patient_time
    ON assessment_result (patient_id, recorded_at);
CREATE INDEX ix_ar_type
    ON assessment_result (patient_id, assessment_type, recorded_at);
```

**Column guide and constraints explained**

| Item | Meaning |
|---|---|
| `assessment_type` | Which assessment (free text, no CHECK). |
| `recorded_at` | When the assessment was taken. Supplied by the caller, with no default, unlike `created_at`. |
| `scores` | The scores as a JSON object (`ck_ar_scores_json`). |
| `file_id` | Optional attached file. `fk_ar_file` is a three-column composite FK, so the file must belong to the same patient and tenant. |
| `ix_ar_type` | Look up a patient's results of one type over time. |

**Design notes:** the source gives no separate notes for this table. It has no immutability trigger in the source's trigger list, so assessment results are mutable by default.

## Relationships

**Depends on (this table references):** [Patient](../b-patients-assignments/patient.md), [PatientFile](../h-files/patient-file.md), [Tenant](../a-tenancy-identity/tenant.md), [TenantMembership](../a-tenancy-identity/tenant-membership.md)

**Referenced by:** no table

## Triggers on this table

- [enforce_archived_read_only](../../03-enforcement/triggers/enforce_archived_read_only.md): applies to this table through the child-table check for archived patients

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[Group overview](README.md)
