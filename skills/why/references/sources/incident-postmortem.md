# Incident & Postmortem Context

This is a cross-cutting angle, not a separate source. Use it when the target contains defensive behavior such as null checks, retries, timeouts, rate limits, feature flags, fallbacks, or egress guards.

Search available history, tickets, documents, discussions, incident records, logs, and error reports for:

- the target file, symbol, feature, or error string
- the dates around the change
- incident, outage, regression, postmortem, or action-item language

If you find an incident link, read the full record and look for the timeline, root cause, and action items that connect it to the code. A matching date or error is supporting evidence, not proof of causation; corroborate it with the commit, PR, or ticket when possible. If no incident source is available or nothing relevant appears, record that gap.
