[← Back to index](../../README.md)

# NoteAppointmentLink

> `note_appointment_link` · Group E: clinical notes

**Purpose:** links a finalized note to the appointment(s) it documents, without modifying either row. Implements N-1 and the D-N1 resolution documented in [design decisions (technical resolution)](../../01-foundations/design-decisions.md).

```sql
CREATE TABLE note_appointment_link (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id             UUID NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
    patient_id            UUID NOT NULL,
    note_id               UUID NOT NULL,
    appointment_id        UUID NOT NULL,
    created_by_membership_id UUID NOT NULL,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    removed_at            TIMESTAMPTZ,
    removed_by_membership_id UUID,
    CONSTRAINT fk_nal_note
        FOREIGN KEY (note_id, patient_id, tenant_id)
        REFERENCES clinical_note (id, patient_id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_nal_appointment
        FOREIGN KEY (appointment_id, patient_id, tenant_id)
        REFERENCES appointment (id, patient_id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_nal_creator
        FOREIGN KEY (created_by_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_nal_remover
        FOREIGN KEY (removed_by_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT uq_nal_id_tenant UNIQUE (id, tenant_id),
    CONSTRAINT ck_nal_removal_pair CHECK (
        (removed_at IS NULL AND removed_by_membership_id IS NULL)
        OR (removed_at IS NOT NULL AND removed_by_membership_id IS NOT NULL)
    )
);
CREATE UNIQUE INDEX uq_nal_active
    ON note_appointment_link (note_id, appointment_id)
    WHERE removed_at IS NULL;
CREATE INDEX ix_nal_note
    ON note_appointment_link (note_id);
CREATE INDEX ix_nal_appointment
    ON note_appointment_link (appointment_id);
```

**Source notes (verbatim):**

> Notes: implements N-1 and the D-N1 resolution documented in Part 1. The link table is mutable (link can be created and removed), but the underlying ClinicalNote and Appointment rows are never modified. Both the note and the appointment must belong to the same patient and tenant; enforced by composite FKs, so a note from one patient cannot be linked to another patient's appointment.

**Column guide**

| Column | Meaning |
|---|---|
| `patient_id` | Repeated here on purpose, so both composite FKs can check it. |
| `note_id`, `appointment_id` | The two things being linked. |
| `created_by_membership_id` | Who created the link. |
| `removed_at`, `removed_by_membership_id` | Set when the link is removed. |

**Constraints and indexes explained**

- `fk_nal_note` and `fk_nal_appointment` both include `patient_id` and `tenant_id`. Because both use the **same** `patient_id` column of the link row, the note and the appointment are forced to belong to the **same patient**.
- `ck_nal_removal_pair`: `removed_at` and `removed_by_membership_id` are either both empty or both set.
- `uq_nal_active` (partial unique): the same note and appointment can be linked only once while the link is active. After removal, they can be linked again as a new row.
- Indexes on `note_id` and `appointment_id` support looking up links from either side.

**Design notes**

- The link is **soft-removed**, never deleted. The only update allowed by the trigger `enforce_note_link_append_only` is setting the two removal columns once, from `NULL` to a value ([trigger summary](../../03-enforcement/triggers/README.md)).
- One note can be linked to several appointments, and one appointment to several notes (for example an original note and its addendum).

## Relationships

**Depends on (this table references):** [Appointment](../d-appointments/appointment.md), [ClinicalNote](clinical-note.md), [Tenant](../a-tenancy-identity/tenant.md), [TenantMembership](../a-tenancy-identity/tenant-membership.md)

**Referenced by:** no table

## Triggers on this table

- [enforce_note_link_append_only](../../03-enforcement/triggers/enforce_note_link_append_only.md): fires on BEFORE UPDATE, BEFORE DELETE

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[← ClinicalNote](clinical-note.md) · [Group overview](README.md)
