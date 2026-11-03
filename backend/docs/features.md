# features.md

CRM for Mental Health Professionals — MVP Feature Specification

## 1. Purpose

A web-based CRM for mental health professionals (psychologists, psychotherapists, counselors) to manage patients, appointments, clinical documentation, session histories, assessments, and related files.

Two product profiles share one codebase and one data model:

- Solo / Small Clinic (1–5 therapists)
- Larger Clinic / Organization (multiple therapists, supervisors, administrators)

Differences between profiles are limited to roles, permissions, and UI presentation. They are not separate deployments.

## 2. Target Users and Scope

In scope for MVP:
- Psychologists
- Psychotherapists
- Counselors

Out of scope for MVP:
- Psychiatry (medication management)
- Physiotherapy, occupational therapy, speech therapy
- Patient self-service portal
- Telehealth
- Billing and payments
- External calendar, e-signature, or payment integrations

## 3. Technology Baseline

- Frontend: React + TypeScript + Tailwind CSS
- Backend: Python (FastAPI or Django — final choice deferred)
- Database: PostgreSQL
- Language and layout: Farsi (Persian), right-to-left (RTL)
- Calendar: Jalali for scheduling and display; Gregorian internally where needed

## 4. Language, Localization, and Accessibility

- All UI strings in Farsi.
- RTL layout across the application.
- Jalali calendar for appointments, dates of birth, and clinical dates.
- Persian number formatting where appropriate.
- Accessibility: keyboard navigation, screen-reader-friendly labels, sufficient contrast.
- Additional languages deferred.

## 5. Core Domain Model (High Level)

- Tenant (clinic or organization)
- User (therapist, supervisor, admin, assistant/receptionist)
- Role and Permission
- Patient
- Consent record
- Appointment
- Clinical note (draft and finalized)
- Note addendum
- Treatment plan
- Treatment goal
- Assessment result
- Session history / progress entry
- Uploaded file / document
- Audit event

Every tenant-owned table carries tenant_id. Cross-tenant relationships are prevented by composite foreign keys where practical.

## 6. Roles, Permissions, and Authorization

### 6.1 Roles

- Owner/Admin — operational administration only
- Clinical Supervisor — clinical oversight for explicitly assigned therapists or patients
- Therapist — own patients and clinical records
- Assistant/Receptionist — scheduling and non-clinical operations

### 6.2 Permission Matrix (proposed defaults)

| Resource / action                              | Therapist                                              | Supervisor                                        | Admin                               | Receptionist                                     |
| ---------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------- | ----------------------------------- | ------------------------------------------------ |
| Manage clinic users                            | No                                                     | No                                                | Yes                                 | No                                               |
| Manage appointments (scheduling operations)    | Own appointments and appointments of assigned patients | Appointments of assigned supervisees' patients    | All appointments (operational only) | All appointments (operational only, if granted)  |
| Read patient demographics                      | Assigned patients                                      | Patients of assigned supervisees                  | All patients (operational only)     | All patients (operational only, if granted)      |
| Read clinical notes                            | Only notes for currently assigned patients, plus own authored notes (see 6.3) | Only notes for explicitly assigned patients or supervisees | No                                  | No                                               |
| Read assessments, treatment plans, progress    | Assigned patients                                      | Explicitly assigned patients or supervisees       | No                                  | No                                               |
| Finalize own notes                             | Yes                                                    | Only if also authorized as treating therapist     | No                                  | No                                               |
| Review security metadata                       | No by default                                          | No by default                                     | Explicit permission                 | No                                               |

Hard rules:
- Operational scopes (appointment management, demographics access, administrative operations) do not grant clinical access to any patient.
- No role gains clinical-note, assessment, treatment-plan, or progress-entry access merely because it can manage the patient's appointments or demographics.
- A supervisor's access to a supervisee's patients must still respect the explicit clinical-assignment rules in Section 6.3. Being a supervisee's supervisor does not automatically grant access to every patient in that supervisee's caseload; each patient must be explicitly assigned for supervision.
- The detailed authorization defaults in Section 6.3 take precedence over the table in case of ambiguity.

