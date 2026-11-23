# Therapy Clinic Management

A web-based CRM for mental health professionals: psychologists, psychotherapists and counselors. It helps solo practitioners and small clinics manage their patients, appointments, clinical notes, treatment plans, assessments and patient files in one place.

The application is in Farsi with a right-to-left layout and uses the Jalali calendar.

## What it does

- **Patients:** demographics, contact details, intake information and archiving.
- **Appointments:** day and week calendar with conflict detection.
- **Clinical notes:** drafts, and finalized notes that can never be changed; corrections are added as addenda.
- **Treatment and assessments:** treatment plans, goals, progress tracking and assessment results.
- **Files:** private storage of patient documents.
- **Clinics and roles:** owner/admin, clinical supervisor, therapist and assistant roles, with each clinic's data kept separate.
- **Audit:** a log of security-relevant actions.

## Technology

Django and Django REST Framework on PostgreSQL. A React + TypeScript frontend is planned.

## Project status

Early development. The full feature specification is in [backend/docs/features.md](backend/docs/features.md), and setup instructions are in [backend/README.md](backend/README.md).
