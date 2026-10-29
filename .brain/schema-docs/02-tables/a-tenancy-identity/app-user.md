[← Back to index](../../README.md)

# User (table `app_user`)

> `app_user` · Group A: tenancy, identity, authentication

**Purpose:** one row per human account, independent of any clinic. A person who works at two clinics is one user with two memberships.

```sql
CREATE TABLE app_user (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT NOT NULL,
    email_norm      TEXT NOT NULL,
    password_hash   TEXT NOT NULL,
    full_name       TEXT NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    deactivated_at  TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_user_email_norm UNIQUE (email_norm),
    CONSTRAINT ck_user_active_consistent CHECK (
        (is_active = FALSE AND deactivated_at IS NOT NULL)
        OR is_active = TRUE
    )
);
CREATE INDEX ix_user_email_norm ON app_user (email_norm);
```

**Column guide**

| Column | Meaning |
|---|---|
| `email` | The email as the user typed it. |
| `email_norm` | The normalized form used for uniqueness and lookup. Persian/Arabic characters and digits are folded to a single canonical form. |
| `password_hash` | A hash only. Plaintext passwords are never stored. |
| `is_active` / `deactivated_at` | Soft deactivation. |

**Constraints explained**

- `uq_user_email_norm`: uniqueness is on the **normalized** column. Without this, visually identical emails written with different Persian/Arabic character variants could create duplicate accounts.
- `ck_user_active_consistent`: an inactive user must have a deactivation timestamp.

**Design notes**

- The table is called `app_user` because `user` is a reserved keyword in PostgreSQL.
- The normalization rule is an **implementation requirement** (Section 11 in Part 2 of the source; the normalization requirement is listed in [application-level rules](../../03-enforcement/application-level-rules.md)). The database stores the result but does not compute it.
- `ix_user_email_norm` duplicates the index that the `UNIQUE` constraint already creates (see [review notes on Part 1](../../05-notes/review-notes-part1.md)).

## Relationships

**Depends on (this table references):** none

**Referenced by:** [AuditEvent](../i-audit/audit-event.md), [PlatformRole](platform-role.md), [ResetToken](reset-token.md), [Session](session.md), [TenantMembership](tenant-membership.md)

## Triggers on this table

- [set_updated_at](../../03-enforcement/triggers/set_updated_at.md): BEFORE UPDATE

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[← Tenant](tenant.md) · [Group overview](README.md) · [TenantMembership →](tenant-membership.md)
