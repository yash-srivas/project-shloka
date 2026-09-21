Three diagrams, one for each concern: the user flow, the technical architecture, and the evaluation framework. Let me build them.Now the technical architecture — what you actually need to build, layer by layer.Now the evaluation framework — how to measure whether the system is actually working.Here is everything broken down clearly.

---

## What to build, step by step

### Phase 1 — Data preparation (before any code)

The first thing you build is not the app, it is the knowledge base. Collect and clean all your source documents: the Sushruta Samhita Nidana Sthana text (especially Chapter 1), Dalhana's Nibandha Sangraha commentary, Gayadasa's Nyayachandrika, Amarakosha, and Dhatu Ratnavali. You then chunk these documents intelligently — not by arbitrary character count but by shloka boundaries — and embed them into a vector database (ChromaDB or FAISS work well for a research project). This becomes your RAG layer, Layer D in the architecture diagram. Nothing downstream works correctly without this step being done carefully.

### Phase 2 — Backend API and database

Build a simple PostgreSQL schema with three core tables: `chapters` (id, name, sthaana), `shlokas` (id, chapter_id, number, Sanskrit text, transliteration), and `shloka_steps` (shloka_id, step_number, cached_output). The caching table is critical — you do not want to run all 7 LLM calls every time a student opens a shloka. Run the pipeline once per shloka offline, store the outputs, and serve them instantly. Build a FastAPI backend with three routes: one for listing chapters, one for fetching a shloka with all its pre-computed step outputs, and one POST endpoint that the chatbot calls in real time.

### Phase 3 — AI pipeline and orchestrator

This is the core intellectual work. Build a Python orchestrator class that takes a shloka as input and runs each of the 7 step agents in sequence, passing the output of each step into the context of the next. Each agent is just an LLM call with one of the 7 prompts you already have, plus a RAG retrieval call that fetches the right knowledge for that specific step. Build the chatbot agent separately — it takes the student's question plus the full 7-step output of the current shloka as context, runs a RAG retrieval on the question, and generates the answer. Run the pipeline offline for all shlokas in Chapter 1 and cache the results in the database before the students ever use the app.

### Phase 4 — Frontend (Android)

Three screens. The chapter/shloka list screen is a simple scrollable list — nothing complex. The shloka detail screen is the main one: display the Sanskrit text at the top, then seven tabs below it (one per step), each showing the pre-cached output for that step. The chatbot is a floating button on the shloka detail screen that opens a chat thread. The chat always knows which shloka the student is currently viewing and passes that context automatically to the backend.

---

## How to evaluate

You run evaluation in three phases that match your synopsis exactly.

For AI output quality, before any student touches the app, you send the 7-step outputs for 5–10 representative shlokas to your panel of Ayurveda scholars. They score each step output on a 4-point scale (not relevant / somewhat relevant / relevant / very relevant). You compute the Item-level Content Validity Index (I-CVI) per step and the Scale-level CVI (S-CVI) across all steps. Target is I-CVI ≥ 0.78. For the chatbot specifically, run it through the RAGAS framework which automatically checks faithfulness (does the answer match the retrieved context), answer relevancy (does it address the actual question), and context recall (did RAG pull the right passages).

For educational effectiveness, run a pre-test before students use the app, let them use it for 4–6 weeks on Chapter 1, then run the same post-test. Your test questions should map directly to the 7 steps — some questions test Padavibhaga understanding, some test Bhavartha comprehension, some test Dhvanitartha insight. This lets you measure not just overall improvement but which specific steps are driving the learning gains. Use a paired t-test for normally distributed data or the Wilcoxon signed-rank test otherwise, with p < 0.05 as your threshold.

For usability, have students fill in the System Usability Scale (10 questions, produces a 0–100 score, anything above 68 is considered average or better) and the Mobile App Rating Scale which gives you separate scores for functionality, aesthetics, information quality, and subjective quality. Add a short Likert-scale survey specifically about the chatbot — did it answer your doubt correctly, did it feel grounded in the shloka you were studying, would you use it again.

# User flow
![User flow](images/user_flow_diagram.png)

# Architecture
![Architecture](images/technical_architecture.png)

# Evaluation
![Evaluation](images/evaluation_framework.png)