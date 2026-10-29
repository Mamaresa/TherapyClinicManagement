[← Back to index](../README.md)

# Observations on the text of Part 2

These are observations on the source text itself. They are for the operator's consideration and do not change the design above.

1. **Creation order.** `consent_record` ([ConsentRecord](../02-tables/c-consent/consent-record.md)) and `assessment_result` ([AssessmentResult](../02-tables/g-assessments/assessment-result.md)) have foreign keys to `patient_file` ([PatientFile](../02-tables/h-files/patient-file.md)), but the source defines `patient_file` later. Real DDL must create `patient_file` first, or add those two constraints afterwards with `ALTER TABLE`. Likewise `CREATE EXTENSION btree_gist` must run before `appointment` is created.
2. **Consent text can be edited after use.** No trigger in [trigger summary](../03-enforcement/triggers/README.md) protects `consent_text_version.body` once a `consent_record` points at it. The records stay append-only, but the wording they point at could change.
3. **`updated_at` conventions disagree.** Part 1's conventions say `updated_at` is "refreshed by application logic; no trigger is assumed". Section 16.2 lists a `set_updated_at` trigger on every table with `updated_at`. One of the two should be chosen.
4. **Where `enforce_archived_read_only` is attached.** The trigger is listed on `Patient`, "with cascading check on child tables", but a trigger on `patient` fires only when a `patient` row changes. Blocking an `INSERT` into `clinical_note` for an archived patient needs a trigger on `clinical_note` itself (and on each other child table in the list), which looks up the patient's status and takes the row lock.
5. **Drafts stay editable after finalization.** `uq_cn_source_draft` guarantees one note per draft, and `clinical_note` is immutable, but no trigger or constraint stops the *draft* row from being updated after its note exists. The source describes locking on reassignment as application logic, not locking on finalization.
6. **The audit tenant check is a list of known types.** `ck_ae_tenant_for_clinical_resources` requires a tenant only for the resource types it names. An event with a new, misspelled or unlisted `resource_type` may be stored with `tenant_id` set to `NULL`. This is the opposite of the "fails safe" reasoning the source gives for the appointment predicate.
7. **`action` is not an enum.** The mapping table ([requirements-to-schema mapping](../04-requirements/requirements-mapping.md), row 9.10) describes `AuditEvent` with an "action enum", but `audit_event.action` is plain `TEXT` with no `CHECK`.
8. **"Intended duration" has no column.** The trigger `enforce_appointment_utc_local_consistency` checks that `ends_at_utc` equals `starts_at_utc` plus "the intended duration", but `appointment` has no duration column, so the source does not say where that duration comes from.
9. **Goals and sessions are not linked directly.** The mapping for features.md 9.5 says goals are linked to sessions "via ProgressEntry to TreatmentGoal and ClinicalNote to Appointment". But `progress_entry` has no reference to a note or appointment, so no table connects a goal to a session. The only shared keys are the patient and the time.
10. **Several things are mutable by omission.** `assessment_result` and `treatment_plan` have no immutability trigger, and `treatment_plan` has no "one active plan" index. These may be intended; the source does not say.
11. **Referenced material is not present.** The source refers to a "research note" (and "research note 2.5") and to requirement codes (X-1 to X-8, A-1, A-4, A-6, C-1, C-3, N-1 to N-7, F-1, U-1 to U-3, D-N1, D-N5, D-N8). Neither the research note nor the text of these codes appears in the material provided in this conversation.
12. **`uq_ctv_id_tenant` is inert.** It cannot constrain global rows and nothing references it.

See also the [section crosswalk](section-crosswalk.md).
