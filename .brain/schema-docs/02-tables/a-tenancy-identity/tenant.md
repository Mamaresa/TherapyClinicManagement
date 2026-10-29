[← Back to index](../../README.md)

# Tenant

> `tenant` · Group A: tenancy, identity, authentication

**Purpose:** one row per clinic or practice. It is the root of data isolation.

```sql
CREATE TABLE tenant (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name         TEXT NOT NULL,
    slug         TEXT NOT NULL,
    timezone     TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'active'
                 CHECK (status IN ('active','suspended','closed')),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    archived_at  TIMESTAMPTZ,
    CONSTRAINT uq_tenant_slug UNIQUE (slug),
    CONSTRAINT ck_tenant_archived CHECK (
        (status = 'closed' AND archived_at IS NOT NULL)
        OR status <> 'closed'
    )
);
```

**Column guide**

| Column | Meaning |
|---|---|
| `name` | Display name of the clinic. |
| `slug` | URL-safe identifier, unique across the whole platform. |
| `timezone` | IANA timezone identifier (for example `Asia/Tehran`). Used to interpret local appointment times. |
| `status` | `active`, `suspended` or `closed`. |
| `archived_at` | When the tenant was closed. |

**Constraints explained**

- `uq_tenant_slug`: two clinics cannot share a URL slug.
- `ck_tenant_archived`: a `closed` tenant must have `archived_at` set. Other statuses are unconstrained. The check is one-directional: it does not forbid `archived_at` on an active tenant.

**Design notes:** tenants are never deleted. Closing a tenant is a status change plus a timestamp.

## Relationships

**Depends on (this table references):** none

**Referenced by:** [Appointment](../d-appointments/appointment.md), [AppointmentHistory](../d-appointments/appointment-history.md), [AssessmentResult](../g-assessments/assessment-result.md), [AuditEvent](../i-audit/audit-event.md), [ClinicalNote](../e-clinical-notes/clinical-note.md), [ClinicalNoteDraft](../e-clinical-notes/clinical-note-draft.md), [ConsentRecord](../c-consent/consent-record.md), [ConsentTextVersion](../c-consent/consent-text-version.md), [Invitation](invitation.md), [NoteAppointmentLink](../e-clinical-notes/note-appointment-link.md), [Patient](../b-patients-assignments/patient.md), [PatientFile](../h-files/patient-file.md), [ProgressEntry](../f-treatment/progress-entry.md), [Session](session.md), [TenantMembership](tenant-membership.md), [TreatmentGoal](../f-treatment/treatment-goal.md), [TreatmentPlan](../f-treatment/treatment-plan.md)

## Triggers on this table

- [set_updated_at](../../03-enforcement/triggers/set_updated_at.md): BEFORE UPDATE

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[Group overview](README.md) · [User →](app-user.md)
