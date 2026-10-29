[← Back to index](../../README.md)

# PatientFile

> `patient_file` · Group H: files

**Purpose:** metadata about a file stored outside the database (the blob lives in object storage). Implements F-1 and D16.

```sql
CREATE TABLE patient_file (
    id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id                UUID NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
    patient_id               UUID NOT NULL,
    uploaded_by_membership_id UUID NOT NULL,
    storage_key              TEXT NOT NULL,
    original_filename        TEXT NOT NULL,
    mime_type                TEXT NOT NULL,
    size_bytes               BIGINT NOT NULL,
    checksum_sha256          BYTEA NOT NULL,
    lifecycle_state          TEXT NOT NULL DEFAULT 'pending'
                             CHECK (lifecycle_state IN ('pending','available','deleted','purge_pending','purged')),
    created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    purged_at                TIMESTAMPTZ,
    CONSTRAINT fk_pf_patient
        FOREIGN KEY (patient_id, tenant_id)
        REFERENCES patient (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_pf_uploader
        FOREIGN KEY (uploaded_by_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT uq_pf_storage_key UNIQUE (storage_key),
    CONSTRAINT uq_pf_id_tenant UNIQUE (id, tenant_id),
    CONSTRAINT uq_pf_id_patient_tenant UNIQUE (id, patient_id, tenant_id),
    CONSTRAINT ck_pf_size CHECK (size_bytes >= 0),
    CONSTRAINT ck_pf_hash_len CHECK (octet_length(checksum_sha256) = 32),
    CONSTRAINT ck_pf_purged CHECK (
        (lifecycle_state = 'purged' AND purged_at IS NOT NULL)
        OR (lifecycle_state <> 'purged' AND purged_at IS NULL)
    )
);
CREATE INDEX ix_pf_patient
    ON patient_file (patient_id);
CREATE INDEX ix_pf_tenant_state
    ON patient_file (tenant_id, lifecycle_state);
CREATE INDEX ix_pf_checksum
    ON patient_file (checksum_sha256);
```

**Source notes (verbatim):**

> Notes: implements F-1 and D16. storage_key is opaque and contains no patient information; the download path authorizes against the PatientFile record per request, never against knowledge of the key. original_filename may contain patient information and is stored with that in mind (access is authorization-gated like any other PII). lifecycle_state transitions are: pending to available (upload completed), available to deleted (soft delete), deleted to purge_pending (retention expires), purge_pending to purged (blob removed and purged_at set). Transitions are application-enforced; the state enum is a CHECK. The purge process design is deferred per D16.

**Column guide**

| Column | Meaning |
|---|---|
| `storage_key` | Opaque pointer to the blob in storage. Globally unique (`uq_pf_storage_key`). |
| `original_filename` | The filename the uploader gave. |
| `mime_type`, `size_bytes` | Validated type and size. |
| `checksum_sha256` | SHA-256 of the file contents (exactly 32 bytes). |
| `lifecycle_state` | `pending`, `available`, `deleted`, `purge_pending` or `purged`. |
| `purged_at` | When the blob was physically removed. |

**Constraints and indexes explained**

- `ck_pf_size`: size cannot be negative.
- `ck_pf_hash_len`: the checksum is exactly 32 bytes.
- `ck_pf_purged`: **two-way** consistency. `purged_at` is set **if and only if** the state is `purged`. A file cannot have a purge timestamp without being purged, nor be marked purged without one.
- `uq_pf_id_tenant`, `uq_pf_id_patient_tenant`: the keys other tables target. `consent_record` and `assessment_result` use the three-column one, so attached files always belong to the same patient.
- `ix_pf_patient`, `ix_pf_tenant_state`, `ix_pf_checksum`: lookups by patient, by tenant and state, and by checksum.

**Design notes**

- **Lifecycle** (application-enforced; the schema only checks the allowed values):

  `pending` → `available` (upload completed) → `deleted` (soft delete) → `purge_pending` (retention expires) → `purged` (blob removed, `purged_at` set).

- **Authorization.** Every download is authorized against the `patient_file` record on each request. Knowing the storage key is never enough.
- **Privacy.** `original_filename` can contain patient information, so it is treated like any other personal data and protected by authorization, not by encryption at column level.
- The purge process itself is deferred (D16).

## Relationships

**Depends on (this table references):** [Patient](../b-patients-assignments/patient.md), [Tenant](../a-tenancy-identity/tenant.md), [TenantMembership](../a-tenancy-identity/tenant-membership.md)

**Referenced by:** [AssessmentResult](../g-assessments/assessment-result.md), [ConsentRecord](../c-consent/consent-record.md)

## Triggers on this table

- [enforce_archived_read_only](../../03-enforcement/triggers/enforce_archived_read_only.md): applies to this table through the child-table check for archived patients

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[Group overview](README.md)
