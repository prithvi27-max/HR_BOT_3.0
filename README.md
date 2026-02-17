# 🤖 HR-GPT 3.0 – Multilingual HR Analytics Copilot

An enterprise-style HR Analytics AI Assistant that combines:

- LLM-based intent understanding  
- Deterministic analytics engine  
- Machine Learning (Attrition Prediction)  
- Multilingual query support  
- Dynamic visualization & tables  

This system behaves like a ChatGPT-style assistant — but is strictly restricted to HR analytics to prevent hallucinated outputs.

---

## 🚀 Key Features

### 🧠 Intelligent Query Understanding
- LLM-based intent classification
- Confidence scoring
- Fallback rule-based NLU for robustness
- Multilingual support (English + others via translation)

### 📊 HR Analytics Engine
- Headcount
- Attrition rate
- Salary analysis
- Engagement metrics
- Workforce diversity

All numeric results are computed deterministically from structured data.

### 📈 Machine Learning
- Attrition risk prediction
- Risk bucket segmentation
- Model metrics (AUC, Precision, Recall)

### 📉 Visualization Layer
- Table-first response design
- Charts only when explicitly requested
- Plotly-based dynamic visualization

### 🛡 Safe Hybrid Architecture
- LLM used only for:
  - Intent extraction
  - Translation
  - HR concept explanations
- All analytics computed using Pandas
- No LLM-generated numbers

---

## 🏗 Architecture Overview

User Query  
↓  
Translation (if multilingual)  
↓  
LLM Intent Classification (JSON output + confidence)  
↓  
Fallback Rule-Based NLU (if low confidence)  
↓  
Deterministic HR Analytics Engine  
↓  
Table / Chart Output  
↓  
Optional ML Prediction Layer  

This hybrid design ensures:

- Flexible language understanding  
- Structured analytics accuracy  
- Reduced hallucination risk  
- High system robustness  

---

## 🧰 Tech Stack

- Python  
- Pandas  
- Streamlit  
- Plotly  
- Groq LLaMA API  
- Supabase (Postgres via REST)  
- Scikit-learn  
- JSON-based intent parsing  
- LRU caching for performance optimization  

---

## ⚙️ Local Setup Instructions

### 1️⃣ Install Python

Python 3.10 or 3.11 required.

Check version:
python --version

---

### 2️⃣ Clone Repository

git clone https://github.com/prithvi27-max/HR_BOT_3.0.git  
cd HR_BOT_3.0  

---

### 3️⃣ Create Virtual Environment (Recommended)

Windows:
python -m venv venv  
venv\Scripts\activate  

Mac/Linux:
python3 -m venv venv  
source venv/bin/activate  

---

### 4️⃣ Install Dependencies

pip install -r requirements.txt  

---

### 5️⃣ Configure API Key

Create a `.env` file in root directory:

GROQ_API_KEY=your_api_key_here  

OR set environment variable:

Windows:
set GROQ_API_KEY=your_api_key_here  

Mac/Linux:
export GROQ_API_KEY=your_api_key_here  

---

### 6️⃣ Run Application

streamlit run app.py  

Open in browser:
http://localhost:8501  

---

## 📌 Example Queries

- Show headcount by year  
- Give attrition rate by department  
- Show salary comparison by region  
- Predict attrition risk  
- Explain attrition rate  
- Zeigen Sie die Mitarbeiterzahl pro Jahr  

---

## 🔐 Security & Data Notes

- This repository uses dummy HR data only  
- No real employee data included  
- API keys excluded from repository  
- `.env` file not committed for security  
- Designed to avoid LLM-generated numerical hallucinations  

---

## 🎓 Academic / Evaluation Notes

This system demonstrates:

- Hybrid AI system design  
- Deterministic analytics enforcement  
- LLM-first NLU with fallback safety  
- Performance optimization via caching  
- Confidence-based intent validation  
- Domain-restricted assistant architecture  

---

## 📈 Performance Optimizations

- Dataset caching (LRU)  
- Intent caching to reduce API calls  
- Confidence-based fallback  
- Explicit chart detection  
- Structured logging for debugging  

---

## 🏁 Summary

HR-GPT 3.0 is not a generic chatbot.  
It is a controlled, domain-restricted HR Analytics Copilot combining:

- Business Intelligence  
- Machine Learning  
- Natural Language Understanding  
- Secure Architecture Design  
