[← Back to index](../../README.md)

# ClinicalAssignment

> `clinical_assignment` · Group B: patients, assignments, supervision

**Purpose:** records which therapist (and optional supervisor) is responsible for a patient, in which role, and for what period. Implements D-N5, D-N8 and X-1.

```sql
CREATE TABLE clinical_assignment (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id               UUID NOT NULL,
    patient_id              UUID NOT NULL,
    therapist_membership_id UUID NOT NULL,
    role_in_case            TEXT NOT NULL
                            CHECK (role_in_case IN ('primary','co_therapist','observing')),
    supervisor_membership_id UUID,
    started_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at                TIMESTAMPTZ,
    CONSTRAINT fk_ca_patient
        FOREIGN KEY (patient_id, tenant_id)
        REFERENCES patient (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_ca_therapist
        FOREIGN KEY (therapist_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_ca_supervisor
        FOREIGN KEY (supervisor_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT ck_ca_dates CHECK (ended_at IS NULL OR ended_at >= started_at),
    CONSTRAINT uq_ca_id_patient_tenant UNIQUE (id, patient_id, tenant_id)
);
CREATE UNIQUE INDEX uq_ca_one_active_primary
    ON clinical_assignment (patient_id)
    WHERE role_in_case = 'primary' AND ended_at IS NULL;
CREATE UNIQUE INDEX uq_ca_active_pair
    ON clinical_assignment (patient_id, therapist_membership_id)
    WHERE ended_at IS NULL;
CREATE INDEX ix_ca_therapist_active
    ON clinical_assignment (therapist_membership_id, ended_at);
CREATE INDEX ix_ca_supervisor_active
    ON clinical_assignment (supervisor_membership_id, ended_at)
    WHERE supervisor_membership_id IS NOT NULL;
```

**Role values**

| `role_in_case` | Meaning |
|---|---|
| `primary` | The lead therapist. Exactly one may be active per patient. |
| `co_therapist` | Shares treatment. |
| `observing` | Observer/trainee. |

**Constraints and indexes explained**

- Three composite FKs ensure the patient, the therapist and the supervisor all belong to the same tenant as the assignment.
- `uq_ca_one_active_primary`: **at most one active primary** per patient. Because the index is partial (`role_in_case = 'primary' AND ended_at IS NULL`), historical primaries are unrestricted. Note that it enforces "at most one", while the ER notes say "exactly one". The "at least one" half is not enforced by the schema.
- `uq_ca_active_pair`: the same therapist cannot hold two active assignments on one patient.
- `ix_ca_therapist_active`, `ix_ca_supervisor_active`: speed up "which patients does this therapist or supervisor have?".
- `uq_ca_id_patient_tenant`: reserved for future composite FKs. **No table currently references it** (a note-to-assignment link could use it later).

**Design notes**

- When `supervisor_membership_id` is `NULL`, `MATCH SIMPLE` skips the supervisor FK. That is correct.
- **Insert-only, with one allowed update.** Rows are never edited; the only permitted mutation is setting `ended_at` once. Enforcing "once" requires a trigger (Section 12 in Part 2 of the source; the trigger is `enforce_assignment_ended_once`, [trigger summary](../../03-enforcement/triggers/README.md)).
- **Reassignment** is done by ending the old row and inserting a new one, which preserves the history that decisions D2 and D3 rely on.
- Nothing in the schema checks that the assigned therapist actually holds the `therapist` role in `tenant_membership.roles`. That is an application rule.

## Relationships

**Depends on (this table references):** [Patient](patient.md), [TenantMembership](../a-tenancy-identity/tenant-membership.md)

**Referenced by:** no table

## Triggers on this table

- [enforce_assignment_ended_once](../../03-enforcement/triggers/enforce_assignment_ended_once.md): fires on BEFORE UPDATE
- [enforce_archived_read_only](../../03-enforcement/triggers/enforce_archived_read_only.md): applies to this table through the child-table check for archived patients

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[← Patient](patient.md) · [Group overview](README.md) · [ClinicalSupervision →](clinical-supervision.md)
