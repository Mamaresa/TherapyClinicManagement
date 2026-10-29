[← Back to index](../README.md)

# Constraint enforcement summary

This section answers one question for every rule in the design: **who enforces it?** There are four possible answers: PostgreSQL itself through declarative DDL (16.1), a trigger (16.2), the application (16.3), or nobody, as a documented limitation (16.4).

## Contents

- [Enforced declaratively by PostgreSQL (DDL)](declarative-constraints.md)
- [Enforced by trigger](triggers/README.md)
- [Enforced at application level only](application-level-rules.md)
- [Not enforced anywhere (documented limitations)](documented-limitations.md)

Every table page also lists its own triggers under "Triggers on this table".
