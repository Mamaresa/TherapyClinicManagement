[← Back to index](../../README.md)

# ResetToken

> `reset_token` · Group A: tenancy, identity, authentication

**Purpose:** single-use password-reset tokens.

```sql
CREATE TABLE reset_token (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES app_user(id) ON DELETE RESTRICT,
    token_hash   BYTEA NOT NULL,
    issued_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at   TIMESTAMPTZ NOT NULL,
    consumed_at  TIMESTAMPTZ,
    CONSTRAINT uq_reset_token_hash UNIQUE (token_hash),
    CONSTRAINT ck_reset_dates CHECK (expires_at > issued_at)
);
```

**Design notes**

- `token_hash` is a **hash** of the token. The raw token is emailed to the user and never stored, so a database leak does not yield usable reset links.
- `consumed_at` marks the token as used. A token is valid only while `consumed_at IS NULL` and `expires_at > now()`.
- `uq_reset_token_hash` guarantees lookup by hash is unambiguous.

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

[← Session](session.md) · [Group overview](README.md) · [Invitation →](invitation.md)
