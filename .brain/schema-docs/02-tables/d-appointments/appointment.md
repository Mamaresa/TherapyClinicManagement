[← Back to index](../../README.md)

# Appointment

> `appointment` · Group D: appointments

**Purpose:** a scheduled session between one patient and one therapist. Implements D6 and A-1.

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE appointment (
    id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id                UUID NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
    patient_id               UUID NOT NULL,
    therapist_membership_id  UUID NOT NULL,
    starts_at_utc            TIMESTAMPTZ NOT NULL,
    ends_at_utc              TIMESTAMPTZ NOT NULL,
    local_start_date         DATE NOT NULL,
    local_start_time         TIME NOT NULL,
    local_timezone           TEXT NOT NULL,
    status                   TEXT NOT NULL DEFAULT 'scheduled'
                             CHECK (status IN ('scheduled','completed','cancelled','no_show')),
    cancellation_reason      TEXT,
    created_by_membership_id UUID NOT NULL,
    created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_appt_patient
        FOREIGN KEY (patient_id, tenant_id)
        REFERENCES patient (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_appt_therapist
        FOREIGN KEY (therapist_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_appt_creator
        FOREIGN KEY (created_by_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT uq_appt_id_tenant UNIQUE (id, tenant_id),
    CONSTRAINT uq_appt_id_patient_tenant UNIQUE (id, patient_id, tenant_id),
    CONSTRAINT ck_appt_times CHECK (ends_at_utc > starts_at_utc),
    CONSTRAINT ck_appt_cancel_reason CHECK (
        (status = 'cancelled' AND cancellation_reason IS NOT NULL)
        OR status <> 'cancelled'
    ),
    CONSTRAINT ex_appt_overlap EXCLUDE USING gist (
        therapist_membership_id WITH =,
        tstzrange(starts_at_utc, ends_at_utc) WITH &&
    ) WHERE (status <> 'cancelled')
);
CREATE INDEX ix_appt_therapist_time
    ON appointment (tenant_id, therapist_membership_id, starts_at_utc);
CREATE INDEX ix_appt_patient_time
    ON appointment (tenant_id, patient_id, starts_at_utc);
CREATE INDEX ix_appt_local_date
    ON appointment (tenant_id, therapist_membership_id, local_start_date);
```

**Source notes (verbatim):**

> Notes: implements D6 and A-1. The negative predicate (status <> 'cancelled') fails safe when new statuses are added; no_show retains the slot by default. btree_gist is trusted on PG18; a CREATE EXTENSION requires the database-level privilege described in the research note. UTC/local consistency is enforced by a trigger (Section 15), not a CHECK, because time zone conversion is not immutable. The two UNIQUE constraints on (id, tenant_id) and (id, patient_id, tenant_id) enable downstream composite FKs from AppointmentHistory and NoteAppointmentLink.

**Column guide**

| Column | Meaning |
|---|---|
| `therapist_membership_id` | The therapist who will hold the session. It is a *membership*, not a user, so the same person at two clinics has two different values. |
| `starts_at_utc`, `ends_at_utc` | The absolute instants the session starts and ends. Used for overlap detection and ordering. |
| `local_start_date`, `local_start_time`, `local_timezone` | The wall-clock time as the clinic sees it (for example 09:00 in `Asia/Tehran`). Stored separately so reports and reminders can use the local date without conversions. |
| `status` | `scheduled`, `completed`, `cancelled` or `no_show`. |
| `cancellation_reason` | Required when cancelled. |
| `created_by_membership_id` | Who booked it. |

**Constraints and indexes explained**

- `ck_appt_times`: the end must be after the start.
- `ck_appt_cancel_reason`: a cancelled appointment must have a reason. The check is one-directional: a reason may exist on a non-cancelled appointment.
- `ex_appt_overlap`: an **exclusion constraint**. It says that no two rows may have the **same** `therapist_membership_id` **and** **overlapping** time ranges, among rows that satisfy the `WHERE` clause. Details:
  - `tstzrange(starts_at_utc, ends_at_utc)` builds a half-open time range, so a session ending at 10:00 and another starting at 10:00 do **not** overlap.
  - `WITH =` on the therapist column and `WITH &&` (overlaps) on the range means "same therapist and overlapping time is forbidden".
  - GiST normally cannot index plain equality on a `UUID`; the `btree_gist` extension supplies that capability, which is why `CREATE EXTENSION IF NOT EXISTS btree_gist;` appears first.
  - The predicate `WHERE (status <> 'cancelled')` is **negative**: everything *except* cancelled holds the slot. If a new status is added later, it will hold the slot by default (safe failure) unless someone deliberately excludes it. `no_show` therefore keeps the slot until an explicit, audited release (D6).
- `uq_appt_id_tenant`, `uq_appt_id_patient_tenant`: the two unique keys enable composite FKs from `appointment_history` (tenant) and `note_appointment_link` (patient and tenant).
- The three indexes support "a therapist's schedule", "a patient's appointments" and "a therapist's day".

**Design notes**

- **Cross-clinic double booking (D14).** Because the constraint is keyed on `therapist_membership_id`, which belongs to one tenant, a therapist who works at two clinics has two memberships and **can** be booked at overlapping times by the two clinics. This is the documented limitation, not a defect ([documented limitations](../../03-enforcement/documented-limitations.md)).
- **UTC vs local consistency.** The rule that the UTC instants match the local date/time/timezone cannot be a `CHECK`, because converting through a time zone is not an immutable operation (the time zone database can change). It is enforced by a trigger (`enforce_appointment_utc_local_consistency`, [trigger summary](../../03-enforcement/triggers/README.md)).
- **Extension privilege.** The source says `CREATE EXTENSION` needs a database-level privilege "described in the research note", and that `btree_gist` is trusted on PostgreSQL 18. That research note is not part of the material in this conversation. Section 19 repeats that installing the extension is a deployment prerequisite.

## Relationships

**Depends on (this table references):** [Patient](../b-patients-assignments/patient.md), [Tenant](../a-tenancy-identity/tenant.md), [TenantMembership](../a-tenancy-identity/tenant-membership.md)

**Referenced by:** [AppointmentHistory](appointment-history.md), [NoteAppointmentLink](../e-clinical-notes/note-appointment-link.md)

## Triggers on this table

- [enforce_archived_read_only](../../03-enforcement/triggers/enforce_archived_read_only.md): applies to this table through the child-table check for archived patients
- [enforce_appointment_utc_local_consistency](../../03-enforcement/triggers/enforce_appointment_utc_local_consistency.md): fires on BEFORE INSERT, BEFORE UPDATE
- [set_updated_at](../../03-enforcement/triggers/set_updated_at.md): BEFORE UPDATE

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[Group overview](README.md) · [AppointmentHistory →](appointment-history.md)
