# RAG ingress rate-limit runbook — reviewed 12 November 2026

## Decision

The code has request-size, output-token, timeout, and per-function-instance limits. Those do not provide a shared budget across serverless instances. Vercel's WAF can add an edge-side fixed-window rule for the RAG endpoint, but it is not configured or verified for this project. This file is a preparation guide, not proof of a live control.

## Gemini spend controls are not a hard zero-overrun guarantee

Official Google AI Studio billing documentation checked on 12 November 2026 says project-level monthly spend caps are **experimental** and can overrun during roughly ten minutes of billing-processing latency. Long-running work can also exceed a project cap. Billing-account tier caps aggregate Gemini API usage across linked projects, so one project's activity can consume capacity shared with other projects. API keys inherit their project's billing state; a key is not an independent budget boundary. Under Prepay, reaching a zero balance stops Gemini API keys across linked projects, but Google still documents possible overage during the processing delay. The monthly auto-charge limit applies to automatic reloads and does not count manually initiated one-time purchases. These controls therefore do not justify promising an exact maximum charge or zero overspend.

Before enabling RAG, the authorized owner must inspect the exact API-key project and linked billing account, current billing mode and tier, project spend cap (if available), linked-project aggregation, existing auto-reload/payment settings, and usage alerts. Record only redacted settings and the owner's chosen budget; do not store keys, payment data, account identifiers, or billing screenshots here. Do not enable auto-reload, make a purchase, change a billing account, or claim a budget cap was verified without explicit owner action. If the account/budget cannot be verified, keep RAG Production closed. Evidence review: `evidence/rag-gemini-billing-controls-review-2026-11-12.json`.

As checked on 12 November 2026, Vercel documents WAF rate limiting on all plans. Hobby and Pro support fixed-window rules with IP and JA4 digest keys; counters are per region, so requests from multiple regions can exceed the configured per-region threshold. The current rate-limit page lists one million included allowed requests for Hobby and usage-based billing for Pro; it lists $0.50 per million allowed requests. The separate usage page says WAF-denied, challenged, or rate-limited requests do not incur CDN Request/Fast Data Transfer charges. That waiver does not waive the rate-limiting feature's allowed-request charge, and neither rule nor waiver caps Gemini provider spend. Check the project's actual plan, quota, billing settings, region exposure, and current pricing dialog before enabling a rule. Do not infer that this project has a free allowance or that the rule is a global hard cap. Sources: [Vercel WAF Rate Limiting](https://vercel.com/docs/vercel-firewall/vercel-waf/rate-limiting), [Vercel WAF usage and pricing](https://vercel.com/docs/vercel-firewall/vercel-waf/usage-and-pricing), and [Firewall-mitigated traffic billing update](https://vercel.com/changelog/web-application-firewall-mitigated-traffic-is-free-on-vercel).

## Proposed rule, pending owner decision

In Vercel Dashboard, select the TamsoodBase project, then **Firewall → Configure → New Rule**. Scope it to the exact `POST /api/rag/ask` path and, if the rule editor offers it, the intended project hostname. Select **Rate Limit → Fixed Window**, key by source IP (JA4 can be an additional supported key on Hobby/Pro), and use HTTP 429 for excess requests. Do not use the default 100 requests/minute without a budget review; select a limit that fits an explicitly agreed demo traffic pattern and the Google AI project quota. A 60-second window is available, but fixed windows may allow a burst on both sides of a window boundary.

Before enforcement, the owner may use **Log** to observe the intended match. Logging does not block traffic and does not substitute for a rate limit. Review the cost dialog and the proposed rule scope before publishing. Publishing applies a Production firewall configuration immediately; it is deliberately left to an authorized project owner. No dashboard change was made while preparing this runbook.

## Verification evidence required before treating the gate as passed

1. Record the project plan, rule ID/name, exact method/path/host conditions, key, time window, threshold, action, pricing acknowledgement, and owner decision. Do not save secret values or personal IP addresses in the repository.
2. Exercise the rule against a non-production deployment first if available. Confirm a normal question remains usable and over-limit requests receive 429 at the edge before the Gemini function runs.
3. Inspect Vercel Firewall events/analytics to verify the rule matched the intended route and did not throttle unrelated website routes. Save a redacted rule summary and counts, not visitor identifiers.
4. Confirm Google AI quota/budget alerts and Vercel spend notifications separately. A WAF rule is not a global spend cap and does not replace provider quotas, privacy approval, rights clearance, or human evaluation.
5. Record the rollback version and owner who can restore the prior Firewall configuration. Vercel documents restoring a prior version through the Firewall audit log; test this only with project-owner approval.

## Current status

- Configuration: **NOT VERIFIED / NOT CONFIGURED BY THIS WORK**.
- Production RAG: **HOLD**.
- Human action: project owner must check the project's plan/billing and decide whether to configure the rule; no threshold or spend approval is assumed.

## Preview client-IP header review — 10 November 2026

The Preview function currently keys its in-memory limiter from the first address in `x-forwarded-for`. Vercel's request-header documentation says Vercel overwrites that header with the public client IP to prevent IP spoofing; it also documents `x-vercel-forwarded-for` as the equivalent Vercel header. This supports the current direct `*.vercel.app` Preview deployment's header choice, but this was a documentation review, not a live header probe. If a proxy is placed in front of Vercel, re-check which header is preserved before relying on it. The limiter still resets with function instances and has no global counter or spend budget, so this finding does not pass the abuse/cost gate. Source: [Vercel request headers](https://vercel.com/docs/headers/request-headers). Evidence: `evidence/rag-vercel-forwarded-for-review-2026-11-10.json`.

