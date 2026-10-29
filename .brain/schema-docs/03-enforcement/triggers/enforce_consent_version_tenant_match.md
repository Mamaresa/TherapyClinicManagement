[← Trigger summary](README.md) · [← Back to index](../../README.md)

# enforce_consent_version_tenant_match

| | |
|---|---|
| Table | ConsentRecord |
| Fires on | BEFORE INSERT |
| Rule | Verify that the referenced consent_text_version has tenant_id NULL or equal to the record's tenant_id. |

## Explanation

consent_record references consent_text_version with a plain foreign key, because platform-provided texts (tenant_id NULL) must be usable by every clinic. The trigger restores the missing check: the text must be global or belong to the same tenant as the record.

## Applies to

[ConsentRecord](../../02-tables/c-consent/consent-record.md)

## Requirements for all triggers

Trigger declarations must be ENABLE ALWAYS, and the trigger functions must be owned by a role the runtime role does not belong to (D12). Migration tests must confirm each trigger survives fresh setup, upgrades, and restoration. See the [trigger summary](README.md).
