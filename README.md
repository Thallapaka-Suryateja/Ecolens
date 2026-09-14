# 🌿 EcoLens — Campus Sustainability Audit Agent

> An AI-powered agentic system that autonomously audits an Indian college campus's sustainability footprint across five domains, benchmarks it against real government standards, and generates a professional SDG compliance report.

**Built for:** 1M1B × IBM SkillsBuild AI for Sustainability Virtual Internship  
**Developer:** Thallapaka Suryateja — VIT Chennai  
**SDGs Addressed:** SDG 6 · SDG 7 · SDG 12 · SDG 13 · SDG 15  

---

## 🔍 What It Does

Most sustainability tools give generic advice. EcoLens acts like a sustainability consultant — it takes your campus's actual consumption data, runs it through a 5-step autonomous audit pipeline, and produces a downloadable PDF report with your SDG compliance score and ranked recommendations.

**The agent runs 5 autonomous steps:**

| Step | Action |
|------|--------|
| 1 | Calculate carbon footprint per domain using real BEE/MoEFCC factors |
| 2 | Score each domain (0–100) against Indian national benchmarks |
| 3 | Identify critical problem areas (LLM-powered, grounded in data) |
| 4 | Generate 5 prioritised recommendations ranked by CO₂ impact |
| 5 | Write an executive summary + produce downloadable PDF report |

---

## 🏗️ Architecture

```
User Input (Campus Data)
        │
        ▼
┌───────────────────────────────────────────────┐
│              EcoLens Audit Agent               │
│                                               │
│  Step 1: calculate_footprints()               │
│          → Pure Python, BEE/MoEFCC factors    │
│                                               │
│  Step 2: score_domains()                      │
│          → Ratio-to-score conversion          │
│          → Weighted overall score             │
│                                               │
│  Step 3: identify_problems()    ┐             │
│  Step 4: generate_recommendations() ├ Groq   │
│  Step 5: generate_summary()    ┘  LLM calls  │
│                                               │
│  Output: Structured audit result dict         │
└───────────────────────────────────────────────┘
        │
        ▼
┌──────────────────┐    ┌──────────────────────┐
│  Streamlit UI    │    │   PDF Report          │
│  (Live results)  │    │   (fpdf2 generator)   │
└──────────────────┘    └──────────────────────┘
```

**Pattern used:** Plan-and-execute (steps are fixed and known upfront; each step is atomic and independently testable — recommended by agentic AI engineering guidelines over ReAct for structured audit tasks).

---

## 📊 Real Data Sources

All benchmarks are sourced from Indian government publications — no invented numbers:

| Domain | Source | Benchmark Used |
|--------|--------|----------------|
| Energy | Bureau of Energy Efficiency (BEE) | 800 kWh/student/year |
| CO₂ factor | MoEFCC GHG Platform India, CEA v18 | 0.716 kg CO₂/kWh |
| Water | CPHEEO Manual, Ministry of Jal Shakti | 45 L/person/day |
| Waste | CPCB SWM Guidelines | 0.1 kg/student/day |
| Transport | ARAI / MoRTH | 0.12 kg CO₂/vehicle-km |
| Green cover | GRIHA (MoEFCC) | 1 tree per 50 sq.ft |
| Canteen | ICAR lifecycle emissions | 0.8 kg CO₂/veg meal |

---

## 🛠️ Tech Stack

| Layer | Tool | Reason |
|-------|------|--------|
| Language | Python 3.10+ | Clean, readable, IBM Bob compatible |
| UI + Deployment | Streamlit | Fastest path to a live deployed web app |
| AI Engine | Groq API (Llama 3.3 70B) | Fast inference, free tier |
| PDF Generation | fpdf2 | Pure Python, no external dependencies |
| Dev Assistant | IBM Bob (VS Code) | Used for agent orchestration + scoring logic |
| Architecture | IBM Granite (production design) | Model-agnostic design, Granite-ready |

**IBM Bob was used for:**
- Writing and reviewing the `agent.py` orchestrator loop
- Designing the `score_domains()` weighted scoring function
- Refactoring `calculate_footprints()` for edge cases

---

## 🚀 Running Locally

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/ecolens.git
cd ecolens

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Groq API key
# Edit .streamlit/secrets.toml and add:
# GROQ_API_KEY = "your_key_here"
# Get a free key at: https://console.groq.com

# 4. Run
streamlit run app.py
```

---

## ☁️ Deploying to Streamlit Cloud (Free)

1. Push this repo to GitHub (make sure `.streamlit/secrets.toml` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Under **Secrets**, add: `GROQ_API_KEY = "your_key_here"`
5. Deploy — you get a live public URL instantly

---

## 📁 Project Structure

```
ecolens/
├── app.py              ← Streamlit UI + audit workflow
├── agent.py            ← 5-step audit agent (IBM Bob assisted)
├── benchmarks.py       ← Real Indian government benchmark data
├── report.py           ← PDF report generator
├── requirements.txt
└── .streamlit/
    ├── config.toml     ← Theme configuration
    └── secrets.toml    ← API keys (not committed to Git)
```

---

## 🌍 Responsible AI

| Principle | Implementation |
|-----------|----------------|
| **Transparency** | Every score shows which benchmark it's measured against |
| **Fairness** | Benchmarks are government-sourced, not subjective assumptions |
| **Grounding** | LLM is given actual calculated numbers — not asked to guess |
| **Accountability** | Report includes a disclaimer recommending professional review |
| **Privacy** | No personal data collected — only institutional consumption figures |

---

## 📈 Expected Impact

If deployed across India's ~1,000 NAAC-accredited universities:
- Provides each institution a baseline sustainability score in under 60 seconds
- Replaces ₹2–5 lakh manual consultant audits with a free, instant tool
- Enables annual SDG compliance tracking
- Estimated: identifying and fixing top 2 problem areas per campus could reduce institutional CO₂ by 15–25% on average

---

## 🔗 Live Demo

> [Add your Streamlit Cloud URL here after deployment]

---

*Built with Python · Streamlit · Groq · IBM Bob · Real Indian Government Data*
