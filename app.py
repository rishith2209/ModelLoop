"""
ModelLoop Streamlit UI.
Provides a simple, clean Web UI to run evaluation and inspect results & learning metrics.
"""

import os
import json
import streamlit as st
import main as pipeline

# Page configuration
st.set_page_config(
    page_title="ModelLoop | Research Laboratory",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Technical / Research Lab Styling & Sidebar UX
st.markdown("""
<style>
    /* Dark Theme Customizations */
    .stApp {
        background-color: #0e1117;
        color: #e0e6ed;
    }
    
    /* Sidebar Width & Professional Styling */
    section[data-testid="stSidebar"] {
        width: 340px !important;
        background-color: #12161f !important;
        border-right: 1px solid #232a3b !important;
    }
    
    /* Sidebar padding adjustments to avoid scrollbars/overflow */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
    }

    /* Model Identity Card Styling */
    .sidebar-card {
        background-color: #1a202c;
        border: 1px solid #2d3748;
        border-radius: 6px;
        padding: 12px 14px;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    
    .sidebar-card-title {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #718096;
        margin-bottom: 6px;
    }
    
    .sidebar-card-value {
        font-size: 0.95rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 8px;
    }
    
    .sidebar-card-disclosure {
        font-size: 0.75rem;
        color: #a0aec0;
        line-height: 1.3;
        border-top: 1px solid #2d3748;
        padding-top: 6px;
        margin-top: 6px;
    }

    /* Streamlit Radio Buttons (Navigation) Customization */
    div[data-testid="stRadio"] > label {
        display: none !important; /* Hide 'Navigation' header label */
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 4px !important;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
        margin: 0px !important;
        cursor: pointer !important;
        transition: all 0.15s ease-in-out !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
    }
    
    /* Hide native radio circles */
    div[data-testid="stRadio"] div[role="radiogroup"] label input[type="radio"] {
        display: none !important;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] label p {
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: #cbd5e0 !important;
        margin: 0 !important;
        white-space: nowrap !important;
    }
    
    /* Selected State */
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input[type="radio"]:checked) {
        background-color: #2b3649 !important;
        border: 1px solid #4a5568 !important;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input[type="radio"]:checked) p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Hover State */
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
        background-color: #1a2332 !important;
    }

    /* General Card & Metric Styling */
    .metric-card {
        background-color: #1a1f2c;
        border: 1px solid #2d3748;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Helper Function to Load Artifacts safely
def load_json(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

# Helper Function to Read Real Source Code Excerpts safely
def read_source_excerpt(filename, start_str=None, end_str=None, max_lines=50):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, filename)
    if not os.path.exists(file_path):
        return "Source evidence unavailable."
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        if not start_str:
            return "".join(lines[:max_lines])
            
        start_idx = 0
        for i, line in enumerate(lines):
            if start_str in line:
                start_idx = i
                break
                
        end_idx = min(start_idx + max_lines, len(lines))
        if end_str:
            for i in range(start_idx + 1, len(lines)):
                if end_str in line:
                    end_idx = i + 1
                    break
                    
        return "".join(lines[start_idx:end_idx])
    except Exception as e:
        return f"Error reading source file: {str(e)}"

eval_results = load_json("evaluation_results.json")
memory_results = load_json("improvement_memory.json")

# Sidebar Navigation & Control Panel
with st.sidebar:
    st.markdown("### ⚡ ModelLoop Lab")
    st.caption("LLM Evaluation & Failure-Driven Improvement")
    
    # Compact Model Identity Card
    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-card-title">Target Model</div>
        <div class="sidebar-card-value">Gemini 3.6 Flash</div>
        <div class="sidebar-card-title">Provider</div>
        <div class="sidebar-card-value">Google GenAI API</div>
        <div class="sidebar-card-disclosure">
            🔒 <b>Guided-context intervention</b><br>
            Underlying weights are not retrained.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("##### Navigation")
    
    nav_selection = st.radio(
        "Navigation",
        [
            "📊 Overview & Health",
            "🔬 Evaluation Lab",
            "📋 Detailed Test Results",
            "🧠 Learning Memory",
            "🔀 Generalization & Retrieval",
            "⚡ Custom Test Lab",
            "🔍 Audit & Experiment View"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Run Benchmark Action Button
    run_clicked = st.button("🚀 Run Full Benchmark", type="primary", use_container_width=True)
    if run_clicked:
        with st.spinner("Executing Baseline, Failure Engine, Retrieval & Post-Intervention..."):
            try:
                pipeline.main()
                st.success("Benchmark completed successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Execution Error: {str(e)}")

# MAIN HEADER
st.title("ModelLoop")
st.caption("Automated Evaluation → Failure Detection → Category Learning → Guided Intervention → Verification")

# 1. OVERVIEW & HEALTH SECTION
if nav_selection == "📊 Overview & Health":
    st.header("📊 Model Performance & Health")
    
    if eval_results:
        metrics = eval_results.get("generalization_metrics", eval_results.get("learning_metrics", {}))
        baseline_run = eval_results.get("baseline_run", {})
        post_run = eval_results.get("post_intervention_run", {})
        
        # Primary KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric(
            label="Baseline Pass Rate", 
            value=metrics.get("baseline_pass_rate", "N/A"),
            delta=f"Avg Score: {metrics.get('baseline_avg_score', 0.0)}"
        )
        col2.metric(
            label="Post-Intervention Pass Rate", 
            value=metrics.get("post_intervention_pass_rate", "N/A"),
            delta=metrics.get("pass_rate_delta", "N/A")
        )
        col3.metric(
            label="Baseline Failures", 
            value=metrics.get("total_baseline_failures", 0),
            delta="- Failures Detected",
            delta_color="inverse"
        )
        col4.metric(
            label="Lessons Generated & Applied", 
            value=metrics.get("lessons_generated", 0),
            delta="Category Rules"
        )
        
        st.divider()
        
        # Category Breakdown & Weakness Map
        st.subheader("🔥 Weakness Category Heatmap")
        
        category_breakdown = metrics.get("category_breakdown", {})
        
        cat_cols = st.columns(3)
        idx = 0
        for cat, stats in category_breakdown.items():
            b_rate = stats.get("baseline_pass_rate", "0%")
            p_rate = stats.get("post_intervention_pass_rate", "0%")
            imp = stats.get("improvement", "+0%")
            
            status_tag = "🟢 IMPROVED" if float(imp.replace("%","").replace("+","")) > 0 else "⚪ UNCHANGED"
            
            with cat_cols[idx % 3]:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{cat.replace('_', ' ').title()}</h4>
                    <p style="font-size: 1.2em; font-weight: bold;">{b_rate} → {p_rate} ({imp})</p>
                    <p>{status_tag}</p>
                </div>
                """, unsafe_allow_html=True)
                st.write("")
            idx += 1

        # Regression Detection Banner
        st.divider()
        regressions = [
            cat for cat, stats in category_breakdown.items() 
            if float(stats.get("improvement", "0%").replace("%","").replace("+","")) < 0
        ]
        if regressions:
            st.error(f"⚠️ REGRESSION DETECTED in categories: {', '.join(regressions)}")
        else:
            st.success("✅ NO CATEGORY-LEVEL REGRESSION DETECTED across evaluation suite.")

    else:
        st.warning("No evaluation results found. Click 'Run Full Benchmark' in the sidebar to generate data.")

# 2. EVALUATION LAB
elif nav_selection == "🔬 Evaluation Lab":
    st.header("🔬 Evaluation Lab & Control Center")
    st.markdown("Configure and execute benchmark evaluations against Gemini 3.6 Flash.")
    
    st.info("💡 **Execution Strategy**: Relevance-Matched Guided Context Intervention with Independent Evaluator Isolation.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.selectbox("Target Model", ["Gemini 3.6 Flash (gemini-3.6-flash)"], disabled=True)
        st.selectbox("Provider", ["Google GenAI API"], disabled=True)
    with c2:
        st.selectbox("Test Suite", ["Full Benchmark (13 Cases)"], disabled=True)
        st.selectbox("Intervention Layer", ["Relevance-Matched Guided Context"], disabled=True)
        
    st.divider()
    st.write("Ready to run execution loop.")

# 3. DETAILED TEST RESULTS
elif nav_selection == "📋 Detailed Test Results":
    st.header("📋 Detailed Test Cases & Side-by-Side Comparison")
    
    if eval_results:
        baseline_run = eval_results.get("baseline_run", {})
        post_run = eval_results.get("post_intervention_run", {})
        
        b_results = {r["test_id"]: r for r in baseline_run.get("detailed_results", [])}
        p_results = {r["test_id"]: r for r in post_run.get("detailed_results", [])}
        
        all_ids = sorted(list(set(b_results.keys()).union(set(p_results.keys()))))
        
        for tid in all_ids:
            b_item = b_results.get(tid, {})
            p_item = p_results.get(tid, {})
            
            b_res = b_item.get("evaluation_result", "N/A")
            p_res = p_item.get("evaluation_result", "N/A")
            
            b_badge = "✅ PASS" if b_res == "PASS" else "❌ FAIL"
            p_badge = "✅ PASS" if p_res == "PASS" else "❌ FAIL"
            
            with st.expander(f"Test {tid}: {b_item.get('description', '')} [{b_badge} → {p_badge}]"):
                st.write(f"**Category:** `{b_item.get('category')}` | **Severity:** `{b_item.get('severity')}`")
                st.markdown(f"**Prompt:** `{b_item.get('original_prompt')}`")
                
                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.markdown("#### Baseline Outcome")
                    st.write(f"**Result:** {b_badge} (Score: {b_item.get('score')})")
                    st.caption(f"**Explanation:** {b_item.get('evaluator_explanation')}")
                    st.text_area("Baseline Response", b_item.get("gemini_response", ""), height=120, key=f"b_{tid}")
                    
                with res_col2:
                    st.markdown("#### Post-Intervention Outcome")
                    st.write(f"**Result:** {p_badge} (Score: {p_item.get('score')})")
                    st.caption(f"**Explanation:** {p_item.get('evaluator_explanation')}")
                    st.text_area("Post Response", p_item.get("gemini_response", ""), height=120, key=f"p_{tid}")

# 4. LEARNING MEMORY
elif nav_selection == "🧠 Learning Memory":
    st.header("🧠 Failure-Driven Learning Memory")
    st.markdown("Lessons automatically extracted by the LearningEngine from baseline failures.")
    
    if memory_results:
        for item in memory_results:
            with st.expander(f"Lesson derived from {item.get('source_test_id')} | Category: {item.get('weakness_category')}"):
                st.write(f"**Learned Lesson:** {item.get('learned_lesson')}")
                st.code(item.get('guidance_rule'), language="markdown")
                st.caption(f"**Evaluator Failure Explanation:** {item.get('evaluator_explanation')}")
                st.text_area("Failed Response Snippet", item.get('failed_response_snippet', ''), height=80, key=f"mem_{item.get('source_test_id')}")
    else:
        st.info("No lessons found in memory.")

# 5. GENERALIZATION & RETRIEVAL
elif nav_selection == "🔀 Generalization & Retrieval":
    st.header("🔀 Relevance Retrieval & Generalization Audit")
    st.markdown("Auditable trace showing how relevance scoring filters out noisy/unrelated lessons and targets specific guidance.")
    
    if eval_results:
        post_run = eval_results.get("post_intervention_run", {})
        p_detailed = post_run.get("detailed_results", [])
        
        for r in p_detailed:
            trace = r.get("category_retrieval_trace")
            if trace and trace.get("retrieved_sources"):
                with st.expander(f"Test {r['test_id']} ({r['category']}) — Retrieval Audit"):
                    st.markdown(f"**Target Test:** `{r['test_id']}` | **Outcome:** `{'✅ PASS' if r['evaluation_result']=='PASS' else '❌ FAIL'}`")
                    st.markdown(f"**Injected Guidance:**")
                    st.code(trace.get("guidance_supplied"), language="markdown")
                    
                    st.markdown("**Retrieved Source Lessons & Relevance Scoring:**")
                    for src in trace.get("retrieved_sources", []):
                        st.markdown(f"- **Source:** `{src['source_test_id']}` | **Score:** `{src.get('relevance_score')}`")
                        st.caption(f"  *Reason:* {src.get('relevance_reason')}")

# 6. CUSTOM TEST LAB
elif nav_selection == "⚡ Custom Test Lab":
    st.header("⚡ Custom Experiment Lab")
    st.markdown("Test single prompts through the ModelLoop pipeline without modifying fixed benchmark criteria.")
    
    custom_prompt = st.text_area("Enter Custom Prompt", "Respond ONLY in valid JSON format with keys 'status' and 'output'. Do not use markdown backticks.")
    custom_cat = st.selectbox("Select Category", ["instruction_following", "reasoning_consistency", "hallucination_factual"])
    
    if st.button("Execute Custom Test"):
        with st.spinner("Testing via Gemini 3.6 Flash..."):
            from main import call_gemini
            from evaluator import evaluate_response
            
            resp = call_gemini(custom_prompt)
            st.markdown("### Model Response")
            st.code(resp)

# 7. AUDIT & EXPERIMENT VIEW
elif nav_selection == "🔍 Audit & Experiment View":
    st.header("🔍 Research Summary & Technical Audit Trail")
    st.markdown("**Hypothesis**: Failure-derived, relevance-matched guidance improves LLM performance on related unseen tasks without retraining weights.")
    
    st.divider()
    
    st.subheader("🔬 Implementation Evidence")
    st.caption("Read-only excerpts dynamically loaded from the actual ModelLoop source code on disk.")
    
    # 01. Model Configuration
    with st.expander("01 · Target Model Configuration (main.py)"):
        st.markdown("**SOURCE**: `main.py` | **PURPOSE**: Model identity and Google GenAI SDK setup")
        model_code = read_source_excerpt("main.py", start_str="MODEL_NAME =", max_lines=25)
        st.code(model_code, language="python")
        
    # 02. Independent Evaluator
    with st.expander("02 · Independent Evaluator (evaluator.py)"):
        st.markdown("**SOURCE**: `evaluator.py` | **PURPOSE**: Criteria-based judgment independent of intervention context")
        eval_code = read_source_excerpt("evaluator.py", start_str="def evaluate_response", max_lines=45)
        st.code(eval_code, language="python")
        
        c1, c2, c3 = st.columns(3)
        c1.success("✓ Fixed benchmark criteria")
        c2.success("✓ Independent evaluation")
        c3.success("✓ Context isolated from scoring")

    # 03. Failure-Driven Learning Engine
    with st.expander("03 · Failure-Driven Learning Engine (LearningEngine.py)"):
        st.markdown("**SOURCE**: `LearningEngine.py` | **PURPOSE**: Failure record extraction and lesson derivation")
        learn_code = read_source_excerpt("LearningEngine.py", start_str="def process_failures_and_build_memory", max_lines=40)
        st.code(learn_code, language="python")

    # 04. Relevance Matching & Scoring
    with st.expander("04 · Relevance Matching & Scoring (LearningEngine.py)"):
        st.markdown("**SOURCE**: `LearningEngine.py` | **PURPOSE**: Scores previously learned lessons against target test weakness keywords")
        score_code = read_source_excerpt("LearningEngine.py", start_str="def compute_relevance_score", max_lines=45)
        st.code(score_code, language="python")
        
        if eval_results:
            st.markdown("#### Live Relevance Retrieval Audit Evidence from `evaluation_results.json`")
            post_detailed = eval_results.get("post_intervention_run", {}).get("detailed_results", [])
            for r in post_detailed:
                trace = r.get("category_retrieval_trace")
                if trace and trace.get("retrieved_sources"):
                    for src in trace.get("retrieved_sources", []):
                        st.markdown(f"- **Target Test `{r['test_id']}`** ← **Source `{src['source_test_id']}`** | Score: **{src.get('relevance_score')}**")
                        st.caption(f"  *Reasoning:* {src.get('relevance_reason')}")

    # 05. Evaluation Pipeline
    with st.expander("05 · Execution Pipeline (main.py)"):
        st.markdown("**SOURCE**: `main.py` | **PURPOSE**: Complete pipeline orchestration (Baseline → Failures → Learning → Post-Evaluation)")
        pipeline_code = read_source_excerpt("main.py", start_str="def run_evaluation_suite", max_lines=45)
        st.code(pipeline_code, language="python")

    # 06. Benchmark Test Definitions
    with st.expander("06 · Benchmark Test Definitions (test_cases.py)"):
        st.markdown("**SOURCE**: `test_cases.py` | **PURPOSE**: 13 benchmark evaluation cases across 8 weakness categories")
        tc_code = read_source_excerpt("test_cases.py", start_str="TEST_CASES =", max_lines=45)
        st.code(tc_code, language="python")

    # 07. Artifact Persistence
    with st.expander("07 · Artifact Persistence (main.py)"):
        st.markdown("**SOURCE**: `main.py` | **PURPOSE**: File persistence for evaluation runs and learning memory")
        persist_code = read_source_excerpt("main.py", start_str="def save_json", max_lines=20)
        st.code(persist_code, language="python")

    # 08. Security Configuration
    with st.expander("08 · Security Configuration (.gitignore)"):
        st.markdown("**SOURCE**: `.gitignore` | **PURPOSE**: Excludes credentials, secrets, virtualenvs, and python cache")
        git_code = read_source_excerpt(".gitignore", max_lines=15)
        st.code(git_code, language="text")
        
        sec_col1, sec_col2 = st.columns(2)
        sec_col1.success("✓ Environment-based secret loading")
        sec_col2.success("✓ .env & venv excluded from Git")

    st.divider()
    st.subheader("📦 Raw JSON Artifacts")
    
    audit_col1, audit_col2, audit_col3 = st.columns(3)
    with audit_col1:
        st.markdown("#### `evaluation_results.json`")
        st.json(eval_results)
    with audit_col2:
        st.markdown("#### `improvement_memory.json`")
        st.json(memory_results)
    with audit_col3:
        st.markdown("#### `improvements.json`")
        imp_results = load_json("improvements.json")
        st.json(imp_results)

