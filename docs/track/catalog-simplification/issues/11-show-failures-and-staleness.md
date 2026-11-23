# Show failures and staleness to users

Type: grilling
Label: wayfinder:grilling
Status: open
Blocked by: 06

## Question

What does a user see for an app whose last check failed, that has never
succeeded, or whose data is old, and what does the webpage's health view keep
from today's run summaries and statistics?

## Comments

November 23, 2026, from ticket 04: repository files get optional `failed_at`
and `failed_with` (present only while the latest attempt failed). This ticket
settles the `failed_with` code list (schema enum; `not_found`, `rate_limited`,
`too_large`, `invalid_response`, `other` are the starting guess) and what the
page says for each.
