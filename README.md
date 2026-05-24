# 🧠 Coofy AI — Ecommerce Deal Intelligence Platform

> **Advanced AI-powered ecommerce deal intelligence platform that detects fake discounts, ranks deals, and provides trust scoring.**

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=flat-square&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41-red?style=flat-square&logo=streamlit)
![Groq](https://img.shields.io/badge/Groq_AI-llama--3.3--70b-purple?style=flat-square)

---

## 🎯 What is Coofy AI?

Coofy AI is a **production-grade AI application** that analyzes ecommerce product pages and multi-product listing pages to:

- 🔍 **Detect the BEST deals** — AI ranks products from best to worst value
- 🚨 **Identify fake discounts** — Spots inflated MRPs and deceptive pricing
- 🛡️ **Detect scam patterns** — Urgency manipulation, misleading offers
- 📊 **Analyze trustworthiness** — AI trust scores from 0-100
- ⚖️ **Compare products** — Side-by-side deal analysis
- 🏆 **Rank deals intelligently** — TOP 5 best deals highlighted

This is NOT a simple chatbot. This is:
- A **pricing intelligence engine**
- An **ecommerce fraud detector**
- An **AI shopping copilot**
- A **deal ranking platform**

---

## 🏗️ Architecture

```
User enters ecommerce URL
        ↓
FastAPI backend receives request
        ↓
Selenium launches headless Chrome
        ↓
Dynamic page renders fully (JS, lazy-load)
        ↓
BeautifulSoup extracts & cleans content
        ↓
AI agent (Groq/LLaMA 3.3 70B) analyzes ALL products
        ↓
AI ranks best deals, detects fakes
        ↓
Structured JSON returned
        ↓
Streamlit renders futuristic dashboard
```

---

## 📁 Project Structure

```
coofy_ai/
│
├── agents/
│   ├── planner.py          # Pipeline orchestrator
│   └── validator.py         # AI deal analysis agent (Groq)
│
├── tools/
│   ├── scraper.py           # Selenium + BS4 web scraper
│   └── parser.py            # Content parser & platform detector
│
├── models/
│   └── schemas.py           # Pydantic data models
│
├── app/
│   ├── api.py               # FastAPI backend (/analyze endpoint)
│   └── streamlit_app.py     # Streamlit frontend (futuristic UI)
│
├── evals/
│   └── benchmark.py         # Evaluation & testing suite
│
├── .env                     # API keys (GROQ_API_KEY)
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, FastAPI |
| **Frontend** | Streamlit |
| **AI Model** | Groq API — `llama-3.3-70b-versatile` |
| **Scraping** | Selenium, BeautifulSoup, webdriver-manager |
| **Data Validation** | Pydantic |
| **Config** | python-dotenv |

---

## 🚀 Installation

### Prerequisites
- Python 3.11+
- Google Chrome installed
- Free Groq API key from [console.groq.com](https://console.groq.com/keys)

### Step 1: Clone / Navigate to Project

```bash
cd coofy_ai
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure API Key

Edit the `.env` file and add your **Groq API key**:

```env
GROQ_API_KEY=gsk_your_actual_api_key_here
```

> 🔑 Get your FREE key at: https://console.groq.com/keys

---

## ▶️ Running the Application

### Terminal 1 — Start Backend

```bash
uvicorn app.api:app --reload
```

The API will be available at: `http://localhost:8000`  
Swagger docs at: `http://localhost:8000/docs`

### Terminal 2 — Start Frontend

```bash
streamlit run app/streamlit_app.py
```

The dashboard will open at: `http://localhost:8501`

---

## 🧪 Running Benchmarks

```bash
python -m evals.benchmark
```

This tests the pipeline against real ecommerce URLs and generates `evals/benchmark_results.json`.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/health` | Detailed health status |
| `GET` | `/analyze?url=<URL>` | Analyze ecommerce URL |

### Example API Call

```bash
curl "http://localhost:8000/analyze?url=https://www.amazon.in/s?k=laptops"
```

### Response Format

```json
{
  "success": true,
  "url": "...",
  "platform": "Amazon",
  "page_type": "Multi-Product Listing",
  "analysis_time_seconds": 15.2,
  "total_products_found": 5,
  "top_deals": [
    {
      "product_name": "HP Laptop 15s",
      "original_price": "₹65,000",
      "discounted_price": "₹45,999",
      "estimated_discount_percentage": 29,
      "deal_quality_rating": "HOT DEAL",
      "trust_score": 87,
      "suspicious": false,
      "reasons": "Genuine discount from reputed brand...",
      "pros": "Good specs, trusted brand, real discount",
      "cons": "Could find better during sales",
      "final_verdict": "Buy Now",
      "summary": "Excellent value HP laptop with genuine 29% discount"
    }
  ]
}
```

---

## 🌐 Supported Platforms

| Platform | Single Product | Multi-Product Listing |
|----------|:-:|:-:|
| Amazon India | ✅ | ✅ |
| Flipkart | ✅ | ✅ |
| Myntra | ✅ | ✅ |
| Generic ecommerce | ✅ | ✅ |

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ChromeDriver not found` | Install Google Chrome. webdriver-manager handles the driver automatically. |
| `GROQ_API_KEY not found` | Make sure `.env` has your key and you're running from the `coofy_ai/` directory. |
| `Connection refused` on Streamlit | Start the FastAPI backend first: `uvicorn app.api:app --reload` |
| `Timeout errors` | Some sites block headless browsers. Try different URLs. |
| `Empty results` | The site might use anti-bot measures. Try Amazon or Flipkart listing pages. |

---

## 📸 Screenshots

> _Add screenshots of the running application here_

---

## 📄 License

This project was built for educational and interview purposes.

---

<p align="center">
  <strong>🧠 Coofy AI</strong> — Built like a startup. Made for interviews.<br>
  <em>Powered by Groq AI · FastAPI · Streamlit · Selenium</em>
</p>
