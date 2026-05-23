# Handoffs

This folder is reserved for durable handoffs that a future thread should be able to execute directly.

Keep it clean:

- Add a handoff only when the work genuinely needs restart instructions, explicit gates, or cross-thread continuity.
- Prefer current roadmaps, ADRs, and user-facing docs for stable package truth.
- Remove completed or superseded handoffs once their durable decisions have been captured in the current source-of-truth docs.
- Do not use this folder for temporary notes, partial scratch plans, or generated logs.
