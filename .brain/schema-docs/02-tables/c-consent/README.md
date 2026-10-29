[← Back to index](../../README.md)

# Group C: consent

| Table | SQL name | Purpose |
|---|---|---|
| [ConsentTextVersion](consent-text-version.md) | `consent_text_version` | the versioned wording of a consent form. A consent record points at the exact text the patient agreed to. Texts can be provided by the platform for every clinic, or written by a single clinic (decision D8). |
| [ConsentRecord](consent-record.md) | `consent_record` | the history of a patient's consents and withdrawals. Each row is either a **grant** or a **withdrawal** of an earlier grant. Implements requirements C-1 and C-3. |
