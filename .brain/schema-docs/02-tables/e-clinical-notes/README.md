[← Back to index](../../README.md)

# Group E: clinical notes

| Table | SQL name | Purpose |
|---|---|---|
| [ClinicalNoteDraft](clinical-note-draft.md) | `clinical_note_draft` | an editable work-in-progress clinical note. When finalized, a separate immutable `clinical_note` row is created from it. |
| [ClinicalNote](clinical-note.md) | `clinical_note` | the finalized, immutable clinical note, and also the addendum record used to correct a finalized note. Implements D7, N-2 and N-7. |
| [NoteAppointmentLink](note-appointment-link.md) | `note_appointment_link` | links a finalized note to the appointment(s) it documents, without modifying either row. Implements N-1 and the D-N1 resolution documented in [design decisions (technical resolution)](../../01-foundations/design-decisions.md). |
