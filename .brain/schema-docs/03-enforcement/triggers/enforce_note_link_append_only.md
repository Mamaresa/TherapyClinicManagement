[← Trigger summary](README.md) · [← Back to index](../../README.md)

# enforce_note_link_append_only

| | |
|---|---|
| Table | NoteAppointmentLink |
| Fires on | BEFORE UPDATE, BEFORE DELETE |
| Rule | Allow only setting removed_at and removed_by_membership_id once, from NULL to a value. Reject DELETE. |

## Explanation

The note-to-appointment link is the one mutable structure around notes, but only in a controlled way: a link can be marked removed (both removal columns set once, from NULL to a value). Anything else is rejected, and rows can never be deleted.

## Applies to

[NoteAppointmentLink](../../02-tables/e-clinical-notes/note-appointment-link.md)

## Requirements for all triggers

Trigger declarations must be ENABLE ALWAYS, and the trigger functions must be owned by a role the runtime role does not belong to (D12). Migration tests must confirm each trigger survives fresh setup, upgrades, and restoration. See the [trigger summary](README.md).
