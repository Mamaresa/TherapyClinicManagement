# Backend

Django 5.2 + Django REST Framework on PostgreSQL 17. Python 3.13.

## Local setup (Windows PowerShell)

```powershell
docker compose up -d          # from the repository root; creates roles and the "clinic" database
cd backend
Copy-Item .env.example .env
..\venv\Scripts\python -m pip install -r requirements\dev.txt
$env:DJANGO_MIGRATE = "1"; ..\venv\Scripts\python manage.py migrate; Remove-Item Env:DJANGO_MIGRATE
..\venv\Scripts\python -m pytest
```

## Database roles

The app never connects as the owner of its tables. A table owner can bypass
privileges, disable triggers and alter tables, so two roles are used.

| Role | Used by | Can do |
|---|---|---|
| clinic_owner | `migrate` (with `DJANGO_MIGRATE=1`, reads `MIGRATION_DATABASE_URL`) and test-database creation | Owns the database, every table and the trigger function |
| clinic_app | The running app and the test suite (`DATABASE_URL`) | SELECT, INSERT, UPDATE only; owns nothing |

- Roles are created once per PostgreSQL cluster by `db/init/01-roles.sql`
  (docker-compose runs it automatically; change the passwords elsewhere).
- Privileges are granted by migrations, so every database, including the test
  database, gets the same rules: `apps/core/migrations/0001_*` sets the baseline
  (default privileges for future tables), and each app's security migration
  narrows its own tables.
- The runtime role has no DELETE (except `django_session`), no TRUNCATE, no
  TRIGGER and no CREATE on the schema. It cannot ALTER, DROP or disable
  triggers because it owns nothing.
- Append-only: `audit_event` (no UPDATE/DELETE privilege, plus `ENABLE ALWAYS`
  triggers using the shared `forbid_change()` function).
- History tables allow only the columns that may change:
  `clinical_assignment.ended_at`, `clinical_supervision.ended_at`,
  `tenant_membership.roles/ended_at`, `membership_grant.revoked_at`.
  Code must save these with `save(update_fields=[...])`.
- A new table automatically gets SELECT/INSERT/UPDATE for the runtime role.
  If it is append-only or history, revoke in that app's security migration.

## Tenant isolation

- The active tenant is chosen with `POST /api/v1/session/tenant/ {"tenant": id}`,
  checked against the user's active membership, and kept in the server session.
  Every request re-checks the membership and the tenant status.
- Tenant ids in request bodies, headers or query strings are ignored.
- Every view over a tenant-owned model starts with `TenantScopedMixin`
  (`apps/accounts/tenancy.py`): it filters querysets by the active tenant and
  sets the tenant on create. Foreign keys sent by clients use
  `TenantScopedRelatedField`. Another tenant's ids therefore return 404 / 400.
- `tests/test_tenant_isolation.py` fails if a new routed view over a
  tenant-owned model skips the mixin or exposes `tenant` as a field.

## Who may change access

| Operation | Allowed for | Always denied |
|---|---|---|
| Change roles (`PATCH /memberships/{id}/`) | owner_admin | Changing your own membership |
| Grant / revoke (`/grants/`) | owner_admin | Grants on your own membership |
| Assign therapist (`/assignments/`) | owner_admin; target must hold the therapist role | Anyone else, including self-assignment |
| Clinical supervision (`/supervisions/`) | owner_admin; target must hold clinical_supervisor and the therapist must be assigned to the patient | Anyone else; supervising your own case |

Every success and every denial of these operations writes an `audit_event`.
Denials are written before any transaction starts, so they survive the failed
request. An owner_admin who also holds the therapist role (a solo
practitioner) may assign themselves; the audit event marks it
`self_assignment: true`.

Serializers list fields explicitly. Tenant, user, author, timestamps and status
fields are read-only and set by the server.

## Clinical supervision

`clinical_supervision` is the only source of truth. `clinical_assignment` has
no supervisor column.

## Tests

`pytest` creates a test database as `clinic_owner`, runs migrations, then runs
every test connected as `clinic_app`, so tests see production privileges.
