[← Back to index](../../README.md)

# Enforced by trigger

Triggers are needed where the rule crosses rows or tables and cannot be expressed as a CHECK or FK.

| Trigger | Table | Fires on | Rule |
|---|---|---|---|
| [enforce_clinical_note_immutable](enforce_clinical_note_immutable.md) | ClinicalNote | BEFORE UPDATE, BEFORE DELETE | Reject any UPDATE or DELETE once the row exists. The finalization check is implicit: rows are only inserted via the finalize path. |
| [enforce_appointment_history_append_only](enforce_appointment_history_append_only.md) | AppointmentHistory | BEFORE UPDATE, BEFORE DELETE | Reject UPDATE and DELETE. |
| [enforce_audit_event_append_only](enforce_audit_event_append_only.md) | AuditEvent | BEFORE UPDATE, BEFORE DELETE | Reject UPDATE and DELETE. |
| [enforce_consent_record_append_only](enforce_consent_record_append_only.md) | ConsentRecord | BEFORE UPDATE, BEFORE DELETE | Reject UPDATE and DELETE. Current state is derived from the chain. |
| [enforce_note_link_append_only](enforce_note_link_append_only.md) | NoteAppointmentLink | BEFORE UPDATE, BEFORE DELETE | Allow only setting removed_at and removed_by_membership_id once, from NULL to a value. Reject DELETE. |
| [enforce_assignment_ended_once](enforce_assignment_ended_once.md) | ClinicalAssignment | BEFORE UPDATE | Allow only a single transition: ended_at from NULL to a non-null value. Reject any other UPDATE. |
| [enforce_archived_read_only](enforce_archived_read_only.md) | Patient (with cascading check on child tables) | BEFORE INSERT, BEFORE UPDATE | When Patient.status = 'archived', reject INSERT on ClinicalNoteDraft, ClinicalNote, ProgressEntry, AssessmentResult, Appointment (except status transitions to cancelled), TreatmentPlan, TreatmentGoal. Exceptions: ConsentRecord inserts (consent withdrawal is allowed on archived patients), AuditEvent inserts (audit always allowed), ClinicalAssignment UPDATE to set ended_at, PatientFile lifecycle transitions to deleted or purge_pending. The trigger takes a row-level lock on the Patient row to prevent a race between archiving and a concurrent note insert. |
| [enforce_consent_withdrawal_target_is_grant](enforce_consent_withdrawal_target_is_grant.md) | ConsentRecord | BEFORE INSERT | When status = 'withdrawal', verify that withdraws_consent_id refers to a row whose status = 'grant' in the same patient and tenant. |
| [enforce_consent_version_tenant_match](enforce_consent_version_tenant_match.md) | ConsentRecord | BEFORE INSERT | Verify that the referenced consent_text_version has tenant_id NULL or equal to the record's tenant_id. |
| [enforce_audit_membership_tenant_match](enforce_audit_membership_tenant_match.md) | AuditEvent | BEFORE INSERT | When actor_membership_id IS NOT NULL and tenant_id IS NOT NULL, verify the membership belongs to the tenant. |
| [enforce_appointment_utc_local_consistency](enforce_appointment_utc_local_consistency.md) | Appointment | BEFORE INSERT, BEFORE UPDATE | Verify that starts_at_utc equals the local_start_date + local_start_time interpreted in local_timezone, and ends_at_utc equals starts_at_utc + the intended duration. Uses the tz database; not a CHECK because zone conversion is not immutable. |
| [set_updated_at](set_updated_at.md) | Tables with updated_at | BEFORE UPDATE | Set NEW.updated_at = now(). |

Trigger declarations must be ENABLE ALWAYS, and the trigger functions must be owned by a role the runtime role does not belong to (D12). Migration tests must confirm each trigger survives fresh setup, upgrades, and restoration.

**How to read the trigger table**

- **Immutability triggers** (`clinical_note`, `appointment_history`, `audit_event`, `consent_record`) all follow one idea: the row can be inserted but never changed or removed. `note_appointment_link` is the controlled exception, and `clinical_assignment` allows exactly one change (ending it).
- **Cross-row validation triggers** (`consent_withdrawal_target_is_grant`, `consent_version_tenant_match`, `audit_membership_tenant_match`) check conditions that need a lookup in another row, which a CHECK cannot do and which no composite FK can express.
- **`enforce_archived_read_only`** blocks new clinical activity for archived patients, with deliberate exceptions so that consent can still be withdrawn, audit events can still be written, assignments can still be ended and files can still be soft-deleted or queued for purge. It takes a row-level lock on the patient to prevent a race between archiving and a concurrent note insert.
- **`ENABLE ALWAYS`** matters because PostgreSQL can be told to skip ordinary triggers (for example during replication or a bulk restore). Declaring them `ENABLE ALWAYS` keeps them active in those cases.
- **Trigger-function ownership** (D12): the functions are owned by a role that the runtime application role does not belong to. Otherwise the application's own database role could drop or replace the triggers.
- **`set_updated_at`** appears in the trigger table although Part 1's conventions say `updated_at` is "refreshed by application logic; no trigger is assumed". See [review notes on Part 2](../../05-notes/review-notes-part2.md).

Each trigger has its own page in this folder.

---

[← Enforcement summary](../README.md)
