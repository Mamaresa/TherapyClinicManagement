[← Back to index](../README.md)

# Requirements-to-schema mapping

Each features.md section mapped to the tables and constraints that implement it.

| features.md | Requirement | Tables and constraints |
|---|---|---|
| 5 Domain model | Tenant, User, Role, Patient, Consent, Appointment, Clinical note, Addendum, Treatment plan, Goal, Assessment, Progress, File, Audit | All 25 tables; addendum modeled as ClinicalNote self-reference (D7) |
| 6.1 Roles | Owner/Admin, Clinical Supervisor, Therapist, Assistant | TenantMembership.roles TEXT[] CHECK; combined roles permitted (X-2) |
| 6.2 Permission matrix; "if granted"; "explicit permission" | Receptionist operational access and admin security-metadata review gated by grant | MembershipGrant with grant_code enum; partial unique on active grants (X-3) |
| 6.2 Supervisors operational scope over supervisees' patients | SupervisoryOperationalScope | SupervisoryOperationalScope table; grants no clinical access (X-4) |
| 6.3 Assignment-based clinical access | ClinicalAssignment first-class history; supervisor access only per patient | ClinicalAssignment with partial unique on active primary; ClinicalSupervision with non-null patient_id |
| 6.3 Authored-records view | Author access to own notes only | Application-level (Section 14.3); schema preserves author_membership_id and patient link, so the view is a query |
| 6.3 Archived patient | Read-only | enforce_archived_read_only trigger with the exception list in Section 14.2 |
| 6.3 Immediate revocation on deactivation | Session revocation, access predicate | Session.revoked_at; access predicate at application level |
| 7 Tenant isolation | tenant_id on every tenant-owned table; composite FKs; cross-tenant tests | All Group A through I tables; tests at application level for negative cases |
| 8 Auth, recovery, revocation | Login, hashing, rate limit, session store, reset tokens, invite flow that does not leak account existence | User, Session, ResetToken, Invitation; application-level rate limit and hash |
| 9.1 Patient management | Create, view, update, archive; demographics; intake; files; search; archive | Patient, PatientFile; normalized name columns for search; ck_patient_archived |
| 9.2 Consent | Purpose, scope, status, timestamp, version, method, evidence; history preserved | ConsentTextVersion, ConsentRecord append-oriented; ck_cr_withdrawal_pair; evidence_file_id composite FK |
| 9.3 Appointments | Create, edit, cancel; statuses; conflict detection | Appointment with EXCLUDE constraint; AppointmentHistory for changes; ck_appt_cancel_reason |
| 9.4 Clinical documentation | Draft, finalize, immutable, corrections via addenda; author, timestamp, reason | ClinicalNoteDraft, ClinicalNote with content_hash, addendum_to_note_id, addendum_reason; enforce_clinical_note_immutable trigger |
| 9.5 Treatment plans and progress | Plan, goals, progress entries, linking goals to sessions | TreatmentPlan, TreatmentGoal, ProgressEntry, NoteAppointmentLink (link goals to sessions via ProgressEntry to TreatmentGoal and ClinicalNote to Appointment) |
| 9.6 Assessments | Manual entry, file attachment, patient association, history | AssessmentResult with file_id composite FK to PatientFile |
| 9.7 Session history | Chronological sessions per patient, linked notes, assessments, progress; filter by date and therapist | No dedicated table; query over Appointment + ClinicalNote + AssessmentResult + ProgressEntry joined on patient, ordered by time, filtered by therapist membership and date range |
| 9.8 Files | Private, no public URLs, authorization per download, type and size validation, tenant-scoped, audit | PatientFile with lifecycle_state; enforce via application-level download path; AuditEvent record on every access |
| 9.9 Reporting | Operational summaries, per-therapist and per-tenant, CSV export | No dedicated table; queries over Appointment, Patient, TenantMembership. Exports are audited operations (AuditEvent action = 'export'); no persisted artifact table in MVP (documented limitation) |
| 9.10 Audit and security logging | Log classes of events; no note content in metadata; retention | AuditEvent with action enum and metadata JSONB; CHECK forbids tenant-less events on tenant-owned resources; append-only |
| 9.11 Audit-log integrity | Restricted write/delete; attributed to user or process; timestamps and correlation | AuditEvent append-only trigger; actor_type + actor_user_id + actor_membership_id; correlation_id |
| 10 Security baseline | TLS, AES-256 at rest | Deployment and key management out of scope; contact and emergency fields stored BYTEA (application-encrypted) |
| 11 Backups and recovery | Restore test preserving tenant boundaries, permissions, history, audit | Schema is compatible with pg_dump / pg_restore; triggers are ENABLE ALWAYS and must be verified after restore (research note 2.5) |
| 13 Decided items | Clinical notes immutable, corrections via addenda, role separation, tenant-aware access, RLS deferred | Reflected in ClinicalNote, MembershipGrant, all tenant tables, no RLS |
| 13 Provisional and deferred | Backend framework (now confirmed), deployment topology, backup objectives, audit retention, break-glass mechanism | Framework confirmed as Django/DRF/PostgreSQL; others deferred |

> **Section references inside this table.** "Section 14.3" in the 6.3 Authored-records row is [application-level rules](../03-enforcement/application-level-rules.md), and "Section 14.2" in the 6.3 Archived patient row is [trigger summary](../03-enforcement/triggers/README.md). See the crosswalk in [section crosswalk](../05-notes/section-crosswalk.md).

**How to read the mapping**

- The first column is the section of the original `features.md` requirements document.
- The third column names what implements it. Where it says "No dedicated table", the requirement is met by queries over existing tables, not by storage of its own (session history and reporting).
- Codes such as X-1 to X-4, A-1, A-6, C-1, C-3, N-1 to N-7, F-1 and U-1 to U-3 are requirement identifiers from the earlier conceptual design; their text is not reproduced in the material provided in this conversation.
