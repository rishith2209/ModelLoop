# ⚡ ModelLoop: LLM Evaluation & Failure-Driven Improvement Framework

[![BuildSprint 2026](https://img.shields.io/badge/BuildSprint-2026-blue.svg)](https://github.com/rishith2209/ModelLoop)
[![Target Models](https://img.shields.io/badge/Models-Gemini_3.6_Flash_%7C_GLM_5.2_%7C_Claude_3.5-green.svg)](https://deepmind.google/technologies/gemini/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-yellow.svg)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**ModelLoop** is an automated model evaluation, failure-diagnosis, and self-improvement framework built for **BuildSprint 2026**.

Instead of manually inspecting LLM outputs and tweaking prompts by hand, ModelLoop establishes a closed-loop research framework: **it evaluates baseline model behavior against strict criteria, extracts structured lessons from failures, selectively retrieves domain-relevant guidance, and re-evaluates the model independently to measure performance transfer.**

---

## 📑 Table of Contents
- [💡 Core Conceptual Workflow](#-core-conceptual-workflow)
- [⚡ Model-Agnostic Provider Architecture](#-model-agnostic-provider-architecture)
- [📊 Key Benchmark Results & Verification](#-key-benchmark-results--verification)
- [🔀 Demonstrated Generalization (Transfer Learning)](#-demonstrated-generalization-transfer-learning)
- [📁 Repository Structure](#-repository-structure)
- [🛠️ Installation & Setup Guide](#️-installation--setup-guide)
- [🚀 How to Run ModelLoop](#-how-to-run-modelloop)
- [🔬 Web UI Features & Audit Capabilities](#-web-ui-features--audit-capabilities)
- [🛡️ Security, Privacy & Technical Integrity](#️-security-privacy--technical-integrity)
- [📜 License & Acknowledgments](#-license--acknowledgments)

---

## 💡 Core Conceptual Workflow

ModelLoop operates as an automated 6-step closed-loop evaluation and improvement engine:

```
┌─────────────────────────┐
│     BENCHMARK SUITE     │ (13 Benchmark Cases across 8 Weakness Categories)
└────────────┬────────────┘
             │
             v
┌─────────────────────────┐
│     LLM PROVIDER        │ (Baseline Run: Gemini 3.6 Flash / Configured Model)
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
                            │   IMPROVEMENT MEMORY    │ (Persisted in improvement_memory.json)
                            └──────────┬──────────────┘
                                       │
                                       v
                            ┌─────────────────────────┐
                            │ RELEVANCE RETRIEVAL ENGINE│ (compute_relevance_score Keyword Matching)
                            └──────────┬──────────────┘
                                       │
                                       v
                            ┌─────────────────────────┐
                            │  GUIDED CONTEXT LAYER   │ (In-Context Intervention Prompt Prefix)
                            └──────────┬──────────────┘
                                       │
                                       v
                            ┌─────────────────────────┐
                            │     LLM PROVIDER        │ (Post-Intervention Re-evaluation)
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

## ⚡ Model-Agnostic Provider Architecture

ModelLoop's evaluation engine, learning engine, and relevance scoring algorithm are completely model-agnostic. All LLM interactions route through unified provider adapters in `model_adapter.py`:

```
                    ┌─────────────────────┐
                    │     MODELLOOP       │
                    │                     │
                    │ Evaluation Engine   │
                    │ Learning Engine     │
                    │ Relevance Engine    │
                    │ Audit Engine        │
                    └──────────┬──────────┘
                               │
                         Model Adapter (model_adapter.py)
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
         Google            Anthropic       OpenAI-Compatible
            │                  │                  │
      Gemini 3.6 Flash      Claude        OpenCode Zen / Custom
      Gemini 3.7 Flash                     GLM 5.2 MAAS
            │                  │                  │
            └──────────────────┼──────────────────┘
                               │
                         Model Response
                               │
                               ▼
                     Independent Evaluator (evaluator.py)
                               │
                               ▼
                        Learning + Audit
```

### Supported Model Catalog & Providers:
- **Google GenAI (Native SDK)**:
  - `gemini-3.6-flash` *(Default Known-Good Benchmark Baseline)*
  - `gemini-3.7-flash`
  - `gemini-3.5-flash`
  - `gemini-3.1-pro`
  - `gemini-2.5-flash`
- **OpenAI-Compatible Gateways**:
  - `zai-org/glm-5.2-maas` (OpenCode Zen)
  - `zen-pro`, `zen-flash`, `zen-coder`
- **Anthropic**:
  - `claude-3-5-sonnet-20241022`
  - `claude-3-5-haiku-20241022`
- **Custom Endpoints**: Configurable `base_url` and `model_name` for any OpenAI-compatible API.

---

## 📊 Key Benchmark Results & Verification

All benchmark statistics are dynamically calculated from actual pipeline executions and persisted to `evaluation_results.json`:

| Metric | Baseline Run | Post-Intervention | Improvement Delta |
| :--- | :---: | :---: | :---: |
| **Pass Rate** | **53.8%** (7/13) | **92.3%** (12/13) | **+38.5%** |
| **Average Score** | **0.68** / 1.00 | **0.92** / 1.00 | **+0.24** |
| **Failures Detected** | 6 Failures | 1 Failure | **-5 Failures** |
| **Lessons Generated** | 0 Lessons | 6 Category Rules | **6 Lessons Persisted** |

> 🔒 **Honesty Disclosure**: ModelLoop uses *Guided-Context Intervention* (automated in-context guidance). The underlying neural network weights of the model are **not** retrained. The evaluator remains 100% independent and isolated from intervention metadata during judgment.

---

## 🔀 Demonstrated Generalization (Transfer Learning)

ModelLoop proves that failure-derived lessons generalize to **brand new unseen test cases**:

1. **JSON Formatting Generalization (`TC01` → `TC11`)**:
   - **Baseline Failure (`TC01`)**: Gemini included markdown code fences (` ```json `) in raw JSON output.
   - **Derived Rule**: *"Output raw JSON string only. Do NOT use markdown code blocks like ```json."*
   - **Generalization Target (`TC11`)**: A new prompt asking for a user profile for *"Jane Doe"*.
   - **Outcome**: `TC11` **PASSED** on the post-intervention run using the retrieved `TC01` rule.

2. **Word Count Generalization (`TC02` → `TC13`)**:
   - **Baseline Failure (`TC02`)**: Gemini generated 13 words for a 10-word limit constraint.
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
├── model_adapter.py            # Unified provider adapter layer (Google, Anthropic, OpenAI/OpenCode)
├── LearningEngine.py           # Failure lesson extraction & compute_relevance_score algorithm
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
- **API Credentials**: Gemini API key from [Google AI Studio](https://aistudio.google.com/) (or keys for Anthropic/OpenCode).

### 2. Environment Setup
Clone the repository and set up a virtual environment:

```powershell
# Clone the repository
git clone https://github.com/rishith2209/ModelLoop.git
cd ModelLoop

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required dependencies
pip install google-genai python-dotenv streamlit colorama
```

### 3. API Key Configuration
Create a `.env` file in the root directory:

```env
# Primary Target Provider
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Optional Secondary Providers
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENCODE_API_KEY=your_opencode_api_key_here
```

---

## 🚀 How to Run ModelLoop

### Option A: Launch Web Interface (Recommended)

To launch the dark research lab dashboard:

```powershell
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

### Option B: Run via Command Line Interface (CLI)

To execute the benchmark pipeline in headless mode:

```powershell
python main.py
```

---

## 🔬 Web UI Features & Audit Capabilities

ModelLoop features a dark, technical research-lab dashboard organized into 7 navigation modules:

1. **📊 Overview & Health**: High-level KPIs, baseline vs. post-intervention pass rates, and weakness category heatmaps.
2. **🔬 Evaluation Lab**: Provider & Model execution control center with connection testing (`🔌 Test Provider Connection`).
3. **📋 Detailed Test Results**: Side-by-side comparison of baseline vs. post-intervention responses, scores, and evaluator explanations.
4. **🧠 Learning Memory**: Explorer for failure-derived lessons stored in `improvement_memory.json`.
5. **🔀 Generalization & Retrieval**: Audit trace showing `compute_relevance_score` reasoning for retrieved guidance.
6. **⚡ Custom Test Lab**: Interactive playground for running custom prompts through Gemini 3.6 Flash without modifying benchmark criteria.
7. **🔍 Audit & Implementation Evidence**: Dynamically loads and renders actual Python source code from `main.py`, `evaluator.py`, `LearningEngine.py`, `model_adapter.py`, and `test_cases.py` on disk.

---

## 🛡️ Security, Privacy & Technical Integrity

- **Zero Hardcoded Credentials**: All API keys are loaded via `python-dotenv`. `.env` is explicitly git-ignored.
- **Zero Hardcoded Metrics**: All numbers rendered in `app.py` are loaded directly from `evaluation_results.json` produced during runtime execution.
- **Evaluator Isolation**: The evaluator judges model responses strictly against fixed benchmark criteria without inspecting intervention context.
- **Graceful Quota Handling**: Automatically detects HTTP 429 rate limits and logs fallback states without crashing.

---

## 📜 License & Acknowledgments

This project is licensed under the **MIT License** — built for **BuildSprint 2026**.
