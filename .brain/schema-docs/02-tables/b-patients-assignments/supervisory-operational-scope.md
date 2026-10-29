[← Back to index](../../README.md)

# SupervisoryOperationalScope

> `supervisory_operational_scope` · Group B: patients, assignments, supervision

**Purpose:** gives a supervisor **operational** oversight (demographics, appointments) over a supervisee's patients, without clinical access (D9, X-4 part 2).

```sql
CREATE TABLE supervisory_operational_scope (
    id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id                UUID NOT NULL,
    supervisor_membership_id UUID NOT NULL,
    supervisee_membership_id UUID NOT NULL,
    started_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at                 TIMESTAMPTZ,
    CONSTRAINT fk_sos_supervisor
        FOREIGN KEY (supervisor_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT fk_sos_supervisee
        FOREIGN KEY (supervisee_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT ck_sos_no_self CHECK (supervisor_membership_id <> supervisee_membership_id),
    CONSTRAINT ck_sos_dates CHECK (ended_at IS NULL OR ended_at >= started_at),
    CONSTRAINT uq_sos_id_tenant UNIQUE (id, tenant_id)
);
CREATE UNIQUE INDEX uq_sos_active_pair
    ON supervisory_operational_scope (supervisor_membership_id, supervisee_membership_id)
    WHERE ended_at IS NULL;
```

**Design notes**

- It is tied to a **person** (the supervisee), not to a patient.
- The line between "operational" and "clinical" lives in the **access predicate**, not the schema. The tables only record the relationships.
- `ck_sos_no_self` prevents someone supervising themselves.
- `uq_sos_active_pair` prevents duplicate active relationships.

**ClinicalSupervision vs SupervisoryOperationalScope**

| | ClinicalSupervision | SupervisoryOperationalScope |
|---|---|---|
| Granularity | One patient | One supervisee (all their patients) |
| Access type | Clinical content | Operational data only |
| Key columns | supervisor, patient, therapist | supervisor, supervisee |
| Self-check | No | Yes |

## Relationships

**Depends on (this table references):** [TenantMembership](../a-tenancy-identity/tenant-membership.md)

**Referenced by:** no table

## Triggers on this table

None.

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[← ClinicalSupervision](clinical-supervision.md) · [Group overview](README.md)
