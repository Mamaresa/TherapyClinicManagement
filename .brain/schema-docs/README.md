# Clinical Practice Platform: Database Schema Design (modular documentation)

This folder is the schema design split into small linked files: **one file per table**, one per trigger, and one per topic. Nothing was removed or summarized; every definition and note from the two source messages (Actor Response 61 and 62) is kept, and explanations were added around them.

> **Status:** design text only. No Django models, migrations, SQL files or implementation code have been created. Django's ORM cannot express composite foreign keys natively, so any implementation needs explicit SQL migrations.

Target database: PostgreSQL. 25 tables in 9 groups.

## Reading paths

- **New to the design:** [how to read](01-foundations/how-to-read.md) → [conventions](01-foundations/conventions.md) → [ER diagram](01-foundations/er-diagram.md) → [design decisions](01-foundations/design-decisions.md).
- **Looking up one table:** use the table index below. Each table page lists what it depends on, what references it and which triggers apply.
- **Implementing:** [constraint enforcement summary](03-enforcement/README.md) → [triggers](03-enforcement/triggers/README.md) → [application-level rules](03-enforcement/application-level-rules.md).
- **Reviewing:** [review notes on Part 1](05-notes/review-notes-part1.md), [review notes on Part 2](05-notes/review-notes-part2.md), [section crosswalk](05-notes/section-crosswalk.md).

## Folder map

| Folder | Contents |
|---|---|
| `01-foundations/` | How to read, conventions, ER diagram, design decisions, table inventory, Part 2 introduction, group summary, scope and status |
| `02-tables/` | One folder per group (A to I), one file per table, plus a group overview |
| `03-enforcement/` | Declarative constraints, triggers (one file each), application-level rules, documented limitations |
| `04-requirements/` | Requirements-to-schema mapping and coverage confirmation |
| `05-notes/` | Cross-cutting patterns, review notes, section crosswalk, process notes |

## Table index

### [Group A: tenancy, identity, authentication](02-tables/a-tenancy-identity/README.md)

- [Tenant](02-tables/a-tenancy-identity/tenant.md) (`tenant`): one row per clinic or practice. It is the root of data isolation.
- [User](02-tables/a-tenancy-identity/app-user.md) (`app_user`): one row per human account, independent of any clinic. A person who works at two clinics is one user with two memberships.
- [TenantMembership](02-tables/a-tenancy-identity/tenant-membership.md) (`tenant_membership`): connects a user to a tenant and carries the user's roles there. Almost every tenant-owned table points at this table to say "who".
- [MembershipGrant](02-tables/a-tenancy-identity/membership-grant.md) (`membership_grant`): extra, narrowly-scoped permissions that sit on top of a role. Implements the "if granted" and "explicit permission" wording of features.md 6.2 (X-3).
- [Session](02-tables/a-tenancy-identity/session.md) (`session`): one row per login session. Allows server-side revocation.
- [ResetToken](02-tables/a-tenancy-identity/reset-token.md) (`reset_token`): single-use password-reset tokens.
- [Invitation](02-tables/a-tenancy-identity/invitation.md) (`invitation`): a pending offer for someone to join a tenant with a set of roles. Implements X-7.
- [PlatformRole](02-tables/a-tenancy-identity/platform-role.md) (`platform_role`): platform-level staff roles that sit outside any tenant. Implements X-8.

### [Group B: patients, assignments, supervision](02-tables/b-patients-assignments/README.md)

- [Patient](02-tables/b-patients-assignments/patient.md) (`patient`): the person receiving care at one clinic. Clinic-scoped identity (D1).
- [ClinicalAssignment](02-tables/b-patients-assignments/clinical-assignment.md) (`clinical_assignment`): records which therapist (and optional supervisor) is responsible for a patient, in which role, and for what period. Implements D-N5, D-N8 and X-1.
- [ClinicalSupervision](02-tables/b-patients-assignments/clinical-supervision.md) (`clinical_supervision`): gives a supervisor clinical access to **one specific patient** supervised through a specific therapist (D9, X-4 part 1).
- [SupervisoryOperationalScope](02-tables/b-patients-assignments/supervisory-operational-scope.md) (`supervisory_operational_scope`): gives a supervisor **operational** oversight (demographics, appointments) over a supervisee's patients, without clinical access (D9, X-4 part 2).

### [Group C: consent](02-tables/c-consent/README.md)

- [ConsentTextVersion](02-tables/c-consent/consent-text-version.md) (`consent_text_version`): the versioned wording of a consent form. A consent record points at the exact text the patient agreed to. Texts can be provided by the platform for every clinic, or written by a single clinic (decision D8).
- [ConsentRecord](02-tables/c-consent/consent-record.md) (`consent_record`): the history of a patient's consents and withdrawals. Each row is either a **grant** or a **withdrawal** of an earlier grant. Implements requirements C-1 and C-3.

