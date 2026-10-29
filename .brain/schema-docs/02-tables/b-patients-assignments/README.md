[← Back to index](../../README.md)

# Group B: patients, assignments, supervision

| Table | SQL name | Purpose |
|---|---|---|
| [Patient](patient.md) | `patient` | the person receiving care at one clinic. Clinic-scoped identity (D1). |
| [ClinicalAssignment](clinical-assignment.md) | `clinical_assignment` | records which therapist (and optional supervisor) is responsible for a patient, in which role, and for what period. Implements D-N5, D-N8 and X-1. |
| [ClinicalSupervision](clinical-supervision.md) | `clinical_supervision` | gives a supervisor clinical access to **one specific patient** supervised through a specific therapist (D9, X-4 part 1). |
| [SupervisoryOperationalScope](supervisory-operational-scope.md) | `supervisory_operational_scope` | gives a supervisor **operational** oversight (demographics, appointments) over a supervisee's patients, without clinical access (D9, X-4 part 2). |