### 6.3 Authorization Defaults

- Therapist access to the patient record: a therapist can access only currently assigned patients. When a patient is reassigned, the therapist loses access to the patient record, including demographics, appointments, assessments, treatment plans, progress entries, and any notes authored by other therapists.
- Authored-records view: a therapist retains read access to the full clinical content of notes they personally authored, and addenda they personally created, for that patient. This access is provided through a dedicated authored-records view and does not grant access to any other part of the patient record.
  - The view must not expose other therapists' notes, assessments, treatment plans, progress entries, appointments, or general patient-record information.
  - Access is denied if the user's account is deactivated or their tenant membership is revoked.
  - Access to the authored-records view is audited, and its authorization is enforced server-side.
  - This policy is a product decision and requires validation with practitioners and legal/professional review before production. It is not presented as an established legal entitlement.
- Assistant/Receptionist access: assistants may view patient demographics and contact information for scheduling purposes, but cannot view clinical notes, assessments, treatment plans, or progress entries.
- Supervisor actions: by default, supervisors may read explicitly assigned clinical records but cannot finalize or amend another therapist's notes. Co-signing or supervisory review of another therapist's notes is a separate permission to be defined (see Open Questions).
- Patient archival: archiving makes the patient record read-only. Existing authorized users retain read access. No new clinical entries can be created for an archived patient. Archival does not delete records.
- Administrative exports: exports follow the same authorization rules as the underlying data. Administrators without clinical access cannot export clinical notes or any content they cannot otherwise read.
- Access revocation on user deactivation is immediate, including existing sessions and tokens.
- Patient assignment is granted, transferred, and revoked explicitly; the history of assignment changes is preserved.
- Solo practitioners may hold combined roles, but permissions remain explicit, and the system does not imply independent oversight where none exists.

### 6.4 Break-Glass Access

A restricted exceptional workflow with:
- Explicit reason.
- Narrow scope (specific patient and record).
- Time limit.
- Immediate logging.
- Notification to an independent authority where available.
- A review process.

Break-glass is not a general administrator override and does not grant automatic access to all patients.

## 7. Tenant Isolation and Data Access

- Modular monolith with a tenant-aware data model.
- Centralized tenant-scoped data-access layer. The requirement prohibits unscoped application access paths, not legitimate database administration; controlled exceptions for migrations, maintenance, and explicitly reviewed infrastructure operations are permitted.
- The active tenant is validated against the authenticated user's membership on every request.
- Client-supplied tenant identifiers are never trusted as authorization evidence.
- Every request enforces both tenant scope and the relevant resource-level permission.
- Background jobs, exports, reports, file downloads, and indirect object references follow the same rules.
- Composite foreign keys enforce tenant consistency where practical.
- Cross-tenant tests cover successful in-tenant access and negative cases for reads and mutations across every path, including exports, reporting, background jobs, and file access.
- Code review checks prevent bypass of the data-access layer.
- Audit logs are scoped per tenant.
- PostgreSQL Row-Level Security is NOT used in the MVP; it will be reassessed before broader SaaS deployment.

## 8. Authentication and Account Recovery

- Email + password login.
- Secure password hashing using a modern, established password-hashing algorithm.
- Rate limiting and abuse protection for login and password recovery.
- Secure session expiration, logout, and revocation.
- Immediate denial of access after account deactivation, including existing sessions and tokens.
- Recovery responses do not disclose whether a patient's account or a particular email address exists.
- Multi-factor authentication is a security enhancement to evaluate, not a mandatory MVP feature.
- Audit logging of login events and failed attempts.

## 9. Functional Modules (MVP)

### 9.1 Patient Management
- Create, view, update, and archive patient records.
- Demographics, contact information, emergency contact.
- Intake form data.
- File uploads (documents, scanned forms).
- Search and filter by name, status, and assigned therapist.
- Archive means the record is retained but hidden from active workflows. Archival is distinct from permanent deletion.

### 9.2 Consent Management
- Record the purpose and scope of consent, status, timestamp, and supporting evidence where applicable.
- Track consent version and method.
- Preserve the history of consent changes and withdrawals.
- Consent withdrawal does not automatically require deletion of all clinical records; retention and processing obligations require separate legal and professional review.

