[← Trigger summary](README.md) · [← Back to index](../../README.md)

# enforce_appointment_utc_local_consistency

| | |
|---|---|
| Table | Appointment |
| Fires on | BEFORE INSERT, BEFORE UPDATE |
| Rule | Verify that starts_at_utc equals the local_start_date + local_start_time interpreted in local_timezone, and ends_at_utc equals starts_at_utc + the intended duration. Uses the tz database; not a CHECK because zone conversion is not immutable. |

## Explanation

The UTC instants and the local date, time and time zone describe the same moment. Converting through a time zone is not an immutable operation, so this cannot be a CHECK constraint. The trigger recomputes the conversion using the tz database and rejects mismatches.

## Applies to

[Appointment](../../02-tables/d-appointments/appointment.md)

## Requirements for all triggers

Trigger declarations must be ENABLE ALWAYS, and the trigger functions must be owned by a role the runtime role does not belong to (D12). Migration tests must confirm each trigger survives fresh setup, upgrades, and restoration. See the [trigger summary](README.md).
