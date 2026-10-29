[← Back to index](../README.md)

# Enforced at application level only

These cannot be enforced in the database, or are deliberately kept out of the schema because the enforcement logic is per-request.

| Rule | Why application-level | Where it must be tested |
|---|---|---|
| Access predicate: user active, tenant active, membership active, grant or role present, patient state allows the operation, specific access path (assignment, supervision, authored view, operational scope) authorizes this data | Depends on the session, the request context, and the state of multiple rows; a single SQL expression would duplicate every authorization rule | Every protected endpoint |
| Authored-records view: minimum identifying fields, no unrelated data | The rule is a scope on a query, and a filtered version of another endpoint would leak | The authored-records view's serializer and tests |
| File download authorization | Every request, against the PatientFile record, not the storage key | The download endpoint |
| Invitation response must not reveal account existence | Depends on the response shape, not on a row | The invitation flow |
| Password hashing, token hashing | Must never touch the database in plaintext | Auth endpoints |
| Rate limiting on login and recovery | Depends on request frequency, not row state | Auth middleware |
| Audit-event write coupling to the audited action | Fail-closed requires the write and the action in one transaction | Every audited write and audited read |
| Persian normalization of email and names | The normalization function is code, not a stored procedure | Every write of email, first_name, last_name; every search |
| Contact field encryption and decryption | Key management is outside the schema | Every write and read of encrypted columns |
| Metadata scrubbing for AuditEvent | Would require a JSON validator in a trigger; code review is more reliable | The audit write path |
| Draft locking on reassignment | Cross-row state transition | The reassignment workflow |
| Session revocation on deactivation | A workflow that updates Session.revoked_at and Application state | The deactivation workflow |
| Timezone consistency in future re-interpretation | Depends on the intended deployment policy | Documented separately |
| The client-supplied tenant ID is not authorization evidence | Must be rejected in the request handler, not in SQL | Every tenant-scoped endpoint |

**Why this list matters:** each row is a place where a database-level guarantee does **not** exist. If the application code for one of these is wrong or skipped, nothing in PostgreSQL will catch it, which is why the third column names where each rule must be tested.

---

[← Enforcement summary](README.md)
