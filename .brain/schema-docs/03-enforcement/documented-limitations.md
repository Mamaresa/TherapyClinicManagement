[← Back to index](../README.md)

# Not enforced anywhere (documented limitations)

- Cross-clinic double-booking (D14): the exclusion constraint is per therapist_membership_id, which is per tenant. A therapist working in two clinics can be booked at overlapping times. Documented limitation, not a defect.
- Erasure of finalized note text (D13): no erasure path exists. If a lawful erasure request arrives, the operational fallback is retention with access restriction and demographic anonymization, pending legal input.
- Break-glass (D10): no break-glass path exists. If an emergency arises, the operational fallback is a documented manual procedure, not an application feature.
- A platform role cannot read clinical data: the schema allows the FK, but the access predicate forbids the query. Enforced at application level only.

---

[← Enforcement summary](README.md)
