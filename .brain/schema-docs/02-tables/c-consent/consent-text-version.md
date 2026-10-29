[← Back to index](../../README.md)

# ConsentTextVersion

> `consent_text_version` · Group C: consent

**Purpose:** the versioned wording of a consent form. A consent record points at the exact text the patient agreed to. Texts can be provided by the platform for every clinic, or written by a single clinic (decision D8).

```sql
CREATE TABLE consent_text_version (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id      UUID REFERENCES tenant(id) ON DELETE RESTRICT,
    version_label  TEXT NOT NULL,
    body           TEXT NOT NULL,
    effective_from DATE NOT NULL,
    retired_at     DATE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_ctv_dates CHECK (retired_at IS NULL OR retired_at >= effective_from),
    CONSTRAINT uq_ctv_id_tenant UNIQUE (id, tenant_id)
);
CREATE UNIQUE INDEX uq_ctv_scope_label
    ON consent_text_version (COALESCE(tenant_id::TEXT, 'GLOBAL'), version_label);
CREATE INDEX ix_ctv_tenant_active
    ON consent_text_version (tenant_id, effective_from)
    WHERE retired_at IS NULL;
```

**Source notes (verbatim):**

> Notes: implements D8. tenant_id NULL means platform-provided. The COALESCE-based unique index allows one global row and one per-tenant row per version_label. Regular FK to id from ConsentRecord; the cross-table "same tenant or global" rule cannot be expressed as a FK and is trigger-enforced (Section 15).

**Column guide**

| Column | Meaning |
|---|---|
| `tenant_id` | The clinic that owns this text. **Nullable on purpose:** `NULL` means the text is provided by the platform and is usable by every clinic. This is the only tenant-optional table in the schema besides `audit_event`. |
| `version_label` | Human-readable version name (for example "v1" or "2026-01"). |
| `body` | The full consent text. |
| `effective_from` | First date the text may be used. A `DATE`, not a timestamp. |
| `retired_at` | Date after which the text should no longer be offered for new consents. `NULL` means still current. |

**Constraints and indexes explained**

- `ck_ctv_dates`: a text cannot be retired before it became effective.
- `uq_ctv_scope_label`: this unique index uses an **expression**, `COALESCE(tenant_id::TEXT, 'GLOBAL')`. In PostgreSQL, `NULL` values are treated as distinct in a plain unique index, so two global rows with the same `version_label` would both be allowed. Replacing `NULL` with the text `'GLOBAL'` makes all global rows share one scope. The result: one global row and one row per tenant for each `version_label`. A UUID rendered as text can never equal `'GLOBAL'`, so the two cannot collide.
- `ix_ctv_tenant_active`: partial index over texts that are not retired, ordered by `effective_from`, for "which texts can this clinic currently offer?".
- `uq_ctv_id_tenant`: defined for composite FK use, but see the design notes.

**Design notes**

- `consent_record` references this table with a **plain** FK on `id` (not a composite one), because a composite FK on `(id, tenant_id)` would require the record's tenant to equal the text's tenant, and that would block clinics from using platform-provided texts. The consequence is that the database no longer checks tenant matching, so the rule "the text is global or belongs to the same tenant as the record" is enforced by the trigger `enforce_consent_version_tenant_match` ([trigger summary](../../03-enforcement/triggers/README.md)).
- `uq_ctv_id_tenant` cannot enforce anything for global rows, because a unique constraint ignores rows with a `NULL` in any column. Nothing in the schema references it today.
- There is no trigger in the source's trigger list that stops `body` from being edited after a consent has been recorded against it. See [review notes on Part 2](../../05-notes/review-notes-part2.md).

## Relationships

**Depends on (this table references):** [Tenant](../a-tenancy-identity/tenant.md)

**Referenced by:** [ConsentRecord](consent-record.md)

## Triggers on this table

None.

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[Group overview](README.md) · [ConsentRecord →](consent-record.md)
