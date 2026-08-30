---
name: legacy-equivalence-test-generator
description: Generates a behavior-based test suite from a legacy code snippet so that a rewritten/modernized version can be proven equivalent to the original, rather than just assumed correct. Use this skill whenever the user is modernizing, refactoring, migrating, rewriting, or upgrading legacy code (e.g. old JavaScript/jQuery to TypeScript, Python 2 to Python 3, an old framework to a new one) and needs to verify the new version behaves identically to the old one. Also use whenever the user asks to "prove," "verify," or "check" that a code rewrite didn't break anything, or wants test cases derived directly from existing code's actual behavior rather than from a spec. Trigger this even if the user just says "make sure this refactor is safe" or "generate tests for this old function" without mentioning equivalence explicitly.
---

# Legacy Equivalence Test Generator

A skill for generating a test suite that proves behavioral equivalence between an original (legacy) code snippet and a modernized rewrite of it — turning "trust me, it's the same" into a verifiable, runnable result.

## Why this exists

Most AI-assisted code modernization stops at "here's the rewritten code, hope it's right." This skill exists to close that trust gap: instead of generating tests from a spec or from guesswork, it derives test cases **directly from the legacy code's own observable behavior**, so the same tests can then be run against both the original and the modernized version to confirm they agree.

## When to use this skill

Use this skill whenever:
- A user is rewriting, refactoring, or migrating existing code and wants confidence the behavior didn't change.
- A user explicitly asks to "prove," "verify," or "check" equivalence between two versions of code.
- A user wants tests generated from an existing function's real behavior rather than from a written spec.
- A user is modernizing a legacy codebase (old JS/jQuery, Python 2, old framework code, etc.) and needs a safety net before or after the rewrite.

Do **not** use this skill for generating tests from an API specification (OpenAPI/Postman) or for testing genuinely new code with no prior version to compare against — those are different tasks.

## Process

### Step 1 — Analyze the legacy code

Read the provided snippet and identify:
- The function name(s) and signature(s) (parameter count, apparent types).
- Whether it's a **pure function** (output depends only on inputs, no side effects) or **impure** (touches `document`, `window`, network, timers, randomness, global mutable state).
- Any implicit behavior worth testing: type coercion, default/undefined handling, error-throwing conditions, edge-case branches (e.g. empty arrays, zero, negative numbers, null/undefined).

If the code is impure, don't fail — flag it. Note which parts are safely testable (the pure logic) and which parts would need mocking to test (side effects), and generate tests only for what's safely, deterministically testable.

### Step 2 — Generate representative test cases

Produce test cases covering, at minimum:
1. **Typical/happy path** — normal expected inputs.
2. **Boundary conditions** — empty input, zero, negative numbers, very large values, single-element vs multi-element collections.
3. **Edge cases specific to the code's own logic** — e.g. if there's a conditional branch, make sure at least one test exercises each branch.
4. **Invalid/unexpected input handling** — what does the original code actually do (not what it "should" do) when given the wrong type or a missing argument? Capture that real behavior, don't idealize it.

Each test case must be **deterministic** — no reliance on current time, randomness, or external state, unless that dependency is explicitly mocked/fixed as part of the test itself.

### Step 3 — Determine expected outputs by tracing the original code

For each test case, the `expected` value must come from actually tracing/reasoning through the **original legacy code's** logic — not from assumptions about what the "correct" behavior should be. The goal is behavioral equivalence, not correctness grading. If the legacy code has a bug, the test should capture the bug's actual output, and that should be flagged as a warning rather than silently corrected.

### Step 4 — Output in the standard schema

Return test cases in this structure (matches the LegacyProof `contract.md` schema so it plugs directly into a frontend/backend pipeline without translation):

```json
{
  "function_name": "string",
  "tests": [
    {
      "id": "test-1",
      "description": "short human-readable description of what this test checks",
      "args": ["positional arguments to call the function with"],
      "expected": "the expected return value, traced from the original code"
    }
  ],
  "warnings": [
    "any caveats — e.g. impure code detected, bug preserved intentionally, ambiguous input handling"
  ]
}
```

### Step 5 — Self-check before returning

Before finalizing, verify:
- Every test's `args` and `expected` values are JSON-serializable (no functions, DOM nodes, or non-serializable objects) — this keeps the tests safe to run in a sandboxed environment (e.g. a browser Web Worker) with no special execution infra.
- No two tests are redundant (each should exercise a distinct behavior/branch).
- Aim for 4–8 tests for a typical single-function snippet — enough to be meaningful, not so many that the equivalence check becomes slow or noisy in a live demo setting.

## Example

**Input (legacy code):**
```javascript
function calculateDiscount(price, isMember) {
  if (price < 0) return 0;
  var discount = isMember ? 0.2 : 0.1;
  return price - (price * discount);
}
```

**Output:**
```json
{
  "function_name": "calculateDiscount",
  "tests": [
    { "id": "test-1", "description": "member gets 20% off a normal price", "args": [100, true], "expected": 80 },
    { "id": "test-2", "description": "non-member gets 10% off a normal price", "args": [100, false], "expected": 90 },
    { "id": "test-3", "description": "zero price returns zero regardless of membership", "args": [0, true], "expected": 0 },
    { "id": "test-4", "description": "negative price is clamped to zero (preserves original guard behavior)", "args": [-50, true], "expected": 0 },
    { "id": "test-5", "description": "member with fractional price rounds naturally via floating point", "args": [19.99, true], "expected": 15.992 }
  ],
  "warnings": []
}
```

## Guardrails

- Never silently "fix" a bug you notice in the legacy code while generating expected outputs — the point is equivalence with what exists, not correctness. Flag suspected bugs in `warnings` instead.
- Never generate a test whose expected value depends on non-deterministic behavior (`Date.now()`, `Math.random()`, network calls) without explicitly mocking that dependency and noting it in `warnings`.
- Keep test count proportional to code complexity — don't pad with redundant tests just to hit a number.

## Typical Integration Pattern

This skill is designed to plug into a pipeline like: legacy code in → this skill generates the equivalence test suite → tests are run against both the original and a modernized rewrite (e.g. in a sandboxed environment) → pass/fail results confirm behavioral equivalence.
