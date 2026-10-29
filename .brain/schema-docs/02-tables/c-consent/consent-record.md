[← Back to index](../../README.md)

# ConsentRecord

> `consent_record` · Group C: consent

**Purpose:** the history of a patient's consents and withdrawals. Each row is either a **grant** or a **withdrawal** of an earlier grant. Implements requirements C-1 and C-3.

```sql
CREATE TABLE consent_record (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id              UUID NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
    patient_id             UUID NOT NULL,
    consent_text_version_id UUID NOT NULL REFERENCES consent_text_version(id) ON DELETE RESTRICT,
    purpose                TEXT NOT NULL,
    scope                  TEXT NOT NULL,
    method                 TEXT NOT NULL CHECK (method IN ('written','verbal','electronic')),
    status                 TEXT NOT NULL CHECK (status IN ('grant','withdrawal')),
    evidence_file_id       UUID,
    created_by_membership_id UUID NOT NULL,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    withdraws_consent_id   UUID,
    CONSTRAINT fk_cr_patient
        FOREIGN KEY (patient_id, tenant_id)
        REFERENCES patient (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_cr_creator
        FOREIGN KEY (created_by_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_cr_evidence
        FOREIGN KEY (evidence_file_id, patient_id, tenant_id)
        REFERENCES patient_file (id, patient_id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_cr_withdraws
        FOREIGN KEY (withdraws_consent_id, patient_id, tenant_id)
        REFERENCES consent_record (id, patient_id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT uq_cr_id_patient_tenant UNIQUE (id, patient_id, tenant_id),
    CONSTRAINT ck_cr_withdrawal_pair CHECK (
        (status = 'grant'      AND withdraws_consent_id IS NULL)
        OR (status = 'withdrawal' AND withdraws_consent_id IS NOT NULL)
    ),
    CONSTRAINT ck_cr_withdraws_not_self CHECK (withdraws_consent_id IS NULL OR withdraws_consent_id <> id)
);
CREATE UNIQUE INDEX uq_cr_withdrawn_once
    ON consent_record (withdraws_consent_id)
    WHERE withdraws_consent_id IS NOT NULL;
CREATE INDEX ix_cr_patient_status
    ON consent_record (patient_id, status);
CREATE INDEX ix_cr_patient_created
    ON consent_record (patient_id, created_at);
```

**Source notes (verbatim):**

> Notes: implements C-1 and C-3. Append-oriented: current state is derived from the latest row in the chain. The composite self-FK (withdraws_consent_id, patient_id, tenant_id) enforces same patient/tenant; enforcing that the target is a grant (not a withdrawal) requires a trigger (Section 15). The partial unique on withdraws_consent_id ensures a grant is withdrawn at most once. evidence_file_id uses the patient-scoped composite FK, so an evidence file from another patient cannot be linked. The compliance gap left by "withdrawal on archived patient" is handled by the archived-read-only trigger exception list (Section 15).

**Column guide**

| Column | Meaning |
|---|---|
| `consent_text_version_id` | The exact text the patient consented to (or withdrew from). |
| `purpose` | Why the consent is requested (free text, no CHECK). |
| `scope` | What the consent covers (free text, no CHECK). |
| `method` | How it was obtained: `written`, `verbal` or `electronic`. |
| `status` | `grant` (consent given) or `withdrawal` (an earlier grant is withdrawn). |
| `evidence_file_id` | Optional link to an uploaded file proving the consent (for example a scanned signed form). |
| `created_by_membership_id` | The member who recorded it. |
| `withdraws_consent_id` | For a withdrawal, the grant row it withdraws. `NULL` for a grant. |

**Constraints and indexes explained**

- `fk_cr_patient`, `fk_cr_creator`: composite FKs tie the record, the patient and the recording member to one tenant.
- `fk_cr_evidence`: a **three-column** composite FK `(evidence_file_id, patient_id, tenant_id)` against `patient_file`. The file must belong to the **same patient and tenant**, so evidence from another patient cannot be attached. If `evidence_file_id` is `NULL`, `MATCH SIMPLE` skips the check, which is correct because evidence is optional.
- `fk_cr_withdraws`: a **self-referencing** composite FK. A withdrawal must point at a row for the **same patient and tenant**.
- `uq_cr_id_patient_tenant`: the unique key that the self-FK above targets.
- `ck_cr_withdrawal_pair`: a `grant` must **not** point at anything, and a `withdrawal` **must** point at something. The two columns can never disagree.
- `ck_cr_withdraws_not_self`: a row cannot withdraw itself.
- `uq_cr_withdrawn_once` (partial unique): each grant can be withdrawn **at most once**. A second withdrawal pointing at the same grant is rejected.
- `ix_cr_patient_status`, `ix_cr_patient_created`: lookups of a patient's consents by status and by time.

**Design notes**

- **Append-oriented.** Rows are never edited or deleted (trigger `enforce_consent_record_append_only`, [trigger summary](../../03-enforcement/triggers/README.md)). The patient's *current* consent state is derived by reading the chain, not by reading a flag.
- **Re-consent after a withdrawal** is a new `grant` row; it does not reopen the old one.
- **What the database cannot check by itself:** that a withdrawal points at a *grant* and not at another withdrawal. That is the job of the trigger `enforce_consent_withdrawal_target_is_grant`. Likewise the tenant match between the consent text and the record is trigger-enforced.
- **Archived patients.** A withdrawal must stay possible even after a patient is archived; the archived-read-only trigger has an exception for `ConsentRecord` inserts ([trigger summary](../../03-enforcement/triggers/README.md)).

## Relationships

**Depends on (this table references):** [ConsentTextVersion](consent-text-version.md), [Patient](../b-patients-assignments/patient.md), [PatientFile](../h-files/patient-file.md), [Tenant](../a-tenancy-identity/tenant.md), [TenantMembership](../a-tenancy-identity/tenant-membership.md)

**Referenced by:** no table

This table also references itself (self-referencing foreign key).

## Triggers on this table

- [enforce_consent_record_append_only](../../03-enforcement/triggers/enforce_consent_record_append_only.md): fires on BEFORE UPDATE, BEFORE DELETE
- [enforce_archived_read_only](../../03-enforcement/triggers/enforce_archived_read_only.md): applies to this table through the child-table check for archived patients
- [enforce_consent_withdrawal_target_is_grant](../../03-enforcement/triggers/enforce_consent_withdrawal_target_is_grant.md): fires on BEFORE INSERT
- [enforce_consent_version_tenant_match](../../03-enforcement/triggers/enforce_consent_version_tenant_match.md): fires on BEFORE INSERT

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[← ConsentTextVersion](consent-text-version.md) · [Group overview](README.md)
