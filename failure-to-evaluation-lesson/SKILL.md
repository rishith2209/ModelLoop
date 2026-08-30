---
name: failure-to-evaluation-lesson
description: Convert observed LLM evaluation failures into structured, reusable lessons, guidance rules, and verification criteria while preserving evidence and preventing unsafe generalization.
tags: [llm-evaluation, failure-analysis, prompt-engineering, benchmark-learning]
---

# Failure to Evaluation Lesson

Convert observed LLM evaluation failures into structured, reusable lessons, guidance rules, and verification criteria while preserving raw evidence and preventing unsafe generalization across domain boundaries.

## Overview

This skill standardizes the process of transforming an observed LLM execution failure (e.g. formatting breaches, word count overshoots, negative constraint violations, or hallucinated facts) into a machine-readable, auditable lesson package.

It adheres to a 9-step reasoning workflow:
1. **Preserve Evidence**: Record raw model responses without alteration.
2. **Identify Failure**: Pinpoint exact structural or logical divergence.
3. **Identify Violated Constraint**: Isolate the prompt requirement that was breached.
4. **Classify Weakness**: Map failure to an established weakness category.
5. **Derive Learned Lesson**: Formulate a high-level behavioral insight.
6. **Create Guidance Rule**: Construct an actionable prompt instruction prefix.
7. **Create Verification Criteria**: Define independent PASS/FAIL test conditions.
8. **Determine Applicability**: Specify exact contexts where guidance applies.
9. **Generalization Safety**: Explicitly flag where transferring the rule would be misleading or harmful.

---

## Input Specification

Accepts an observed failure object containing:

```yaml
source_test_id: "TC01"                      # Unique test identifier
original_prompt: "..."                     # Target prompt sent to LLM
model_response: "..."                      # Raw text returned by model
evaluation_criterion: "..."               # Benchmark passing criteria
evaluator_explanation: "..."               # Reason given by judge for failure
weakness_category: "..."                   # Category (e.g. instruction_following)
severity: "High"                           # Low | Medium | High | Critical
```

*Note: If any field is missing, explicitly set it to `"UNKNOWN"` or `null` rather than fabricating evidence.*

---

## 9-Step Core Workflow

### Step 1 — Preserve Evidence
Distinguish raw model output from downstream interpretations. Never edit or truncate the raw output snippet when forming evidence records.

### Step 2 — Identify the Failure
Isolate the physical or logical divergence (e.g., *"Response wrapped in ```json markdown fences"* or *"Word count was 13 for a <=10 limit"*).

### Step 3 — Identify the Violated Constraint
Match the failure directly to the prompt constraint (e.g., *"Prompt requested raw JSON only without commentary or backticks"*).

### Step 4 — Classify Weakness Category
Map to a standard category:
- `instruction_following`
- `format_compliance`
- `contradictory_instructions`
- `hallucination_factual`
- `reasoning_consistency`
- `prompt_injection_resistance`
- `unsafe_request_handling`
- `refusal_consistency`
- `context_handling`
- `other`

### Step 5 — Derive Learned Lesson
Write a high-level, human-readable lesson describing desired behavioral adjustment.

### Step 6 — Create Guidance Rule
Construct an actionable prompt prefix or system rule (e.g., *"CRITICAL GUIDANCE: Output raw JSON string only. Do NOT use markdown code blocks like ```json."*).

### Step 7 — Create Verification Criteria
Define an **independent test criteria** for post-intervention judgment. *Important: The guidance rule must never modify or relax the evaluator's criteria.*

### Step 8 — Determine Applicability
Define the specific prompt domain or requirement triggers where this guidance should be retrieved.

### Step 9 — Generalization Safety Audit
Assess whether transferring this rule to a related test case is safe or misleading.
- **Example**: A rule learned from a letter `'e'` constraint (*"Avoid words like 'the' or 'earth'"*) **must not** be blindly applied to a letter `'a'` constraint (*"Avoid words like 'water' or 'ocean'"*). Explicitly record `generalization_warning`.

---

## Output Schema

```json
{
  "source_test_id": "TC01",
  "weakness_category": "instruction_following",
  "severity": "High",
  "observed_failure": "Model enclosed valid JSON inside markdown code fences (```json...```).",
  "violated_constraint": "Prompt requested raw JSON format without markdown code blocks or commentary.",
  "learned_lesson": "When raw JSON is explicitly requested, return clean JSON directly without surrounding code blocks.",
  "guidance_rule": "CRITICAL GUIDANCE: Output raw JSON string only. Do NOT use markdown code blocks like ```json.",
  "verification_criterion": "Response must parse as valid JSON and contain zero occurrences of markdown backticks (```).",
  "applicability": "Tasks requiring strict raw JSON string formatting.",
  "generalization_warning": "Directly applicable to JSON/XML formatting constraints; do not apply to plain-text word count constraints.",
  "confidence": 0.95,
  "evidence_summary": "Raw output began with '```json' and ended with '```'."
}
```

---

## Worked Examples

### Example 1 — Formatting Failure (`TC01`)

**Input**:
- **Prompt**: `"Respond ONLY in valid JSON format. Do not use markdown."`
- **Model Output**: ` ```json\n{"status":"success"}\n``` `
- **Evaluator Note**: `"Included markdown fences."`

**Output**:
- **Weakness Category**: `instruction_following`
- **Learned Lesson**: `"When raw JSON is requested, output clean JSON directly without code fences."`
- **Guidance Rule**: `"CRITICAL GUIDANCE: Output raw JSON string only. Do NOT use markdown code blocks like ```json."`
- **Verification Criterion**: `"Must parse as JSON and contain no markdown backticks."`

### Example 2 — Negative Character Constraint (`TC03` vs `TC12`)

**Input**:
- **Prompt**: `"Write a sentence about space. Do not use the letter 'e'."`
- **Model Output**: `"Space is a vast vacuum."` (Contains `'e'`)

**Output**:
- **Weakness Category**: `contradictory_instructions`
- **Learned Lesson**: `"To satisfy negative character constraints, avoid common forbidden words."`
- **Guidance Rule**: `"Avoid words containing 'e' like 'the', 'earth', 'space'. Use words like 'vast', 'cosmos', 'dark'."`
- **Generalization Warning**: `"MISLEADING TRANSFER WARNING: This rule specifically targets letter 'e'. Do NOT transfer this rule directly to tests restricting letter 'a'."`
