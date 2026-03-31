# 5512-Threat-Modeling-Assignment
MCDA 5512 - Current Practices II - Cybersecurity

This repository contains our threat modeling work for **Tall Ships Halifax**, a **stateful ticketing system** based on the OWASP Juice Shop architecture.

## What We Built / Modeled
- **Architecture baseline**: Angular SPA frontend, Node.js/Express backend APIs, JWT authentication, and SQLite persistence.
- **Stateful ticketing workflows**: Ticket lifecycle is a core security requirement and is modeled as **Ticket State Integrity** with controlled transitions (Available → Reserved → Paid → Used, with refunds handled via state reversal).

## Threat Modeling Work Completed
- **System boundary + entry points**: Documented primary entry points (public browsing, reservation, payment, transfer/refund, staff check-in) and the associated trust assumptions.
- **Exit points**: Identified where sensitive data leaves the trust boundary (email delivery, payment gateway calls, API error responses, browser storage).
- **Assets and trust levels**: Enumerated key assets (tickets, ticket state, payments, auth tokens, accounts, capacity, logs, infrastructure) and the interacting entities (guest/customer/staff/admin, backend, database, external payment, JWT mechanism, SPA, hosting).
- **STRIDE analysis**: Mapped primary spoofing/tampering/repudiation/info-disclosure/DoS/elevation threats to affected assets and mitigations, with emphasis on workflow abuse (payment bypass, reservation flooding, check-in misuse).

## Key Emphasis
Because the platform is stateful, the highest risks are **business logic and state-transition abuse** (not just traditional injection-style issues). The threat model prioritizes server-side enforcement of state transitions, capacity constraints, and role-based access control for staff/admin actions.
