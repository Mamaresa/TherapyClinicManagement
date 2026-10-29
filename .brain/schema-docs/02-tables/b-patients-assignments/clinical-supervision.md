[← Back to index](../../README.md)

# ClinicalSupervision

> `clinical_supervision` · Group B: patients, assignments, supervision

**Purpose:** gives a supervisor clinical access to **one specific patient** supervised through a specific therapist (D9, X-4 part 1).

```sql
CREATE TABLE clinical_supervision (
    id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id                UUID NOT NULL,
    supervisor_membership_id UUID NOT NULL,
    patient_id               UUID NOT NULL,
    therapist_membership_id  UUID NOT NULL,
    started_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at                 TIMESTAMPTZ,
    CONSTRAINT fk_cs_supervisor
        FOREIGN KEY (supervisor_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_cs_therapist
        FOREIGN KEY (therapist_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_cs_patient
        FOREIGN KEY (patient_id, tenant_id)
        REFERENCES patient (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT ck_cs_dates CHECK (ended_at IS NULL OR ended_at >= started_at),
    CONSTRAINT uq_cs_id_tenant UNIQUE (id, tenant_id)
);
CREATE UNIQUE INDEX uq_cs_active_pair
    ON clinical_supervision (supervisor_membership_id, patient_id)
    WHERE ended_at IS NULL;
CREATE INDEX ix_cs_patient_active
    ON clinical_supervision (patient_id, ended_at);
```

**Design notes**

- `patient_id` is `NOT NULL`: a supervisor reaches clinical content only for specific patients, never for "all patients of a therapist".
- All three composite FKs force supervisor, therapist and patient into the same tenant.
- `uq_cs_active_pair`: a supervisor has at most one active supervision per patient.
- The schema does not check that `therapist_membership_id` is actually assigned to the patient or that the supervisor is not the same person as the therapist. There is no self-check here, unlike in 7.4.

## Relationships

**Depends on (this table references):** [Patient](patient.md), [TenantMembership](../a-tenancy-identity/tenant-membership.md)

**Referenced by:** no table

## Triggers on this table

None.

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[← ClinicalAssignment](clinical-assignment.md) · [Group overview](README.md) · [SupervisoryOperationalScope →](supervisory-operational-scope.md)
