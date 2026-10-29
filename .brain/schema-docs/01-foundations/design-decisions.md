[← Back to index](../README.md)

# Design decisions carried from the conceptual design

The decisions below come from Actor Response 60 and drive the schema. They are repeated here so this document stands on its own.

| ID | Decision | Effect on the schema |
|---|---|---|
| D1 | Patient identity is clinic-scoped. | `patient` is tenant-owned. The same real person at two clinics is two patient rows. |
| D2 | An incoming therapist sees all finalized notes for the patient. | Access rule (application/predicate layer), based on active `clinical_assignment`. |
| D3 | An outgoing therapist sees authored notes only through the authored-records view, revoked when membership ends. | Access rule tied to `tenant_membership.ended_at`. |
| D4 | The authored-records view is available to any therapist for their own notes, with no co-authorization. | Access rule. |
| D5 | The authored-records view shows minimum identifying information. | View/query design. |
| D6 | A no-show occupies the slot until an explicit, audited release. The exclusion predicate is `status <> 'cancelled'`. | Appointment overlap constraint ([Appointment](../02-tables/d-appointments/appointment.md)). |
| D7 | Addenda use `addendum_to_note_id` with a required reason. No supersession in the MVP. | ClinicalNote self-FK ([ClinicalNote](../02-tables/e-clinical-notes/clinical-note.md)). |
| D8 | Consent text versions are tenant-optional. `NULL` tenant_id means platform-provided. | ConsentTextVersion ([ConsentTextVersion](../02-tables/c-consent/consent-text-version.md)). |
| D9 | ClinicalSupervision is patient-specific. SupervisoryOperationalScope is operational only. | Tables 7.3 and 7.4 below. |
| D10 | Break-glass access is deferred. | No break-glass tables. |
| D11 | Audit failure policy: fail closed. Audited reads also deny when the audit write fails. | Application behaviour. |
| D12 | Privileged-actor risk is accepted. Runtime-role restrictions apply. | Database role design. |
| D13 | Erasure of finalized note text is not supported in the MVP. | No erase path for notes. |
| D14 | Cross-clinic double-booking is allowed, with a documented limitation. | Overlap constraints are tenant-scoped. |
| D15 | Audit retention is provisionally 7 years. Hosting is undecided. | Audit retention policy. |
| D16 | File deletion is soft delete with lifecycle states. A purge process is deferred. | PatientFile ([PatientFile](../02-tables/h-files/patient-file.md)). |

## One technical resolution not in the conceptual design

`ClinicalNote.appointment_id` was **dropped** in favour of `NoteAppointmentLink` as the only note-to-appointment relationship.

**Why:** a finalized note is immutable. A column on the note could not be updated after finalization, so a late-discovered link to an appointment would be impossible. A separate link table can be added to later (with append-only history) without touching the immutable note. This is consistent with the intent of decision D-N1.
