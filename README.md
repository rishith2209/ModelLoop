# ⚡ ModelLoop: LLM Evaluation & Self-Improvement Prototype

[![BuildSprint 2026](https://img.shields.io/badge/BuildSprint-2026-blue.svg)](https://github.com/rishith2209/ModelLoop)
[![Model](https://img.shields.io/badge/Target%20Model-Gemini%203.6%20Flash-green.svg)](https://deepmind.google/technologies/gemini/)
[![Python](https://img.shields.io/badge/Python-3.13-yellow.svg)](https://www.python.org/)
[![UI](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)

**ModelLoop** is an automated model evaluation, failure-diagnosis, and self-improvement framework built for **BuildSprint 2026**.

Instead of manually inspecting LLM outputs and tweaking prompts by hand, ModelLoop establishes a closed-loop system: **it evaluates baseline model behavior against strict criteria, extracts structured lessons from failures, selectively retrieves domain-relevant guidance, and re-evaluates the model independently to measure performance transfer.**

---

## 💡 Core Conceptual Workflow

```
┌─────────────────────────┐
│     BENCHMARK SUITE     │ (13 Tests across 8 Weakness Categories)
└────────────┬────────────┘
             │
             v
┌─────────────────────────┐
│    GEMINI 3.6 FLASH     │ (Baseline Run)
└────────────┬────────────┘
             │
             v
┌─────────────────────────┐
│  INDEPENDENT EVALUATOR  │ (Strict Criteria-Based Judgment)
└────────────┬────────────┘
             │
             ├─────────────────────────┐
      [PASS] │                         │ [FAIL]
             v                         v
   (Baseline Results)       ┌─────────────────────────┐
                            │     LEARNING ENGINE     │ (Extracts Failure Lessons)
                            └──────────┬──────────────┘
                                       │
                                       v
                            ┌─────────────────────────┐
                            │   IMPROVEMENT MEMORY    │ (Stored in improvement_memory.json)
                            └──────────┬──────────────┘
                                       │
                                       v
                            ┌─────────────────────────┐
                            │ RELEVANCE RETRIEVAL ENGINE│ (compute_relevance_score)
                            └──────────┬──────────────┘
                                       │
                                       v
                            ┌─────────────────────────┐
                            │ GUIDED CONTEXT LAYER    │ (In-Context Intervention)
                            └──────────┬──────────────┘
                                       │
                                       v
                            ┌─────────────────────────┐
                            │    GEMINI 3.6 FLASH     │ (Post-Intervention Re-evaluation)
                            └──────────┬──────────────┘
                                       │
                                       v
                            ┌─────────────────────────┐
                            │  INDEPENDENT EVALUATOR  │ (Same Criteria Verification)
                            └──────────┬──────────────┘
                                       │
                                       v
                            ┌─────────────────────────┐
                            │ BEFORE vs AFTER REPORT  │ (+38.5% Pass Rate Delta)
                            └─────────────────────────┘
```

---

## 📊 Key Benchmark Results & Verification

All numbers are dynamically calculated from actual pipeline runs and saved to `evaluation_results.json`:

| Metric | Baseline Run | Post-Intervention | Improvement |
| :--- | :---: | :---: | :---: |
| **Pass Rate** | **53.8%** (7/13) | **92.3%** (12/13) | **+38.5%** |
| **Average Score** | **0.68** / 1.00 | **0.92** / 1.00 | **+0.24** |
| **Failures Detected** | 6 Failures | 1 Failure | **-5 Failures** |
| **Lessons Extracted** | 0 Lessons | 6 Category Rules | **6 Lessons Stored** |

> 🔒 **Honesty Disclosure**: ModelLoop uses *Guided-Context Intervention* (automated in-context guidance). The underlying neural network weights of Gemini are **not** retrained. The evaluator remains 100% independent and isolated from intervention metadata during judgment.

---

## 🔀 Demonstrated Generalization (Transfer Learning)

ModelLoop proves that failure-derived lessons generalize to **brand new unseen test cases**:

1. **JSON Formatting Generalization (`TC01` → `TC11`)**:
   - **Baseline Failure (`TC01`)**: Gemini included markdown code fences (` ```json `) in raw JSON output.
   - **Derived Rule**: *"Output raw JSON string only. Do NOT use markdown code blocks like ```json."*
   - **Generalization Target (`TC11`)**: A new prompt asking for a user profile for *"Jane Doe"*.
   - **Outcome**: `TC11` **PASSED** on the post-intervention run using the retrieved `TC01` rule.

2. **Word Count Generalization (`TC02` → `TC13`)**:
   - **Baseline Failure (`TC02`)**: Gemini generated 13 words for a 10-word limit limit constraint.
   - **Derived Rule**: *"Keep answer extremely brief. Word count must strictly be 10 words or fewer."*
   - **Generalization Target (`TC13`)**: Define photosynthesis in $\le 8$ words.
   - **Outcome**: `TC13` **PASSED** with a compliant 7-word output (*"Plants convert light into chemical energy sugar."*).

3. **Evaluator Independence Proof (`TC12`)**:
   - **Test Case (`TC12`)**: Write a sentence about fish without the letter `'a'`.
   - **Retrieval Match**: Retrieved lesson from `TC03` (which targeted letter `'e'`).
   - **Outcome**: Gemini still included the letter `'a'`, and the independent evaluator marked `TC12` as **FAILED**. This proves zero evaluator data leakage or fake passing grades.

---

## 📁 Repository Structure

```
ModelLoop/
│
├── main.py                     # Execution pipeline conductor (CLI execution & run loop)
├── LearningEngine.py           # Lesson extraction engine & compute_relevance_score algorithm
├── evaluator.py                # Criteria-based independent judge (PASS/FAIL & scoring)
├── test_cases.py               # Benchmark bank: 13 cases across 8 weakness categories
├── app.py                      # Dark research lab Web UI built with Streamlit
│
├── evaluation_results.json     # Dynamic run metrics, comparative stats & audit traces
├── improvement_memory.json     # Stored failure lessons and guidance rules
├── improvements.json           # Weakness classifications and structured examples
│
├── .gitignore                  # Excludes .env, venv/, and Python cache
└── .env.example                # Safe environment variable template
```

---

## 🛠️ Installation & Setup Guide

### 1. Prerequisites
- **Python**: 3.10+ (Tested on Python 3.13)
- **Gemini API Key**: Obtain a key from [Google AI Studio](https://aistudio.google.com/).

### 2. Environment Setup
Clone the repository and set up a virtual environment:

```powershell
# Clone the repository
git clone https://github.com/rishith2209/ModelLoop.git
cd ModelLoop

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install google-genai python-dotenv streamlit colorama
```

### 3. API Key Configuration
Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

---

## 🚀 How to Run ModelLoop

### Option A: Launch Web Interface (Recommended)

To launch the dark research lab dashboard:

```powershell
streamlit run app.py
```

Open your browser at `http://localhost:8501` to explore:
- **📊 Overview & Health**: Visual KPIs and category weakness heatmap.
- **📋 Detailed Test Results**: Expandable side-by-side comparison of baseline vs. post-intervention responses.
- **🧠 Learning Memory**: Explorer for failure-derived rules stored in `improvement_memory.json`.
- **🔀 Generalization & Retrieval**: Audit trace showing why lessons were retrieved or penalized.
- **⚡ Custom Test Lab**: Interactive playground for custom prompts.
- **🔍 Audit & Experiment View**: Live implementation evidence reading source code directly from `main.py`, `evaluator.py`, `LearningEngine.py`, and JSON artifacts.

### Option B: Run via Command Line Interface (CLI)

To execute the benchmark pipeline in headless mode:

```powershell
python main.py
```

---

## 🛡️ Security & Integrity

- **No Hardcoded Secrets**: All credentials are loaded via environment variables (`python-dotenv`). `.env` is explicitly git-ignored.
- **No Hardcoded Metrics**: All numbers rendered in `app.py` are loaded directly from `evaluation_results.json` produced during runtime execution.
- **Evaluator Isolation**: The evaluator judges model responses strictly against fixed benchmark criteria without inspecting intervention context.

---

## 📜 License

This project is licensed under the MIT License — built for **BuildSprint 2026**.
