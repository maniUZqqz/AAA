# UpMarket — Development Rules

Binding rules for every phase. Extracted from the Master Specification (`../ROADMAP.md`).

## The 15 Engineering Rules

1. Do not build the entire application in one response.
2. Do not generate huge amounts of code without testing.
3. Do not pretend an integration works when it has not been tested.
4. Do not replace real AI integration with fake responses (mocks are for tests only).
5. Do not hardcode model or workflow configuration.
6. Do not put heavy generation in HTTP request handlers.
7. Do not block Django while waiting for video generation.
8. Do not regenerate successful video segments unnecessarily.
9. Do not allow AI to invent transactional facts (price, stock, policies).
10. Do not break existing working code without a reason.
11. Do not move to the next phase until the current phase is verified.
12. Document important architectural decisions.
13. Every important service must have tests.
14. Every external dependency must have failure handling.
15. Prefer real working vertical slices over incomplete massive architecture.

## Per-Phase Working Procedure

1. Inspect the current repository and read relevant docs.
2. Determine what already exists; define exact scope.
3. Implement only the current phase.
4. Run migrations where needed.
5. Run backend tests; run frontend tests/build.
6. Perform integration verification against the real service (Ollama / ComfyUI / n8n / TTS as applicable).
7. Fix discovered problems.
8. Update documentation (these files).
9. Report and stop — do not start the next phase without explicit instruction.

## Phase Completion Criteria

A phase is **not** complete because code compiles, the server starts, the frontend renders, an endpoint returns 200, or a mocked response appears.

A phase is complete only when the functionality actually works:
- Ollama: the real local model was called.
- ComfyUI: a real workflow was submitted and a real output retrieved.
- Video: a real generated segment was processed.
- TTS: a real audio file was produced.
- n8n: a real test webhook was delivered.

## Required Report After Each Phase

```
## Completed            – what was actually implemented
## Files Changed        – important files
## Database Changes     – migrations/models
## Tests                – what ran, pass/fail
## Integration Verification – which real integrations were exercised
## Known Limitations    – honest list
## Run Instructions     – exact commands
## Next Phase           – named, but not started
```

## When Something Is Unknown

Inspect the environment, verify installed versions, adapt, and document the difference. Never fake compatibility, never invent API behavior.
