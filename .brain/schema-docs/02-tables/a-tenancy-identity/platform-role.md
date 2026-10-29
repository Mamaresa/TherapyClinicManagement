[← Back to index](../../README.md)

# PlatformRole

> `platform_role` · Group A: tenancy, identity, authentication

**Purpose:** platform-level staff roles that sit outside any tenant. Implements X-8.

```sql
CREATE TABLE platform_role (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES app_user(id) ON DELETE RESTRICT,
    role         TEXT NOT NULL
                 CHECK (role IN ('platform_admin','platform_auditor')),
    granted_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    revoked_at   TIMESTAMPTZ,
    CONSTRAINT ck_platform_role_no_membership CHECK (TRUE)
);
CREATE UNIQUE INDEX uq_platform_role_active
    ON platform_role (user_id, role)
    WHERE revoked_at IS NULL;
```

**Design notes**

- Platform roles **never** grant clinical access. The access predicate rejects platform-only sessions from clinical endpoints.
- `CHECK (TRUE)` does nothing. The original text says it is "a placeholder to make the intent visible; the real enforcement is the access predicate". It adds no protection and could be removed or replaced with a comment (see [review notes on Part 1](../../05-notes/review-notes-part1.md)).
- `uq_platform_role_active` prevents the same active role being granted twice to the same user.

## Relationships

**Depends on (this table references):** [User](app-user.md)

**Referenced by:** no table

## Triggers on this table

None.

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[← Invitation](invitation.md) · [Group overview](README.md)