### [Group D: appointments](02-tables/d-appointments/README.md)

- [Appointment](02-tables/d-appointments/appointment.md) (`appointment`): a scheduled session between one patient and one therapist. Implements D6 and A-1.
- [AppointmentHistory](02-tables/d-appointments/appointment-history.md) (`appointment_history`): an append-only log of changes to appointments (who changed what, and why). Implements A-6.

### [Group E: clinical notes](02-tables/e-clinical-notes/README.md)

- [ClinicalNoteDraft](02-tables/e-clinical-notes/clinical-note-draft.md) (`clinical_note_draft`): an editable work-in-progress clinical note. When finalized, a separate immutable `clinical_note` row is created from it.
- [ClinicalNote](02-tables/e-clinical-notes/clinical-note.md) (`clinical_note`): the finalized, immutable clinical note, and also the addendum record used to correct a finalized note. Implements D7, N-2 and N-7.
- [NoteAppointmentLink](02-tables/e-clinical-notes/note-appointment-link.md) (`note_appointment_link`): links a finalized note to the appointment(s) it documents, without modifying either row. Implements N-1 and the D-N1 resolution documented in [design decisions (technical resolution)](01-foundations/design-decisions.md).

### [Group F: treatment](02-tables/f-treatment/README.md)

- [TreatmentPlan](02-tables/f-treatment/treatment-plan.md) (`treatment_plan`): a patient's treatment plan, with a status and a time span.
- [TreatmentGoal](02-tables/f-treatment/treatment-goal.md) (`treatment_goal`): a goal inside a treatment plan.
- [ProgressEntry](02-tables/f-treatment/progress-entry.md) (`progress_entry`): a dated progress record for a patient, optionally tied to a goal.

### [Group G: assessments](02-tables/g-assessments/README.md)

- [AssessmentResult](02-tables/g-assessments/assessment-result.md) (`assessment_result`): a recorded result of a clinical assessment (questionnaire, scale or test), optionally with an attached file.

### [Group H: files](02-tables/h-files/README.md)

- [PatientFile](02-tables/h-files/patient-file.md) (`patient_file`): metadata about a file stored outside the database (the blob lives in object storage). Implements F-1 and D16.

### [Group I: audit](02-tables/i-audit/README.md)

- [AuditEvent](02-tables/i-audit/audit-event.md) (`audit_event`): the append-only record of who did what, to which resource, with what outcome. Implements U-1.

### Triggers

- [enforce_clinical_note_immutable](03-enforcement/triggers/enforce_clinical_note_immutable.md)
- [enforce_appointment_history_append_only](03-enforcement/triggers/enforce_appointment_history_append_only.md)
- [enforce_audit_event_append_only](03-enforcement/triggers/enforce_audit_event_append_only.md)
- [enforce_consent_record_append_only](03-enforcement/triggers/enforce_consent_record_append_only.md)
- [enforce_note_link_append_only](03-enforcement/triggers/enforce_note_link_append_only.md)
- [enforce_assignment_ended_once](03-enforcement/triggers/enforce_assignment_ended_once.md)
- [enforce_archived_read_only](03-enforcement/triggers/enforce_archived_read_only.md)
- [enforce_consent_withdrawal_target_is_grant](03-enforcement/triggers/enforce_consent_withdrawal_target_is_grant.md)
- [enforce_consent_version_tenant_match](03-enforcement/triggers/enforce_consent_version_tenant_match.md)
- [enforce_audit_membership_tenant_match](03-enforcement/triggers/enforce_audit_membership_tenant_match.md)
- [enforce_appointment_utc_local_consistency](03-enforcement/triggers/enforce_appointment_utc_local_consistency.md)
- [set_updated_at](03-enforcement/triggers/set_updated_at.md)

### Other pages

- [how to read this document](01-foundations/how-to-read.md)
- [conventions](01-foundations/conventions.md)
- [ER diagram](01-foundations/er-diagram.md)
- [design decisions](01-foundations/design-decisions.md)
- [table inventory](01-foundations/table-inventory.md)
- [Part 2 introduction](01-foundations/part2-introduction.md)
- [group summary](01-foundations/group-summary.md)
- [scope and status](01-foundations/scope-and-status.md)
- [constraint enforcement summary](03-enforcement/README.md)
- [declarative constraints](03-enforcement/declarative-constraints.md)
- [application-level rules](03-enforcement/application-level-rules.md)
- [documented limitations](03-enforcement/documented-limitations.md)
- [requirements-to-schema mapping](04-requirements/requirements-mapping.md)
- [coverage confirmation](04-requirements/coverage-confirmation.md)
- [cross-cutting patterns](05-notes/cross-cutting-patterns.md)
- [review notes on Part 1](05-notes/review-notes-part1.md)
- [review notes on Part 2](05-notes/review-notes-part2.md)
- [section crosswalk](05-notes/section-crosswalk.md)
- [process notes](05-notes/process-notes.md)
