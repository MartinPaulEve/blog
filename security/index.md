---
layout: page
title: Security & Responsible Disclosure
tags: [security]
comments: false
---

This is a small, static personal website. There are no user accounts, no databases and no forms, so there is very little to attack and almost no personal data at stake. The only data the server holds is minimal request logs (such as IP addresses and requested URLs), kept briefly for operational reasons. I still take security seriously, and this page sets out how I handle incidents and how you can report a problem to me.

## Reporting a vulnerability

If you have found a security issue with this site or its infrastructure, please email me at [martin@eve.gd](mailto:martin@eve.gd). You can also confirm the current contact details in the machine-readable [security.txt](/.well-known/security.txt) file.

Please act in good faith: give me a reasonable chance to investigate and fix the issue before you disclose it publicly, avoid accessing or modifying data that is not yours, and do not run tests that could degrade the service for others. I will acknowledge your report within 5 working days, keep you updated on progress, and let you know once the issue is resolved.

There is no paid bug bounty for this personal site. However, if you report a genuine issue in good faith, I will happily credit you by name (or a handle of your choosing) once the matter is fixed, if you would like me to.

## Incident response

Because the site is static and served over HTTPS via Caddy, most protection comes from a small, well-understood configuration: HTTP Strict Transport Security, a Content-Security-Policy, and the `X-Content-Type-Options`, `X-Frame-Options` and `Referrer-Policy` headers. I detect problems through routine review of server logs, monitoring of the hosting platform, and reports from users and researchers. When something needs fixing, I update the site content or server configuration and redeploy.

If a significant security incident is ever confirmed, I commit to notifying affected people publicly within 72 hours of confirming it. That notice will appear as a note on this website and, where I hold suitable contact details and direct contact is appropriate, I will also reach out to affected individuals directly. The notice will explain what happened, what data (if any) was involved, and what steps I have taken in response.

Last reviewed: July 2026
