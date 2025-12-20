# 🚀 HR-GPT 3.0 — Multilingual AI-Powered HR Analytics Assistant  

HR-GPT 3.0 is an AI-powered conversational HR analytics assistant built using **Streamlit, LLM models, Pandas, Plotly, and Machine Learning**.  

It allows users to chat with HR data, generate dynamic charts, obtain HR insights, download analytics, and get multilingual responses — just like ChatGPT but specialized for HR.

---

## ✨ Key Features  

### 💬 Conversational HR Assistant  
Ask questions such as:  
- What is HR analytics?  
- Explain performance management.  

### 🌍 Multilingual Support  
Respond in European languages.  

### 📊 HR Analytics Metrics  
- Headcount  
- Attrition  
- Salary benchmarking  
- Gender distribution  
- Engagement scores  

### 📈 Dynamic Visualizations  
Supports flexible charting:
- Bar charts  
- Pie charts  
- Line charts  
- Histograms  
With grouping such as:
- Gender  
- Department  
- Job level  
- Location  

Every chart can be **downloaded as CSV**.

### 🤖 Machine Learning Models  
Trained to support:  
1. Attrition Prediction  
2. Salary Estimation  
3. Performance Rating Prediction  
4. Promotion Recommendation  
5. Workforce Forecasting  

### 🧠 LLM Knowledge Responses  
Get HR theory, definitions, and explanations.

---

## 🏗 Tech Stack  

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| LLM Backend | Groq / OpenAI |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly |
| Machine Learning | Scikit-Learn |
| Forecasting | Prophet / Statsmodels |

---

## 📂 Project Structure  

HR_BOT_3.0/
│ app.py
│ config.py
│ requirements.txt
│ README.md
│
├─ data/
│ └─ hr_master_10000.csv
│
├─ modules/
│ ├─ nlu.py
│ ├─ charts.py
│ ├─ analytics.py
│ ├─ analytics_router.py
│ ├─ llm_engine.py
│ └─ ...
│
├─ ml/
│ └─ train_all_models.py
│
├─ models/
│ └─ *.pkl (ignored by git)



---

## ⚙️ Installation  

Clone the repository:


---

## 🔐 API Keys  

Add your LLM API keys inside:


Example:
```py
GROQ_API_KEY = "your-key"
OPENAI_API_KEY = "optional"
