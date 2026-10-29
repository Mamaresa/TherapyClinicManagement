[← Back to index](../README.md)

# Review notes on Part 1 and open points

These are observations on the text of Part 1 itself. They are for the operator's consideration and do not change the design above.

1. **Redundant index.** `ix_user_email_norm` duplicates the index PostgreSQL already creates for `uq_user_email_norm`. It can be dropped.
2. **No-op CHECK.** `ck_platform_role_no_membership CHECK (TRUE)` enforces nothing. Consider removing it and relying on a SQL comment.
3. **Empty arrays.** In `tenant_membership.roles`, `array_length('{}', 1)` returns `NULL`, and a CHECK evaluating to `NULL` passes. An empty array may therefore slip through. `cardinality(roles) >= 1` rejects it. The same gap applies to `invitation.role_set`, which has no minimum-length check at all.
4. **Duplicate array elements.** `<@` accepts `{therapist,therapist}`. Nothing prevents repeated role codes.
5. **Session tenant link.** `session.tenant_context_id` is not tied to the user's membership, so the access predicate must verify it.
6. **"Exactly one" primary.** `uq_ca_one_active_primary` enforces "at most one". "At least one" cannot be a simple constraint and needs application or deferred-trigger logic.
7. **Unused key.** `uq_ca_id_patient_tenant` is not referenced by any table yet.
8. **Part 2 dependency (now resolved).** `consent_record`, `appointment`, notes, treatment, assessment, file and audit tables were not in the Part 1 message. They are now defined in [the per-table files](../02-tables/README.md).
