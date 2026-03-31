# Person 1: The System Architect (Nikola Kriznar)
**Focus:** Infrastructure and Connectivity

This document outlines the system boundaries, environmental setup, and entry points for the Tall Ships Halifax ticketing platform, as defined by the System Architect.

---

## 1. Threat Model Information
**Application Name:** Tall Ships Halifax – Event Ticketing & Tour Booking Platform  
**Application Version:** 1.0 (Based on OWASP Juice Shop v19.2.1)  
**Description:** Tall Ships Halifax is a stateful ticketing platform designed to manage harbour cruises, tall ship tours, and summer events. Built on the Juice Shop architecture (Angular SPA, Node.js/Express, JWT, SQLite), this platform manages complex business workflows including ticket reservations, payments, transfers, and refunds. Unlike a simple retail checkout, this application must enforce strict state transitions and capacity constraints for every maritime event.  
**Document Owner:** Nikola Kriznar  
**Participants:** Person 1 (System Architect), Nikola Kriznar  
**Reviewer:** NSCC Cybersecurity Faculty  

---

## 2. External Dependencies
| ID | Description |
| :--- | :--- |
| 1 | **Node.js Environment**: Hosted on NSCC Halifax Campus production-grade Linux servers. |
| 2 | **SQLite Database**: Persists ticket states, event capacities, and promotional rules at `/var/lib/tallships/db/ticketing.sqlite`. |
| 3 | **Payment Gateway**: Fictional external API for processing ticket payments (TLS 1.3 encrypted). |
| 4 | **NSCC SMTP Relay**: Primary exit point for sending digital tickets and refund confirmations to user emails. |
| 5 | **Infrastructure**: The system sits behind a campus-wide firewall with TLS termination at the load balancer. |

---

## 3. Entry Points
| ID | Name | Description | Trust Levels |
| :--- | :--- | :--- | :--- |
| 1 | Web Gateway (HTTPS) | The primary TLS-secured entry point for all browser-based traffic. | (1), (2), (4), (5) |
| 1.1 | Event Browsing | Publicly accessible catalog of available harbour cruises and ship tours. | (1), (2) |
| 1.2 | Reservation API | Stateful endpoint that moves a ticket from `AVAILABLE` to `RESERVED` for a user. | (2) |
| 1.3 | Payment Endpoint | Accepts payment confirmation and triggers the transition from `RESERVED` to `PAID`. | (2), (5) |
| 1.4 | Ticket Transfer | Logic allowing a user to move a `PAID` ticket to another user's account. | (2) |
| 1.5 | Refund Request | Endpoint for customers to request a `REFUNDED` state for their `PAID` tickets. | (2) |
| 1.6 | Staff Check-in | Mobile-optimized interface for on-site staff to mark tickets as `USED`. | (4) |
