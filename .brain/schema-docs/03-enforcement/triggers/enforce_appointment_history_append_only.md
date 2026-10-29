[← Trigger summary](README.md) · [← Back to index](../../README.md)

# enforce_appointment_history_append_only

| | |
|---|---|
| Table | AppointmentHistory |
| Fires on | BEFORE UPDATE, BEFORE DELETE |
| Rule | Reject UPDATE and DELETE. |

## Explanation

The change log of appointments is evidence of who changed what. The trigger rejects every UPDATE and DELETE, so history rows can only be added.

## Applies to

[AppointmentHistory](../../02-tables/d-appointments/appointment-history.md)

## Requirements for all triggers

Trigger declarations must be ENABLE ALWAYS, and the trigger functions must be owned by a role the runtime role does not belong to (D12). Migration tests must confirm each trigger survives fresh setup, upgrades, and restoration. See the [trigger summary](README.md).
