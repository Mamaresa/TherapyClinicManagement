[← Back to index](../../README.md)

# Session

> `session` · Group A: tenancy, identity, authentication

**Purpose:** one row per login session. Allows server-side revocation.

```sql
CREATE TABLE session (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID NOT NULL REFERENCES app_user(id) ON DELETE RESTRICT,
    tenant_context_id UUID REFERENCES tenant(id) ON DELETE RESTRICT,
    issued_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at        TIMESTAMPTZ NOT NULL,
    revoked_at        TIMESTAMPTZ,
    revocation_reason TEXT,
    CONSTRAINT ck_session_dates CHECK (expires_at > issued_at)
);
CREATE INDEX ix_session_user_active
    ON session (user_id, expires_at)
    WHERE revoked_at IS NULL;
```

**Column guide**

| Column | Meaning |
|---|---|
| `tenant_context_id` | The tenant the user is currently working in. Nullable because a session exists before the user picks a tenant. |
| `expires_at` | Hard expiry. |
| `revoked_at` / `revocation_reason` | Set when the session is ended early, for example on user deactivation. |

**Design notes**

- On every request, the access predicate checks `revoked_at IS NULL AND expires_at > now()` (requirement X-5).
- Revoking on deactivation is a plain `UPDATE` of `revoked_at`.
- `tenant_context_id` references `tenant` alone (not `tenant_membership`), so the schema does not itself guarantee that the user holds a membership in that tenant. The access predicate must check this on each request.

## Relationships

**Depends on (this table references):** [User](app-user.md), [Tenant](tenant.md)

**Referenced by:** no table

## Triggers on this table

None.

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[← MembershipGrant](membership-grant.md) · [Group overview](README.md) · [ResetToken →](reset-token.md)
