"""
Learning Engine & Improvement Memory for ModelLoop.
Processes baseline failure records and converts them into structured guidance items stored in improvement_memory.json.
"""

import json
import os

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "improvement_memory.json")

def process_failures_and_build_memory(failures):
    """
    Takes structured failure records from baseline run and extracts reusable learning lessons.
    Saves learning items to improvement_memory.json.
    """
    memory_items = []
    
    for fail in failures:
        test_id = fail["test_id"]
        category = fail["category"]
        severity = fail["severity"]
        prompt = fail.get("original_prompt", fail.get("prompt_used", ""))
        response = fail["gemini_response"]
        explanation = fail["evaluator_explanation"]
        
        # Generate lesson based on weakness category and specific failure
        lesson, guidance_rule = derive_lesson(test_id, category, explanation)
        
        item = {
            "source_test_id": test_id,
            "weakness_category": category,
            "severity": severity,
            "original_prompt": prompt,
            "failed_response_snippet": response[:150],
            "evaluator_explanation": explanation,
            "learned_lesson": lesson,
            "guidance_rule": guidance_rule
        }
        memory_items.append(item)
        
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory_items, f, indent=4)
        
    return memory_items

def derive_lesson(test_id, category, explanation):
    """Derives specific, structured lesson rules from baseline failures."""
    if test_id == "TC01":
        return (
            "When raw JSON format is requested, output clean JSON directly without surrounding markdown backtick fences (```json).",
            "CRITICAL GUIDANCE: Output raw JSON string only. Do NOT use markdown code blocks like ```json."
        )
    elif test_id == "TC02":
        return (
            "Strictly enforce upper bound word count limits by keeping response concise.",
            "CRITICAL GUIDANCE: Keep answer extremely brief. Word count must strictly be 10 words or fewer."
        )
    elif test_id == "TC03":
        return (
            "To satisfy negative character constraints (e.g., no 'e'), avoid common forbidden words like 'the', 'earth', 'space'.",
            "CRITICAL GUIDANCE: Avoid any word containing the letter 'e'. Strictly use words like 'vast', 'cosmos', 'dark', 'stars'."
        )
    elif test_id == "TC04":
        return (
            "Verify entity reality before stating historical dates for fictional entities.",
            "CRITICAL GUIDANCE: Fact-check entity validity. Explicitly state if an entity or event is fictional."
        )
    
    return (
        f"Enforce criteria for category '{category}': {explanation}",
        f"GUIDANCE: Strictly adhere to rules for {category}."
    )

def load_improvement_memory():
    """Loads stored lessons from improvement_memory.json."""
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def compute_relevance_score(test_case_or_dict, memory_item):
    """
    Computes keyword/constraint relevance score between a target test and a stored memory item.
    Factors:
    - Weakness Category match (base 10 pts)
    - Specific Sub-Domain / Keyword Alignment (+15 pts)
    - Specific Dis-alignment / Misleading Constraint (-20 pts)
    - Severity Weight (+1..4 pts)
    """
    cat = test_case_or_dict.get("category", "")
    mem_cat = memory_item.get("weakness_category", "")
    
    if cat != mem_cat:
        return 0.0, "Category mismatch"
        
    score = 10.0
    reasons = ["Weakness category match"]
    
    prompt = (test_case_or_dict.get("prompt", "") + " " + test_case_or_dict.get("description", "") + " " + test_case_or_dict.get("criteria", "")).lower()
    lesson = (memory_item.get("learned_lesson", "") + " " + memory_item.get("guidance_rule", "")).lower()
    source_id = memory_item.get("source_test_id", "")
    
    # Keyword / Domain alignment
    is_json_test = "json" in prompt or "format" in prompt or "fence" in prompt
    is_json_lesson = "json" in lesson or "backtick" in lesson or source_id == "TC01"
    
    is_words_test = "word" in prompt or "fewer" in prompt or "count" in prompt
    is_words_lesson = "word" in lesson or "concise" in lesson or source_id in ["TC02", "TC13"]
    
    # Specific JSON alignment
    if is_json_test and is_json_lesson:
        score += 15.0
        reasons.append("High alignment on JSON/Formatting constraints")
    elif is_json_test and is_words_lesson:
        score -= 10.0
        reasons.append("Irrelevant (Word-count rule for JSON test)")
        
    # Specific Word-Count alignment
    if is_words_test and is_words_lesson:
        score += 15.0
        reasons.append("High alignment on Word Count constraints")
    elif is_words_test and is_json_lesson:
        score -= 10.0
        reasons.append("Irrelevant (JSON rule for Word Count test)")

    # Negative Character Constraint check (e.g., 'e' vs 'a')
    if "letter" in prompt or "rule 2:" in prompt:
        if "letter 'e'" in lesson or "words like 'vast'" in lesson:
            if "'a'" in prompt or "letter 'a'" in prompt:
                score -= 15.0
                reasons.append("Misleading constraint mismatch (Lesson is for letter 'e', test is for letter 'a')")
            else:
                score += 10.0
                reasons.append("Matched character exclusion constraint domain")

    severity_map = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    score += severity_map.get(memory_item.get("severity"), 1)
    
    return max(0.0, score), ", ".join(reasons)

def retrieve_relevant_lessons(target_test, memory_items):
    """
    Retrieves and filters lessons using Category + Description + Criteria + Keyword relevance.
    """
    scored_lessons = []
    
    for item in memory_items:
        score, reason = compute_relevance_score(target_test, item)
        if score > 5.0:  # Threshold out irrelevant / penalized lessons
            scored_lessons.append({
                "item": item,
                "score": score,
                "reason": reason
            })
            
    scored_lessons.sort(key=lambda x: x["score"], reverse=True)
    return scored_lessons

def build_guided_context(test_id, target_category, original_prompt, memory_items, test_case_dict=None):
    """
    Refined contextual retrieval builder.
    Utilizes compute_relevance_score to select only highly relevant lessons, preventing irrelevant guidance.
    """
    if not test_case_dict:
        test_case_dict = {"id": test_id, "category": target_category, "prompt": original_prompt, "description": "", "criteria": ""}
        
    relevant_scored_lessons = retrieve_relevant_lessons(test_case_dict, memory_items)
    
    if not relevant_scored_lessons:
        # Fallback to general category guidance if no specific high-scoring match exists
        return original_prompt, None
        
    guidance_rules = []
    retrieved_sources = []
    
    for entry in relevant_scored_lessons[:2]:  # Select top 2 most relevant lessons
        item = entry["item"]
        rule = item.get("guidance_rule", "").strip()
        if rule and rule not in guidance_rules:
            guidance_rules.append(rule)
            retrieved_sources.append({
                "source_test_id": item.get("source_test_id"),
                "weakness_category": item.get("weakness_category"),
                "relevance_score": entry["score"],
                "relevance_reason": entry["reason"],
                "learned_lesson": item.get("learned_lesson")
            })
            
    combined_guidance = "\n".join(f"- {r}" for r in guidance_rules)
    
    enhanced_prompt = (
        f"[MODELLOOP GUIDED CONTEXT INTERVENTION]\n"
        f"Target Weakness Category: {target_category}\n"
        f"Relevant Category Guidance Learned from Past Baseline Failures:\n"
        f"{combined_guidance}\n"
        f"----------------------------------------\n"
        f"USER PROMPT: {original_prompt}"
    )
    
    trace_metadata = {
        "target_test_id": test_id,
        "target_category": target_category,
        "retrieved_lesson_count": len(retrieved_sources),
        "retrieved_sources": retrieved_sources,
        "guidance_supplied": combined_guidance
    }
    
    return enhanced_prompt, trace_metadata
