[← Back to index](../../README.md)

# ClinicalNote

> `clinical_note` · Group E: clinical notes

**Purpose:** the finalized, immutable clinical note, and also the addendum record used to correct a finalized note. Implements D7, N-2 and N-7.

```sql
CREATE TABLE clinical_note (
    id                            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id                     UUID NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
    patient_id                    UUID NOT NULL,
    author_membership_id          UUID NOT NULL,
    template                      TEXT NOT NULL,
    template_version              TEXT NOT NULL,
    content                       JSONB NOT NULL,
    finalized_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    content_hash                  BYTEA NOT NULL,
    hash_algorithm                TEXT NOT NULL,
    hash_canonicalization_version TEXT NOT NULL,
    source_draft_id               UUID NOT NULL,
    addendum_to_note_id           UUID,
    addendum_reason               TEXT,
    CONSTRAINT fk_cn_patient
        FOREIGN KEY (patient_id, tenant_id)
        REFERENCES patient (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_cn_author
        FOREIGN KEY (author_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_cn_source_draft
        FOREIGN KEY (source_draft_id, patient_id, tenant_id)
        REFERENCES clinical_note_draft (id, patient_id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_cn_addendum
        FOREIGN KEY (addendum_to_note_id, patient_id, tenant_id)
        REFERENCES clinical_note (id, patient_id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT uq_cn_id_tenant UNIQUE (id, tenant_id),
    CONSTRAINT uq_cn_id_patient_tenant UNIQUE (id, patient_id, tenant_id),
    CONSTRAINT uq_cn_source_draft UNIQUE (source_draft_id),
    CONSTRAINT ck_cn_content_json CHECK (jsonb_typeof(content) = 'object'),
    CONSTRAINT ck_cn_hash_len CHECK (octet_length(content_hash) = 32),
    CONSTRAINT ck_cn_addendum_pair CHECK (
        (addendum_to_note_id IS NULL AND addendum_reason IS NULL)
        OR (addendum_to_note_id IS NOT NULL
            AND addendum_reason IS NOT NULL
            AND length(trim(addendum_reason)) > 0)
    ),
    CONSTRAINT ck_cn_addendum_not_self CHECK (
        addendum_to_note_id IS NULL OR addendum_to_note_id <> id
    )
);
CREATE INDEX ix_cn_patient_finalized
    ON clinical_note (patient_id, finalized_at);
CREATE INDEX ix_cn_author_finalized
    ON clinical_note (author_membership_id, finalized_at);
CREATE INDEX ix_cn_addendum
    ON clinical_note (addendum_to_note_id)
    WHERE addendum_to_note_id IS NOT NULL;
```

**Source notes (verbatim):**

> Notes: implements D7 and N-2 and N-7. content_hash is 32 bytes (SHA-256). hash_algorithm and hash_canonicalization_version are set at insert so future changes of scheme do not require updating existing notes. template_version on the note is independent of the note's own schema, so a template upgrade does not break finalized notes. uq_cn_source_draft ensures one finalized note per draft (N-4). Immutability of the row is enforced by trigger and by revoked UPDATE/DELETE privileges (Sections 14 and 15); the trigger rejects UPDATE and DELETE once the row exists. No appointment_id column; linking is via NoteAppointmentLink so finalized notes are never modified after linking. ck_cn_addendum_not_self prevents direct self-reference; longer cycles are impossible because rows are insert-only and a row's id cannot appear as its own addendum_to_note_id.

**Column guide**

| Column | Meaning |
|---|---|
| `content` | The finalized note body (JSON object). |
| `finalized_at` | When the note was finalized. |
| `content_hash` | A SHA-256 digest of the content (exactly 32 bytes), used to detect later tampering. |
| `hash_algorithm` | Which hash was used (for example `sha256`). Stored per row, so the algorithm can change in future without touching old rows. |
| `hash_canonicalization_version` | Which rules were used to turn the JSON into a stable byte sequence before hashing (key order, whitespace, and so on). Also stored per row for the same reason. |
| `source_draft_id` | The draft this note was finalized from. |
| `addendum_to_note_id` | If this row is a correction, the earlier note it corrects. `NULL` for an original note. |
| `addendum_reason` | Why the addendum was made. Required for an addendum. |

**Constraints and indexes explained**

- `fk_cn_source_draft`: a three-column composite FK, so the draft must be for the **same patient and tenant**.
- `uq_cn_source_draft`: each draft can be finalized **only once** (N-4). Together with the FK this makes draft-to-note a one-to-one relationship, as the ER diagram shows.
- `fk_cn_addendum`: a **self-referencing** composite FK. An addendum must refer to a note of the **same patient and tenant**. If `addendum_to_note_id` is `NULL`, `MATCH SIMPLE` skips the check, which is correct for an original note.
- `ck_cn_addendum_pair`: either both `addendum_to_note_id` and `addendum_reason` are empty (original note), or the target is set and the reason is non-blank (addendum). Neither can be present without the other.
- `ck_cn_addendum_not_self`: a note cannot be an addendum to itself.
- `ck_cn_hash_len`: `octet_length(content_hash) = 32`, the size of a SHA-256 digest.
- `ck_cn_content_json`: `content` must be a JSON object.
- `uq_cn_id_tenant`, `uq_cn_id_patient_tenant`: unique keys for composite FKs from other tables (`note_appointment_link` uses the three-column one, and the table's own self-FK uses it too).
- Indexes: notes for a patient by finalization time, notes by author, and a partial index on addenda.

**Design notes**

- **Immutability.** A finalized note is never changed. The trigger `enforce_clinical_note_immutable` rejects every `UPDATE` and `DELETE`, and the runtime database role is also meant to have `UPDATE` and `DELETE` privileges revoked. The source describes the finalization check as implicit: rows are only inserted through the finalize path.
- **Corrections** are made by inserting a new `clinical_note` row whose `addendum_to_note_id` points at the note being corrected. There is no supersession in the MVP (D7), so the original stays as it was and the addendum sits beside it.
- **No `appointment_id` column.** Linking a note to an appointment happens through `note_appointment_link`, because a column on an immutable row could not be filled in later ([design decisions (technical resolution)](../../01-foundations/design-decisions.md)).
- **`template_version`** is independent of the structure of `content`, so upgrading a template does not invalidate old notes.
- **Why cycles cannot occur.** A row can only reference a row that already exists, and rows are insert-only, so a chain of addenda can only point backwards in time. The self-reference check handles the one remaining case.
- The schema does not say whether an addendum may itself be corrected by another addendum, or whether the addendum's author must be the original author. Those are application rules.

## Relationships

**Depends on (this table references):** [ClinicalNoteDraft](clinical-note-draft.md), [Patient](../b-patients-assignments/patient.md), [Tenant](../a-tenancy-identity/tenant.md), [TenantMembership](../a-tenancy-identity/tenant-membership.md)

**Referenced by:** [NoteAppointmentLink](note-appointment-link.md)

This table also references itself (self-referencing foreign key).

## Triggers on this table

- [enforce_clinical_note_immutable](../../03-enforcement/triggers/enforce_clinical_note_immutable.md): fires on BEFORE UPDATE, BEFORE DELETE
- [enforce_archived_read_only](../../03-enforcement/triggers/enforce_archived_read_only.md): applies to this table through the child-table check for archived patients

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[← ClinicalNoteDraft](clinical-note-draft.md) · [Group overview](README.md) · [NoteAppointmentLink →](note-appointment-link.md)
