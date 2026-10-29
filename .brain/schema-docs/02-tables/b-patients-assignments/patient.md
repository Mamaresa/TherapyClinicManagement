[← Back to index](../../README.md)

# Patient

> `patient` · Group B: patients, assignments, supervision

**Purpose:** the person receiving care at one clinic. Clinic-scoped identity (D1).

```sql
CREATE TABLE patient (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id             UUID NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
    first_name            TEXT NOT NULL,
    last_name             TEXT NOT NULL,
    normalized_first_name TEXT NOT NULL,
    normalized_last_name  TEXT NOT NULL,
    dob                   DATE,
    contact_phone_enc     BYTEA,
    contact_email_enc     BYTEA,
    contact_address_enc   BYTEA,
    emergency_contact_enc BYTEA,
    intake_data           JSONB NOT NULL DEFAULT '{}'::JSONB,
    status                TEXT NOT NULL DEFAULT 'active'
                          CHECK (status IN ('active','archived')),
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    archived_at           TIMESTAMPTZ,
    CONSTRAINT uq_patient_id_tenant UNIQUE (id, tenant_id),
    CONSTRAINT ck_patient_archived CHECK (
        (status = 'archived' AND archived_at IS NOT NULL)
        OR status = 'active'
    ),
    CONSTRAINT ck_patient_intake_version CHECK (intake_data ? 'schema_version')
);
CREATE INDEX ix_patient_tenant_status
    ON patient (tenant_id, status);
CREATE INDEX ix_patient_tenant_name
    ON patient (tenant_id, normalized_last_name, normalized_first_name)
    WHERE status = 'active';
```

**Column guide**

| Column | Meaning |
|---|---|
| `first_name`, `last_name` | Names as entered (display). |
| `normalized_first_name`, `normalized_last_name` | Folded forms used for searching (A-4). |
| `dob` | Date of birth, optional. |
| `contact_*_enc`, `emergency_contact_enc` | Application-encrypted values stored as `BYTEA`. |
| `intake_data` | Structured intake answers as JSONB, carrying a `schema_version` key. |
| `status` / `archived_at` | Active or archived. |

**Constraints and indexes explained**

- `uq_patient_id_tenant`: lets every patient-related child table use a composite FK.
- `ck_patient_archived`: archived patients must have a timestamp.
- `ck_patient_intake_version`: `intake_data ? 'schema_version'` uses the JSONB `?` operator ("has this top-level key"). Every intake document must declare its version, so a later change in intake structure can be detected and migrated.
- `ix_patient_tenant_status`: lists a tenant's patients by status.
- `ix_patient_tenant_name`: partial index over active patients for name lookups.

**Design notes**

- **Persian search.** Plain B-tree indexes on raw names do not support folded matching, which is why the `normalized_*` columns exist. A plain B-tree on those columns supports exact and prefix matches on the folded form, not fuzzy or substring matching.
- **Encryption.** Contact and emergency fields are stored as `BYTEA` ciphertext so plaintext never reaches the DBMS. Key management is out of scope for this schema. Consequence: these columns cannot be searched or indexed by value.
- **No `primary_therapist_id`.** The current primary therapist is derived from `clinical_assignment`, so there is no second place that could disagree.
- Names (`first_name`, `last_name`, `dob`) are **not** encrypted at column level in this design, a deliberate trade-off to keep search practical.

## Relationships

**Depends on (this table references):** [Tenant](../a-tenancy-identity/tenant.md)

**Referenced by:** [Appointment](../d-appointments/appointment.md), [AssessmentResult](../g-assessments/assessment-result.md), [ClinicalAssignment](clinical-assignment.md), [ClinicalNote](../e-clinical-notes/clinical-note.md), [ClinicalNoteDraft](../e-clinical-notes/clinical-note-draft.md), [ClinicalSupervision](clinical-supervision.md), [ConsentRecord](../c-consent/consent-record.md), [PatientFile](../h-files/patient-file.md), [ProgressEntry](../f-treatment/progress-entry.md), [TreatmentPlan](../f-treatment/treatment-plan.md)

## Triggers on this table

- [enforce_archived_read_only](../../03-enforcement/triggers/enforce_archived_read_only.md): fires on BEFORE INSERT, BEFORE UPDATE
- [set_updated_at](../../03-enforcement/triggers/set_updated_at.md): BEFORE UPDATE

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[Group overview](README.md) · [ClinicalAssignment →](clinical-assignment.md)
