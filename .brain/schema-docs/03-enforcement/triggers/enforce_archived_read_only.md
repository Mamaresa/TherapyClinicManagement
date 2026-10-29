[← Trigger summary](README.md) · [← Back to index](../../README.md)

# enforce_archived_read_only

| | |
|---|---|
| Table | Patient (with cascading check on child tables) |
| Fires on | BEFORE INSERT, BEFORE UPDATE |
| Rule | When Patient.status = 'archived', reject INSERT on ClinicalNoteDraft, ClinicalNote, ProgressEntry, AssessmentResult, Appointment (except status transitions to cancelled), TreatmentPlan, TreatmentGoal. Exceptions: ConsentRecord inserts (consent withdrawal is allowed on archived patients), AuditEvent inserts (audit always allowed), ClinicalAssignment UPDATE to set ended_at, PatientFile lifecycle transitions to deleted or purge_pending. The trigger takes a row-level lock on the Patient row to prevent a race between archiving and a concurrent note insert. |

## Explanation

An archived patient's record must not receive new clinical content. The rule is listed on Patient, but inserts into child tables can only be intercepted by triggers on those child tables, which is why the table pages of the child tables also list it. Deliberate exceptions keep consent withdrawal, audit writing, ending assignments and file soft-delete/purge-queueing possible. The row-level lock on the patient prevents a race between archiving and a concurrent insert.

## Applies to

[Patient](../../02-tables/b-patients-assignments/patient.md) and, through the child-table check, [ClinicalNoteDraft](../../02-tables/e-clinical-notes/clinical-note-draft.md), [ClinicalNote](../../02-tables/e-clinical-notes/clinical-note.md), [ProgressEntry](../../02-tables/f-treatment/progress-entry.md), [AssessmentResult](../../02-tables/g-assessments/assessment-result.md), [Appointment](../../02-tables/d-appointments/appointment.md), [TreatmentPlan](../../02-tables/f-treatment/treatment-plan.md), [TreatmentGoal](../../02-tables/f-treatment/treatment-goal.md), [ConsentRecord](../../02-tables/c-consent/consent-record.md), [AuditEvent](../../02-tables/i-audit/audit-event.md), [ClinicalAssignment](../../02-tables/b-patients-assignments/clinical-assignment.md), [PatientFile](../../02-tables/h-files/patient-file.md)

## Requirements for all triggers

Trigger declarations must be ENABLE ALWAYS, and the trigger functions must be owned by a role the runtime role does not belong to (D12). Migration tests must confirm each trigger survives fresh setup, upgrades, and restoration. See the [trigger summary](README.md).