### 9.3 Appointment Scheduling (Basic)
- Create, edit, cancel appointments.
- Statuses: scheduled, completed, cancelled, no-show.
- Calendar view (day/week) using Jalali calendar.
- Per-therapist view; organization view for admins/supervisors.
- Basic conflict detection (same therapist, overlapping times).
- No external calendar sync in MVP.

### 9.4 Clinical Documentation
- A small set of predefined note templates (e.g., SOAP, DAP, BIRP). A simple configuration mechanism may be added only if pilot practitioners need it. A comprehensive template engine is deferred.
- Draft notes remain editable by their author.
- Finalized notes are permanently immutable. They cannot be overwritten, silently deleted, or reverted to draft.
- Correction model (single consistent rule): a correction creates an addendum linked to the original finalized note. The addendum records the author, timestamp, reason, and correction content. The original note and all addenda appear together in the patient's clinical history. The original remains permanently visible and unaltered.
- All corrections, regardless of timing, follow the same addendum model. There is no separate correction window with different behavior.
- Whether corrections by the original author shortly after finalization should be visually distinguished from later corrections is an unresolved product decision and is deferred. Until resolved, no distinction is implemented.
- Supporting replacement-version models for corrections is deferred.
- No digital-signature or legal-attestation workflow in MVP.

### 9.5 Treatment Plans and Progress Tracking
- Create treatment plans with goals and objectives.
- Link goals to sessions and progress entries.
- Progress notes and outcome tracking per goal.
- View progress timeline per patient.
- Outcome measures: record scores over time; no comprehensive instrument library in MVP.

### 9.6 Assessments / Test Results
- Record assessment results (manual entry).
- Attach scanned or uploaded files.
- Associate with patient and date.
- History view per patient.
- No pre-loaded test library in MVP.

### 9.7 Session History
- Chronological list of sessions per patient.
- Linked notes, assessments, and progress entries.
- Filter by date range and therapist.

### 9.8 Files and Documents
- Upload, view, and download patient-related files.
- Private storage by default; no public patient-file URLs.
- Authorization checks before every download or preview.
- File type and size validation, with safe handling of uploaded content.
- Tenant-scoped file ownership and associations.
- Protection against unauthorized access through guessed IDs or expired links.
- Encryption at rest and in transit. AES-256 is a baseline target; naming the algorithm alone does not establish secure encryption.
- Backups and exported files are encrypted, with access to encryption keys restricted separately from ordinary application access.
- Audit logging of file access.

### 9.9 Reporting (Basic)
- Operational summaries: appointment counts, active patients, no-show rates.
- Per-therapist and per-tenant views.
- CSV export is the initial export format. PDF generation is deferred unless a concrete operational need is demonstrated.
- No advanced analytics in MVP.

### 9.10 Audit and Security Logging
- Security-relevant events are logged. The exact set of events, retention, and performance impact will be defined during implementation. At minimum, the following classes of events are candidates: login, patient record access, note create/edit/finalize/correct, export, deletion attempts, break-glass access, and denied authorization.
- Log metadata for security auditing; do not log note contents by default.
- Explicit retention and access policy for audit logs.
- No blanket logging of every internal database operation.
- Clinical-note content, passwords, session tokens, and encryption keys must not appear in application logs, error reports, or diagnostic traces.
- Safe error handling with redaction of sensitive data in logs is required.

### 9.11 Audit-Log Integrity
- Restricted write and deletion privileges for audit records.
- Events attributed to a user or system process.
- Reliable timestamps and correlation with the relevant operation.
- Protection against ordinary application users modifying or deleting audit records.
- Documented retention and review policies.
- Tamper-evident storage or external log forwarding may be evaluated during implementation. A complicated logging platform is not required for the MVP without a demonstrated need.

## 10. Security and Privacy Baseline

