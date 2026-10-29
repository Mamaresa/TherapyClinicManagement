[← Back to index](../../README.md)

# ClinicalNoteDraft

> `clinical_note_draft` · Group E: clinical notes

**Purpose:** an editable work-in-progress clinical note. When finalized, a separate immutable `clinical_note` row is created from it.

```sql
CREATE TABLE clinical_note_draft (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id            UUID NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
    patient_id           UUID NOT NULL,
    author_membership_id UUID NOT NULL,
    template             TEXT NOT NULL CHECK (template IN ('soap','dap','birp','free')),
    template_version     TEXT NOT NULL,
    content              JSONB NOT NULL,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_cnd_patient
        FOREIGN KEY (patient_id, tenant_id)
        REFERENCES patient (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_cnd_author
        FOREIGN KEY (author_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT uq_cnd_id_patient_tenant UNIQUE (id, patient_id, tenant_id),
    CONSTRAINT ck_cnd_content_json CHECK (jsonb_typeof(content) = 'object')
);
CREATE INDEX ix_cnd_patient_updated
    ON clinical_note_draft (patient_id, updated_at);
CREATE INDEX ix_cnd_author_updated
    ON clinical_note_draft (author_membership_id, updated_at);
```

**Source notes (verbatim):**

> Notes: drafts are editable while the author has an active assignment. On reassignment, the draft is locked (application-enforced, Section 16) and remains finalizable by the author through the authored-records view.

**Column guide**

| Column | Meaning |
|---|---|
| `template` | The note format: `soap`, `dap`, `birp` or `free` (free text). These are standard clinical note structures. |
| `template_version` | Which version of that template was used, so a later template change does not misread old notes. |
| `content` | The note body as a JSON object. |
| `author_membership_id` | The therapist writing the note. |

**Constraints and indexes explained**

- `uq_cnd_id_patient_tenant`: the key that `clinical_note.fk_cn_source_draft` targets, so a finalized note's draft must belong to the same patient and tenant.
- `ck_cnd_content_json`: `content` must be a JSON object.
- Two indexes support "drafts for a patient" and "an author's drafts", ordered by last update.

**Design notes**

- The draft table has **no status column**. Whether a draft has been finalized is shown by the existence of a `clinical_note` whose `source_draft_id` equals the draft's id.
- Editing rights depend on the author having an active `clinical_assignment`. The schema does not check this; it is application logic (the "Draft locking on reassignment" row in [application-level rules](../../03-enforcement/application-level-rules.md)).
- After reassignment the draft is locked but the author may still finalize it, through the authored-records view (D3, D4).

## Relationships

**Depends on (this table references):** [Patient](../b-patients-assignments/patient.md), [Tenant](../a-tenancy-identity/tenant.md), [TenantMembership](../a-tenancy-identity/tenant-membership.md)

**Referenced by:** [ClinicalNote](clinical-note.md)

## Triggers on this table

- [enforce_archived_read_only](../../03-enforcement/triggers/enforce_archived_read_only.md): applies to this table through the child-table check for archived patients
- [set_updated_at](../../03-enforcement/triggers/set_updated_at.md): BEFORE UPDATE

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[Group overview](README.md) · [ClinicalNote →](clinical-note.md)
