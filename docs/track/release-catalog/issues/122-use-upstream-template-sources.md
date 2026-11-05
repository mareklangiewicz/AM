# Use upstream template sources and family naming

Type: task
Status: claimed
Triage: ready-for-agent

Marek requested removing the app-specific template name and reusing upstream's
own template/generator guidance where possible, avoiding a second maintained
recipe body. Rename the family, pin the actual upstream template that produces
the supported fixtures, and use that unmodified source. Record generator
substitutions and provenance, verify byte-exact behavior, and explain how newer
upstream templates are reviewed. Do not silently treat legacy and current
upstream layouts as equivalent. No runtime, conversion or collection changes.
