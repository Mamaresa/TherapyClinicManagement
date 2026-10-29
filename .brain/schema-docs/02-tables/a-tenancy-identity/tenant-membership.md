[← Back to index](../../README.md)

# TenantMembership

> `tenant_membership` · Group A: tenancy, identity, authentication

**Purpose:** connects a user to a tenant and carries the user's roles there. Almost every tenant-owned table points at this table to say "who".

```sql
CREATE TABLE tenant_membership (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   UUID NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
    user_id     UUID NOT NULL REFERENCES app_user(id) ON DELETE RESTRICT,
    roles       TEXT[] NOT NULL
                CHECK (roles <@ ARRAY['owner_admin','clinical_supervisor','therapist','assistant']::TEXT[])
                CHECK (array_length(roles, 1) >= 1),
    joined_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at    TIMESTAMPTZ,
    CONSTRAINT uq_tm_id_tenant    UNIQUE (id, tenant_id),
    CONSTRAINT ck_tm_dates        CHECK (ended_at IS NULL OR ended_at >= joined_at)
);
CREATE UNIQUE INDEX uq_tm_active_user
    ON tenant_membership (tenant_id, user_id)
    WHERE ended_at IS NULL;
CREATE INDEX ix_tm_user_active
    ON tenant_membership (user_id)
    WHERE ended_at IS NULL;
```

**Column guide**

| Column | Meaning |
|---|---|
| `roles` | Array of role codes: `owner_admin`, `clinical_supervisor`, `therapist`, `assistant`. |
| `joined_at` / `ended_at` | Membership period. `ended_at IS NULL` means currently active. |

**Constraints and indexes explained**

- `roles <@ ARRAY[...]`: the `<@` operator means "is contained by". Every element of `roles` must be one of the four known codes.
- `array_length(roles, 1) >= 1`: at least one role is required. An empty array would produce `NULL` from `array_length`, and a CHECK that evaluates to `NULL` passes, so the empty-array case needs care in implementation (see [review notes on Part 1](../../05-notes/review-notes-part1.md)).
- `ck_tm_dates`: the end cannot precede the start.
- `uq_tm_active_user` (partial unique): a user can have only **one active** membership per tenant. Past, ended memberships are unrestricted, so a person can leave and later rejoin.
- `ix_tm_user_active` (partial index): speeds up "which tenants is this user currently in?".
- `uq_tm_id_tenant`: the key that child tables use for composite FKs.

**Design notes**

- `roles` is an array so a solo practitioner can be `owner_admin` and `therapist` at once (resolves requirement X-2).
- Ending a membership is how a person's access is revoked. The row is never deleted because notes, appointments and audit events reference it.

## Relationships

**Depends on (this table references):** [User](app-user.md), [Tenant](tenant.md)

**Referenced by:** [Appointment](../d-appointments/appointment.md), [AppointmentHistory](../d-appointments/appointment-history.md), [AssessmentResult](../g-assessments/assessment-result.md), [AuditEvent](../i-audit/audit-event.md), [ClinicalAssignment](../b-patients-assignments/clinical-assignment.md), [ClinicalNote](../e-clinical-notes/clinical-note.md), [ClinicalNoteDraft](../e-clinical-notes/clinical-note-draft.md), [ClinicalSupervision](../b-patients-assignments/clinical-supervision.md), [ConsentRecord](../c-consent/consent-record.md), [Invitation](invitation.md), [MembershipGrant](membership-grant.md), [NoteAppointmentLink](../e-clinical-notes/note-appointment-link.md), [PatientFile](../h-files/patient-file.md), [ProgressEntry](../f-treatment/progress-entry.md), [SupervisoryOperationalScope](../b-patients-assignments/supervisory-operational-scope.md), [TreatmentPlan](../f-treatment/treatment-plan.md)

## Triggers on this table

None.

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[← User](app-user.md) · [Group overview](README.md) · [MembershipGrant →](membership-grant.md)
