[← Trigger summary](README.md) · [← Back to index](../../README.md)

# enforce_assignment_ended_once

| | |
|---|---|
| Table | ClinicalAssignment |
| Fires on | BEFORE UPDATE |
| Rule | Allow only a single transition: ended_at from NULL to a non-null value. Reject any other UPDATE. |

## Explanation

Assignments are history. The only permitted change to an existing row is ending it, which means setting ended_at once from NULL to a value. Reassignment is done by ending the old row and inserting a new one.

## Applies to

[ClinicalAssignment](../../02-tables/b-patients-assignments/clinical-assignment.md)

## Requirements for all triggers

Trigger declarations must be ENABLE ALWAYS, and the trigger functions must be owned by a role the runtime role does not belong to (D12). Migration tests must confirm each trigger survives fresh setup, upgrades, and restoration. See the [trigger summary](README.md).