- TLS in transit; AES-256 at rest as a baseline target.
- Role-based access control as defined in Section 6.
- Break-glass access is restricted and reviewed.
- Exports, backups, and uploaded files are encrypted.
- Privacy-by-design principles documented.
- This specification does NOT claim Iranian legal compliance. Legal and professional requirements in Iran require verification by qualified counsel before any compliance claim is made.
- References to review: patient rights, data protection obligations, and professional confidentiality rules.

## 11. Backups and Recovery

- Backup, restore, and cross-tenant isolation tests are required.
- A documented backup-and-restore procedure is required.
- A successful restoration test is required before production use.
- Restoration must preserve tenant boundaries, permissions, clinical-record history, and audit records.
- Specific recovery objectives remain provisional until defined.

## 12. Non-Functional Requirements

- Maintainable architecture suitable for future scaling. Actual horizontal-scaling work is deferred until performance requirements are known.
- Performance targets to be defined after initial prototype.
- Backup and recovery objectives to be defined (provisional).
- Audit-log retention period to be defined (provisional).
- Farsi-first UI with RTL and Jalali calendar.
- Accessibility baseline as in Section 4.

## 13. Decisions, Provisional Items, Deferred Items, and Pre-Production Requirements

Decided:
- Specialty focus: mental health (psychology, psychotherapy, counseling).
- Initial customers: solo practitioners and clinics of 2–5 therapists.
- Patient accounts: staff-only in MVP.
- Clinical-record workflow: draft and immutable finalized notes; all corrections via addenda that preserve the original.
- Scheduling: core MVP but basic.
- Shared domain model for solo and organization product profiles.
- Role separation: operational admin, clinical supervision, metadata-only security auditing.
- Tenant-aware access with application-layer enforcement; RLS deferred.
- Break-glass access as a restricted exceptional workflow.
- Frontend and database stack as in Section 3.
- No default clinical-note access for administrators or receptionists.
- Operational scopes do not grant clinical access under any role.

Provisional (requires validation):
- Whether corrections by the original author shortly after finalization should be visually distinguished from later corrections. Not implemented until resolved.
- Exact permission matrix values.
- Supervisor co-signing or supervisory review permission.
- Therapist access to full content of their own authored notes after reassignment (current default: granted via authored-records view with safeguards; requires practitioner and legal/professional validation).
- Break-glass authorization and review mechanism design.
- Backend framework choice (FastAPI vs Django).
- Deployment topology.
- Backup and recovery objectives.
- Audit-log retention period and exact event set.

Deferred:
- Patient portal.
- Telehealth.
- Billing and payments.
- External calendar, e-signature, payment integrations.
- Comprehensive assessment/test library.
- Advanced analytics and reporting.
- PDF export generation.
- Comprehensive note template engine.
- Replacement-version correction model.
- Multi-language support beyond Farsi.
- Specialty-specific modules (physiotherapy, OT, speech, psychiatry).
- PostgreSQL RLS adoption.
- Isolated per-clinic deployments.
- Horizontal-scaling implementation.

Required before production:
- Verified authorization boundaries.
- Secure authentication and session revocation.
- Private file handling and access controls.
- Tested backup restoration.
- Audit-log protection and redaction of sensitive data.
- Legal and professional review.
- Practitioner validation of the authored-records view and reassignment policy.

## 14. Open Questions

1. Backend framework: FastAPI or Django? Criteria: team familiarity, admin tooling, async needs, ORM maturity, long-term maintainability.
2. Deployment topology for MVP.
3. Backup and recovery objectives.
4. Audit-log retention policy and exact event set.
5. Exact break-glass authorization and review workflow.
6. Whether supervisors may co-sign or review another therapist's notes, and under what conditions.
7. Whether corrections by the original author shortly after finalization should be visually distinguished from later corrections.

## 15. Success Criteria for MVP

- A solo therapist can manage patients, appointments, notes, treatment plans, assessments, and files end to end.
- A small clinic can onboard multiple therapists with correct permission boundaries.
- Clinical notes are finalized immutably and corrected only via addenda that preserve the original.
- Tenant isolation is enforced and verified by automated tests covering positive and negative cases.
- The UI is fully usable in Farsi with RTL and Jalali calendar.