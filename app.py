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
    page_title="ModelLoop UI",
    page_icon="🔄",
    layout="wide"
)

# Title & Header
st.title("ModelLoop")
st.subheader("LLM Evaluation & Self-Improvement Prototype")
st.caption("Target Model: Gemini Pro / gemini-3.6-flash | BuildSprint 2026")

# Status State Management
if "status" not in st.session_state:
    st.session_state.status = "Ready"

# Top Action Control Bar
col_btn, col_status = st.columns([1, 4])
with col_btn:
    run_clicked = st.button("🚀 Run Evaluation", type="primary", use_container_width=True)

with col_status:
    if st.session_state.status == "Ready":
        st.info("Status: Ready to execute evaluation pipeline.")
    elif st.session_state.status == "Running":
        st.warning("Status: Running baseline evaluation, failure detection, learning engine, and post-intervention re-evaluation...")
    elif st.session_state.status == "Completed":
        st.success("Status: Evaluation & Learning Pipeline Completed successfully.")
    elif "Error" in st.session_state.status:
        st.error(f"Status: {st.session_state.status}")

# Run Pipeline on Button Click
if run_clicked:
    st.session_state.status = "Running"
    with st.spinner("Running Baseline Evaluation, Category Learning, and Guided Context Intervention..."):
        try:
            pipeline.main()
            st.session_state.status = "Completed"
            st.success("Evaluation pipeline finished successfully!")
        except Exception as e:
            st.session_state.status = f"Error: {str(e)}"
            st.error(f"Execution Error: {str(e)}")

# Helper Functions to Load Artifacts safely
def load_json(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

eval_results = load_json("evaluation_results.json")
memory_results = load_json("improvement_memory.json")

if eval_results:
    st.divider()
    metrics = eval_results.get("generalization_metrics", eval_results.get("learning_metrics", {}))
    baseline_run = eval_results.get("baseline_run", {})
    post_run = eval_results.get("post_intervention_run", {})
    
    # 4. SUMMARY METRICS CARDS
    st.markdown("### 📊 Pipeline Summary")
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    
    m1.metric("Total Tests", baseline_run.get("total_tests", 0))
    m2.metric("Baseline Pass Rate", metrics.get("baseline_pass_rate", "N/A"))
    m3.metric("Post-Intervention Pass Rate", metrics.get("post_intervention_pass_rate", "N/A"))
    m4.metric("Pass Rate Delta", metrics.get("pass_rate_delta", "N/A"))
    m5.metric("Baseline Failures", metrics.get("total_baseline_failures", 0))
    m6.metric("Lessons Generated", metrics.get("lessons_generated", 0))
    
    # Notice & Disclosure
    st.caption("ℹ️ **Mechanism**: Category-Based Guided Context Intervention. *Underlying Gemini weights were NOT retrained.*")
    
    # Tabs for detail inspection
    tab_tests, tab_learning, tab_gen, tab_audit = st.tabs([
        "📋 Test Results", 
        "🧠 Learning Memory", 
        "🔀 Generalization Trace", 
        "🔍 Audit JSON Inspector"
    ])
    
    # 5. TEST RESULTS TAB
    with tab_tests:
        st.markdown("### Test Cases Breakdown")
        
        b_results = {r["test_id"]: r for r in baseline_run.get("detailed_results", [])}
        p_results = {r["test_id"]: r for r in post_run.get("detailed_results", [])}
        
        all_ids = sorted(list(set(b_results.keys()).union(set(p_results.keys()))))
        
        table_data = []
        for tid in all_ids:
            b_item = b_results.get(tid, {})
            p_item = p_results.get(tid, {})
            
            b_res = b_item.get("evaluation_result", "N/A")
            p_res = p_item.get("evaluation_result", "N/A")
            
            table_data.append({
                "Test ID": tid,
                "Category": b_item.get("category", "N/A"),
                "Severity": b_item.get("severity", "N/A"),
                "Baseline Result": "✅ PASS" if b_res == "PASS" else "❌ FAIL",
                "Baseline Score": b_item.get("score", 0.0),
                "Post Result": "✅ PASS" if p_res == "PASS" else "❌ FAIL",
                "Post Score": p_item.get("score", 0.0),
                "Description": b_item.get("description", "")
            })
            
        st.dataframe(table_data, use_container_width=True)

    # 6. LEARNING RESULTS TAB
    with tab_learning:
        st.markdown("### Learned Lessons (Improvement Memory)")
        if memory_results:
            for item in memory_results:
                with st.expander(f"Lesson from {item.get('source_test_id')} | Category: {item.get('weakness_category')} ({item.get('severity')})"):
                    st.write(f"**Learned Lesson:** {item.get('learned_lesson')}")
                    st.code(item.get('guidance_rule'), language="markdown")
                    st.write(f"**Evaluator Explanation:** {item.get('evaluator_explanation')}")
                    st.write(f"**Failed Response Snippet:**")
                    st.text(item.get('failed_response_snippet'))
        else:
            st.info("No learned lessons recorded yet.")

    # 7. GENERALIZATION TAB
    with tab_gen:
        st.markdown("### Cross-Test Generalization Audit")
        st.write("Demonstrates where lessons learned from one baseline test were retrieved and applied to improve a DIFFERENT test in the same weakness category.")
        
        gen_test_ids = ["TC11", "TC12", "TC13"]
        p_detailed = post_run.get("detailed_results", [])
        
        for r in p_detailed:
            tid = r["test_id"]
            if tid in gen_test_ids:
                trace = r.get("category_retrieval_trace")
                st.markdown(f"#### Test `{tid}` — Category: `{r['category']}`")
                st.write(f"**Description:** {r.get('description')}")
                st.write(f"**Post-Intervention Result:** {'✅ PASS' if r['evaluation_result'] == 'PASS' else '❌ FAIL'}")
                
                if trace and trace.get("retrieved_sources"):
                    sources_str = ", ".join([s["source_test_id"] for s in trace["retrieved_sources"]])
                    st.info(f"⬅️ **Retrieved Lesson Sources**: `{sources_str}` (Same weakness category: `{r['category']}`)")
                    st.code(trace.get("guidance_supplied"), language="markdown")
                else:
                    st.caption("No category guidance retrieved.")
                st.divider()

    # 8. AUDIT INFORMATION TAB
    with tab_audit:
        st.markdown("### Raw Audit Files")
        st.caption("Direct, unedited inspection of local JSON artifacts.")
        
        audit_col1, audit_col2 = st.columns(2)
        with audit_col1:
            st.markdown("#### `evaluation_results.json`")
            st.json(eval_results)
            
        with audit_col2:
            st.markdown("#### `improvement_memory.json`")
            st.json(memory_results)
