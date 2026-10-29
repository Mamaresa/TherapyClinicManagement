[← Back to index](../README.md)

# Enforced declaratively by PostgreSQL (DDL)

These rules hold no matter what code talks to the database.

| Constraint class | Mechanism | Where |
|---|---|---|
| Primary keys | PRIMARY KEY on id | Every table |
| Composite tenant isolation | FOREIGN KEY (child_id, tenant_id) REFERENCES parent(id, tenant_id) | All tenant-owned children |
| Composite patient scope | FOREIGN KEY (child_id, patient_id, tenant_id) REFERENCES parent(id, patient_id, tenant_id) | All patient-scoped children (ClinicalAssignment, ConsentRecord, ClinicalNoteDraft, ClinicalNote, NoteAppointmentLink, TreatmentPlan, TreatmentGoal, ProgressEntry, AssessmentResult, PatientFile) |
| Composite self-references | FOREIGN KEY on (parent_id, patient_id, tenant_id) | ConsentRecord.withdraws_consent_id, ClinicalNote.addendum_to_note_id |
| Column-level not-null | NOT NULL | As marked per column |
| Single-row value constraints | CHECK (enum sets, date ordering, paired field consistency, hash length, JSONB type, reason presence) | As marked per table |
| Uniqueness | UNIQUE constraint or UNIQUE INDEX | Email normalization, tenant slug, consent version label per scope, one active primary assignment per patient, one active membership per (tenant, user), one finalized note per draft, one active note-appointment link, one withdrawal per grant |
| Partial uniqueness | Partial UNIQUE INDEX WHERE ... | As above |
| Scheduling overlap | EXCLUDE USING gist (... tstzrange ... WITH &&) WHERE status <> 'cancelled' | Appointment |
| Foreign-key restriction | ON DELETE RESTRICT, ON UPDATE RESTRICT | All foreign keys |

---

[← Enforcement summary](README.md)
