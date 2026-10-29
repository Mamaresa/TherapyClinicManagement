[← Back to index](../../README.md)

# Group A: tenancy, identity, authentication

| Table | SQL name | Purpose |
|---|---|---|
| [Tenant](tenant.md) | `tenant` | one row per clinic or practice. It is the root of data isolation. |
| [User](app-user.md) | `app_user` | one row per human account, independent of any clinic. A person who works at two clinics is one user with two memberships. |
| [TenantMembership](tenant-membership.md) | `tenant_membership` | connects a user to a tenant and carries the user's roles there. Almost every tenant-owned table points at this table to say "who". |
| [MembershipGrant](membership-grant.md) | `membership_grant` | extra, narrowly-scoped permissions that sit on top of a role. Implements the "if granted" and "explicit permission" wording of features.md 6.2 (X-3). |
| [Session](session.md) | `session` | one row per login session. Allows server-side revocation. |
| [ResetToken](reset-token.md) | `reset_token` | single-use password-reset tokens. |
| [Invitation](invitation.md) | `invitation` | a pending offer for someone to join a tenant with a set of roles. Implements X-7. |
| [PlatformRole](platform-role.md) | `platform_role` | platform-level staff roles that sit outside any tenant. Implements X-8. |
