# Simplify the YAML encodings

Type: grilling
Label: wayfinder:grilling
Status: open
Blocked by: 01, 08

## Question

Which format-3 and status-1 encodings survive once ticket 08 has removed the
derivable data: media type aliases and `=` escapes, omitted defaults, `state`/
`value` wrappers on counts and metrics, numeric-id map keys, reason codes
(`source_validation` hides a same-tag conflict)? Target: a YAML file a person can
read without the spec.
