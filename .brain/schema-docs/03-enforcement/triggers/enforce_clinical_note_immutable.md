[← Trigger summary](README.md) · [← Back to index](../../README.md)

# enforce_clinical_note_immutable

| | |
|---|---|
| Table | ClinicalNote |
| Fires on | BEFORE UPDATE, BEFORE DELETE |
| Rule | Reject any UPDATE or DELETE once the row exists. The finalization check is implicit: rows are only inserted via the finalize path. |

## Explanation

A finalized note must never change. The trigger fires before every UPDATE or DELETE on the table and raises an error, so neither a bug in the application nor a direct statement from the runtime role can alter or remove a finalized note. Corrections are made by inserting an addendum row instead.

## Applies to

[ClinicalNote](../../02-tables/e-clinical-notes/clinical-note.md)

## Requirements for all triggers

Trigger declarations must be ENABLE ALWAYS, and the trigger functions must be owned by a role the runtime role does not belong to (D12). Migration tests must confirm each trigger survives fresh setup, upgrades, and restoration. See the [trigger summary](README.md).
