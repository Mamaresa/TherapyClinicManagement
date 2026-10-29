[← Back to index](../README.md)

# Section-number crosswalk

The source documents refer to their own section numbers, and those numbers do not always match where the content actually is, because Part 1 and Part 2 were numbered separately and some references appear to be stale. This table maps each reference to the right place in this documentation set.

| Reference in the source | Where it appears | What it points to | Location in this documentation set |
|---|---|---|---|
| "Section 11 in Part 2" | Part 1, User table notes | Persian/Arabic email normalization requirement | [application-level rules](../03-enforcement/application-level-rules.md), row "Persian normalization of email and names"  |
| "Section 12 in Part 2" | Part 1, ClinicalAssignment notes | Trigger for setting `ended_at` once | [trigger summary](../03-enforcement/triggers/README.md), trigger `enforce_assignment_ended_once`  |
| "the CHECK in Section 4" | Part 1, ER cardinality notes (AuditEvent) | `ck_ae_tenant_for_clinical_resources` | [AuditEvent](../02-tables/i-audit/audit-event.md) (and 16.1)  |
| "Section 15" | ConsentTextVersion notes | `enforce_consent_version_tenant_match` | [trigger summary](../03-enforcement/triggers/README.md)  |
| "Section 15" (twice) | ConsentRecord notes | `enforce_consent_withdrawal_target_is_grant`, and the exception list of `enforce_archived_read_only` | [trigger summary](../03-enforcement/triggers/README.md)  |
| "Section 15" | Appointment notes | `enforce_appointment_utc_local_consistency` | [trigger summary](../03-enforcement/triggers/README.md)  |
| "Section 15" | AppointmentHistory notes | `enforce_appointment_history_append_only` | [trigger summary](../03-enforcement/triggers/README.md)  |
| "Section 16" | ClinicalNoteDraft notes | Draft locking on reassignment (application-enforced) | [application-level rules](../03-enforcement/application-level-rules.md), row "Draft locking on reassignment"  |
| "Sections 14 and 15" | ClinicalNote notes | Immutability by trigger and by revoked privileges | [trigger summary](../03-enforcement/triggers/README.md), trigger `enforce_clinical_note_immutable`  |
| "Section 15" | AuditEvent notes | `enforce_audit_membership_tenant_match` | [trigger summary](../03-enforcement/triggers/README.md)  |
| "Section 14.2" and "Section 14.3" | Mapping table, rows 6.3, and section 17 text | Trigger list and application-level list | [trigger summary](../03-enforcement/triggers/README.md) and [application-level rules](../03-enforcement/application-level-rules.md)  |
| "Part 1, Section 1" | Coverage confirmation | The ER diagram | [ER diagram](../01-foundations/er-diagram.md)  |
| "documented in Part 1" | NoteAppointmentLink notes | The D-N1 resolution | [design decisions (technical resolution)](../01-foundations/design-decisions.md)  |

See also [review notes on Part 2](review-notes-part2.md).
