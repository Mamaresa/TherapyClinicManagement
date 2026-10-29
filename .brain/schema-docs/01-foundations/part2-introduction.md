[← Back to index](../README.md)

# Part 2 introduction: source limitation, conventions, numbering

**Source:** Actor Response 62 (Actor → Operator).

This part completes the 25 tables started in Part 1 (Groups C to I), and provides the constraint-enforcement summary, the requirements-to-schema mapping and the coverage confirmation.

**Source limitation (unchanged), as stated in the source:** derived from features.md as pasted in this conversation, and from the decisions in Actor Response 60 (final conceptual design). No files, models, migrations, SQL, or implementation code have been created. The SQL below is design specification, not applied DDL.

**Conventions carried from Part 1, as stated in the source:** UUID primary keys with `gen_random_uuid()`; `TIMESTAMPTZ` for instants; `tenant_id UUID NOT NULL` on tenant-owned tables; composite FK pattern with `UNIQUE (id, tenant_id)` or `UNIQUE (id, patient_id, tenant_id)` on parents; `ON DELETE RESTRICT` and `ON UPDATE RESTRICT` throughout; `MATCH SIMPLE` (nullable FK columns skip the check, safe because `tenant_id` is `NOT NULL`).

> **Numbering note for this documentation set.** The source Part 2 numbered its sections 6 to 17, which collided with the numbering of Part 1. In this documentation set the sections are renumbered so they continue from Part 1 (Group C is [Group C](../02-tables/c-consent/README.md), and so on). The source text is kept word for word; where the source refers to one of its own section numbers, [section crosswalk](../05-notes/section-crosswalk.md) gives the exact location in this documentation set.

> **Reading order for implementation.** `consent_record` ([ConsentRecord](../02-tables/c-consent/consent-record.md)) and `assessment_result` ([AssessmentResult](../02-tables/g-assessments/assessment-result.md)) reference `patient_file` ([PatientFile](../02-tables/h-files/patient-file.md)), so in real DDL `patient_file` must be created first, or those constraints must be added afterwards with `ALTER TABLE`. See [review notes on Part 2](../05-notes/review-notes-part2.md).
