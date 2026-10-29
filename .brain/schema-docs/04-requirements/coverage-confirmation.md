[← Back to index](../README.md)

# Coverage confirmation

All 25 tables promised in Part 1 are defined:

Part 1: [Tenant](../02-tables/a-tenancy-identity/tenant.md), [User](../02-tables/a-tenancy-identity/app-user.md), [TenantMembership](../02-tables/a-tenancy-identity/tenant-membership.md), [MembershipGrant](../02-tables/a-tenancy-identity/membership-grant.md), [Session](../02-tables/a-tenancy-identity/session.md), [ResetToken](../02-tables/a-tenancy-identity/reset-token.md), [Invitation](../02-tables/a-tenancy-identity/invitation.md), [PlatformRole](../02-tables/a-tenancy-identity/platform-role.md), [Patient](../02-tables/b-patients-assignments/patient.md), [ClinicalAssignment](../02-tables/b-patients-assignments/clinical-assignment.md), [ClinicalSupervision](../02-tables/b-patients-assignments/clinical-supervision.md), [SupervisoryOperationalScope](../02-tables/b-patients-assignments/supervisory-operational-scope.md).

Part 2: [ConsentTextVersion](../02-tables/c-consent/consent-text-version.md), [ConsentRecord](../02-tables/c-consent/consent-record.md), [Appointment](../02-tables/d-appointments/appointment.md), [AppointmentHistory](../02-tables/d-appointments/appointment-history.md), [ClinicalNoteDraft](../02-tables/e-clinical-notes/clinical-note-draft.md), [ClinicalNote](../02-tables/e-clinical-notes/clinical-note.md), [NoteAppointmentLink](../02-tables/e-clinical-notes/note-appointment-link.md), [TreatmentPlan](../02-tables/f-treatment/treatment-plan.md), [TreatmentGoal](../02-tables/f-treatment/treatment-goal.md), [ProgressEntry](../02-tables/f-treatment/progress-entry.md), [AssessmentResult](../02-tables/g-assessments/assessment-result.md), [PatientFile](../02-tables/h-files/patient-file.md), [AuditEvent](../02-tables/i-audit/audit-event.md).

Count check: 12 + 13 = 25.

All relationships in the ER diagram (Part 1, Section 1, which is the [ER diagram](../01-foundations/er-diagram.md)) are backed by a foreign key:

| Relationship (from diagram) | Backed by |
|---|---|
| Tenant–TenantMembership | tenant_membership.tenant_id → tenant.id |
| User–TenantMembership | tenant_membership.user_id → app_user.id |
| User–Session | session.user_id → app_user.id |
| User–ResetToken | reset_token.user_id → app_user.id |
| User–PlatformRole | platform_role.user_id → app_user.id |
| Tenant–Invitation | invitation.tenant_id → tenant.id |
| TenantMembership–Invitation | invitation.invited_by_membership_id + tenant_id |
| TenantMembership–MembershipGrant | membership_grant.membership_id + tenant_id |
| Tenant–Patient | patient.tenant_id → tenant.id |
| Patient–ClinicalAssignment | clinical_assignment.patient_id + tenant_id |
| TenantMembership–ClinicalAssignment | clinical_assignment.therapist_membership_id + tenant_id, and supervisor_membership_id + tenant_id |
| Patient–ClinicalSupervision | clinical_supervision.patient_id + tenant_id |
| TenantMembership–ClinicalSupervision | clinical_supervision.supervisor_membership_id + tenant_id, and therapist_membership_id + tenant_id |
| TenantMembership–SupervisoryOperationalScope | supervisory_operational_scope.supervisor_membership_id and supervisee_membership_id, both + tenant_id |
| Tenant–ConsentTextVersion | consent_text_version.tenant_id (nullable) → tenant.id |
| Patient–ConsentRecord | consent_record.patient_id + tenant_id |
| ConsentTextVersion–ConsentRecord | consent_record.consent_text_version_id → consent_text_version.id |
| ConsentRecord–ConsentRecord (withdraws) | consent_record.withdraws_consent_id + patient_id + tenant_id |
| PatientFile–ConsentRecord (evidence) | consent_record.evidence_file_id + patient_id + tenant_id |
| Patient–Appointment | appointment.patient_id + tenant_id |
| TenantMembership–Appointment | appointment.therapist_membership_id + tenant_id |
| Appointment–AppointmentHistory | appointment_history.appointment_id + tenant_id |
| TenantMembership–AppointmentHistory | appointment_history.actor_membership_id + tenant_id |
| Patient–ClinicalNoteDraft | clinical_note_draft.patient_id + tenant_id |
| TenantMembership–ClinicalNoteDraft | clinical_note_draft.author_membership_id + tenant_id |
| Patient–ClinicalNote | clinical_note.patient_id + tenant_id |
| TenantMembership–ClinicalNote | clinical_note.author_membership_id + tenant_id |
| ClinicalNoteDraft–ClinicalNote (finalizes to) | clinical_note.source_draft_id + patient_id + tenant_id; uq_cn_source_draft ensures one-to-one |
| ClinicalNote–ClinicalNote (addendum to) | clinical_note.addendum_to_note_id + patient_id + tenant_id |
| ClinicalNote–NoteAppointmentLink | note_appointment_link.note_id + patient_id + tenant_id |
| Appointment–NoteAppointmentLink | note_appointment_link.appointment_id + patient_id + tenant_id |
| TenantMembership–NoteAppointmentLink | note_appointment_link.created_by_membership_id + tenant_id (and removed_by_membership_id + tenant_id when set) |
| Patient–TreatmentPlan | treatment_plan.patient_id + tenant_id |
| TenantMembership–TreatmentPlan | treatment_plan.created_by_membership_id + tenant_id |
| TreatmentPlan–TreatmentGoal | treatment_goal.treatment_plan_id + patient_id + tenant_id |
| TreatmentGoal–ProgressEntry | progress_entry.treatment_goal_id + patient_id + tenant_id |
| Patient–ProgressEntry | progress_entry.patient_id + tenant_id |
| TenantMembership–ProgressEntry | progress_entry.recorded_by_membership_id + tenant_id |
| Patient–AssessmentResult | assessment_result.patient_id + tenant_id |
| TenantMembership–AssessmentResult | assessment_result.recorded_by_membership_id + tenant_id |
| PatientFile–AssessmentResult | assessment_result.file_id + patient_id + tenant_id |
| Patient–PatientFile | patient_file.patient_id + tenant_id |
| TenantMembership–PatientFile | patient_file.uploaded_by_membership_id + tenant_id |
| Tenant–AuditEvent | audit_event.tenant_id → tenant.id (nullable) |
| User–AuditEvent | audit_event.actor_user_id → app_user.id |
| TenantMembership–AuditEvent | audit_event.actor_membership_id → tenant_membership.id |

Every relationship in the diagram is backed by a declared foreign key or by a check with a documented trigger or application-level enforcement. No relationship is missing.
