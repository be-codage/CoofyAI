"""
Coofy AI — Streamlit Frontend
===============================
Modern AI startup-grade dashboard with futuristic dark theme,
glassmorphism cards, neon accents, and animated loading states.

Run with: streamlit run app/streamlit_app.py
"""

# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
import streamlit.components.v1 as components  # ← ADDED
import requests
import time
import json
from urllib.parse import urlparse

# ---------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Coofy AI — Ecommerce Deal Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------
# Backend URL
# ---------------------------------------------------------------
BACKEND_URL = "https://coofyai.onrender.com"

# ---------------------------------------------------------------
# Custom CSS — Futuristic Dark Theme
# ---------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #12121a;
    --bg-card: rgba(18, 18, 30, 0.7);
    --bg-glass: rgba(255, 255, 255, 0.03);
    --border-color: rgba(255, 255, 255, 0.06);
    --text-primary: #e8e8ed;
    --text-secondary: #8b8b9e;
    --text-muted: #5a5a6e;
    --accent-primary: #7c5bf5;
    --accent-secondary: #5eead4;
    --accent-pink: #f472b6;
    --accent-orange: #fb923c;
    --accent-red: #ef4444;
    --accent-green: #22c55e;
    --gradient-primary: linear-gradient(135deg, #7c5bf5, #5eead4);
    --gradient-hot: linear-gradient(135deg, #f472b6, #fb923c);
    --gradient-danger: linear-gradient(135deg, #ef4444, #fb923c);
    --shadow-glow: 0 0 30px rgba(124, 91, 245, 0.15);
    --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.3);
    --radius: 16px;
    --radius-sm: 10px;
}

.stApp {
    background-color: var(--bg-primary) !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
    color: var(--text-primary) !important;
}

#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}

.hero-container {
    text-align: center;
    padding: 3rem 1rem 2rem;
    position: relative;
}

.hero-badge {
    display: inline-block;
    background: rgba(124, 91, 245, 0.12);
    border: 1px solid rgba(124, 91, 245, 0.25);
    color: #a78bfa;
    padding: 6px 18px;
    border-radius: 50px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
}

.hero-title {
    font-size: 3.6rem;
    font-weight: 900;
    background: linear-gradient(135deg, #7c5bf5 0%, #5eead4 50%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.8rem;
    letter-spacing: -1.5px;
    animation: gradientShift 6s ease-in-out infinite;
    background-size: 200% 200%;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.hero-subtitle {
    font-size: 1.15rem;
    color: var(--text-secondary);
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.65;
    font-weight: 400;
}

.hero-subtitle strong { color: var(--accent-secondary); font-weight: 600; }

.stTextInput > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius) !important;
    padding: 2px !important;
    transition: all 0.3s ease;
}

.stTextInput > div > div:focus-within {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 20px rgba(124, 91, 245, 0.2) !important;
}

.stTextInput input {
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    padding: 14px 18px !important;
    background: transparent !important;
}

.stTextInput input::placeholder { color: var(--text-muted) !important; }

.stButton > button {
    background: var(--gradient-primary) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: 14px 40px !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: 0.3px;
    cursor: pointer;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(124, 91, 245, 0.3) !important;
    width: 100%;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(124, 91, 245, 0.45) !important;
}

.stats-bar {
    display: flex;
    justify-content: center;
    gap: 2rem;
    padding: 1.2rem;
    margin: 1.5rem 0;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius);
    backdrop-filter: blur(12px);
    flex-wrap: wrap;
}

.stat-item { text-align: center; }

.stat-value {
    font-size: 1.6rem;
    font-weight: 800;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-label {
    font-size: 0.72rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
    margin-top: 2px;
}

.loading-container { text-align: center; padding: 3rem 1rem; }
.loading-title { font-size: 1.4rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem; }
.loading-subtitle { color: var(--text-secondary); font-size: 0.95rem; margin-bottom: 2rem; }
.loading-step { display: flex; align-items: center; gap: 12px; padding: 10px 0; color: var(--text-secondary); font-size: 0.9rem; max-width: 400px; margin: 0 auto; text-align: left; }
.loading-step.active { color: var(--accent-primary); font-weight: 600; }
.loading-step.done { color: var(--accent-green); }

.error-card { background: rgba(239, 68, 68, 0.06); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: var(--radius); padding: 2rem; text-align: center; margin: 1rem 0; }
.error-title { font-size: 1.2rem; font-weight: 700; color: #ef4444; margin-bottom: 0.5rem; }
.error-text { color: var(--text-secondary); font-size: 0.9rem; line-height: 1.6; }

.footer { text-align: center; padding: 3rem 1rem; color: var(--text-muted); font-size: 0.8rem; border-top: 1px solid var(--border-color); margin-top: 3rem; }
.footer a { color: var(--accent-primary); text-decoration: none; }

@media (max-width: 768px) {
    .hero-title { font-size: 2.2rem; }
    .stats-bar { gap: 1rem; }
}

.block-container { padding-top: 1rem !important; max-width: 900px !important; }

.stTabs [data-baseweb="tab-list"] { gap: 2px; background: var(--bg-card); border-radius: var(--radius); padding: 4px; border: 1px solid var(--border-color); }
.stTabs [data-baseweb="tab"] { color: var(--text-secondary) !important; border-radius: var(--radius-sm); font-weight: 600; font-size: 0.85rem; }
.stTabs [aria-selected="true"] { background: rgba(124, 91, 245, 0.15) !important; color: var(--accent-primary) !important; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------

def get_badge_class(rating: str) -> str:
    rating_lower = rating.lower().strip() if rating else ""
    if "hot" in rating_lower:       return "badge-hot"
    elif "good" in rating_lower:    return "badge-good"
    elif "fair" in rating_lower:    return "badge-fair"
    elif "risky" in rating_lower:   return "badge-risky"
    elif "suspicious" in rating_lower: return "badge-suspicious"
    return "badge-fair"


def get_trust_color(score: float) -> str:
    if score >= 80:   return "#22c55e"
    elif score >= 50: return "#fb923c"
    else:             return "#ef4444"


def shorten_url(url: str, max_path: int = 45) -> str:
    try:
        parsed = urlparse(url)
        path = parsed.path
        if len(path) > max_path:
            path = path[:max_path] + "…"
        return parsed.netloc + path
    except Exception:
        return url[:60]


def render_deal_card(deal: dict, rank: int) -> None:
    """
    Render a deal card using st.components.v1.html so the HTML
    is always rendered properly — never shown as raw text.
    """
    name         = deal.get("product_name", "Unknown Product")
    product_url  = deal.get("product_url") or ""
    original     = deal.get("original_price", "N/A")
    discounted   = deal.get("discounted_price", "N/A")
    discount_pct = deal.get("estimated_discount_percentage", 0)
    rating       = deal.get("deal_quality_rating", "Unknown")
    trust        = deal.get("trust_score", 0)
    suspicious   = deal.get("suspicious", False)
    reasons      = deal.get("reasons", "N/A")
    pros         = deal.get("pros", "N/A")
    cons         = deal.get("cons", "N/A")
    verdict      = deal.get("final_verdict", "N/A")

    badge_class  = get_badge_class(rating)
    trust_color  = get_trust_color(trust)

    suspicious_badge = (
        '<span class="badge badge-warning">⚠ Suspicious</span>'
        if suspicious
        else '<span class="badge badge-safe">✓ Safe</span>'
    )

    if product_url and product_url.startswith("http"):
        display_url = shorten_url(product_url)
        link_html   = f'<a class="product-link" href="{product_url}" target="_blank">🔗 {display_url} ↗</a>'
        cta_html    = f'<a class="cta-btn" href="{product_url}" target="_blank">🛒 View Product ↗</a>'
    else:
        link_html = ""
        cta_html  = ""

    rank_capped = min(rank, 5)

    # ── Full self-contained HTML+CSS per card ──────────────────────────────
    # Using components.v1.html so Streamlit NEVER treats this as plain text.
    # Each card carries its own <style> block — no dependency on the parent page.
    card_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
      * {{ box-sizing: border-box; margin: 0; padding: 0; }}
      body {{ background: transparent; font-family: 'Inter', sans-serif; padding: 4px 2px 8px 2px; }}

      .deal-card {{
        background: rgba(18, 18, 30, 0.95);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
        transition: border-color 0.3s;
      }}
      .deal-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(135deg, #7c5bf5, #5eead4);
      }}

      .deal-rank {{
        position: absolute;
        top: 1rem; right: 1rem;
        width: 36px; height: 36px;
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 0.9rem; color: white;
      }}
      .rank-1 {{ background: linear-gradient(135deg, #f59e0b, #f97316); }}
      .rank-2 {{ background: linear-gradient(135deg, #8b5cf6, #6366f1); }}
      .rank-3 {{ background: linear-gradient(135deg, #06b6d4, #0ea5e9); }}
      .rank-4, .rank-5 {{ background: linear-gradient(135deg, #64748b, #475569); }}

      .product-name {{
        font-size: 1.1rem; font-weight: 700;
        color: #e8e8ed;
        padding-right: 50px;
        line-height: 1.4;
        margin-bottom: 0.3rem;
      }}

      .product-link {{
        display: inline-block;
        font-size: 0.78rem;
        color: #7c5bf5;
        text-decoration: none;
        margin-bottom: 0.8rem;
        opacity: 0.85;
        word-break: break-all;
      }}
      .product-link:hover {{ opacity: 1; text-decoration: underline; }}

      .deal-prices {{
        display: flex; align-items: center;
        gap: 12px; flex-wrap: wrap;
        margin-bottom: 0.9rem;
      }}
      .price-discounted {{ font-size: 1.5rem; font-weight: 800; color: #5eead4; }}
      .price-original {{ font-size: 1rem; color: #5a5a6e; text-decoration: line-through; }}
      .discount-badge {{
        background: rgba(34,197,94,0.12); color: #22c55e;
        padding: 4px 10px; border-radius: 6px;
        font-size: 0.8rem; font-weight: 700;
      }}

      .badge {{
        display: inline-block; padding: 5px 14px;
        border-radius: 8px; font-size: 0.75rem;
        font-weight: 700; letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-right: 8px; margin-bottom: 6px;
      }}
      .badge-hot {{ background: rgba(244,114,182,0.15); color: #f472b6; border: 1px solid rgba(244,114,182,0.3); }}
      .badge-good {{ background: rgba(94,234,212,0.1); color: #5eead4; border: 1px solid rgba(94,234,212,0.25); }}
      .badge-fair {{ background: rgba(251,146,60,0.1); color: #fb923c; border: 1px solid rgba(251,146,60,0.25); }}
      .badge-risky {{ background: rgba(251,146,60,0.12); color: #f97316; border: 1px solid rgba(251,146,60,0.3); }}
      .badge-suspicious {{ background: rgba(239,68,68,0.12); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }}
      .badge-safe {{ background: rgba(34,197,94,0.1); color: #22c55e; border: 1px solid rgba(34,197,94,0.25); }}
      .badge-warning {{ background: rgba(239,68,68,0.1); color: #ef4444; border: 1px solid rgba(239,68,68,0.25); }}

      .trust-row {{
        display: flex; align-items: center;
        gap: 10px; margin: 0.8rem 0;
      }}
      .trust-lbl {{ font-size: 0.72rem; color: #5a5a6e; font-weight: 600; letter-spacing: 1px; }}
      .trust-track {{
        flex: 1; height: 8px;
        background: rgba(255,255,255,0.06);
        border-radius: 10px; overflow: hidden;
      }}
      .trust-fill {{ height: 100%; border-radius: 10px; }}
      .trust-val {{ font-size: 0.85rem; font-weight: 600; min-width: 30px; text-align: right; }}

      .insights {{
        display: grid; grid-template-columns: 1fr 1fr;
        gap: 10px; margin-top: 1rem;
      }}
      .insight-box {{
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 10px; padding: 0.8rem;
      }}
      .insight-lbl {{
        font-size: 0.7rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 1px;
        color: #5a5a6e; margin-bottom: 4px;
      }}
      .insight-txt {{ font-size: 0.84rem; color: #8b8b9e; line-height: 1.5; }}

      .ai-box {{ margin-top: 0.8rem; }}

      .verdict {{
        font-size: 0.92rem; color: #5eead4; font-weight: 600;
        margin-top: 0.8rem; padding: 0.6rem 0.8rem;
        background: rgba(94,234,212,0.06);
        border-left: 3px solid #5eead4;
        border-radius: 0 8px 8px 0;
      }}

      .cta-btn {{
        display: inline-block; margin-top: 1rem;
        padding: 10px 22px;
        background: linear-gradient(135deg, #7c5bf5, #5eead4);
        color: white; border-radius: 10px;
        font-size: 0.88rem; font-weight: 700;
        text-decoration: none; letter-spacing: 0.3px;
      }}
      .cta-btn:hover {{ opacity: 0.88; }}

      @media (max-width: 500px) {{ .insights {{ grid-template-columns: 1fr; }} }}
    </style>
    </head>
    <body>
      <div class="deal-card">
        <div class="deal-rank rank-{rank_capped}">#{rank}</div>
        <div class="product-name">{name}</div>

        {link_html}

        <div class="deal-prices">
          <span class="price-discounted">{discounted}</span>
          <span class="price-original">{original}</span>
          <span class="discount-badge">↓ {discount_pct:.0f}% OFF</span>
        </div>

        <div>
          <span class="badge {badge_class}">{rating}</span>
          {suspicious_badge}
        </div>

        <div class="trust-row">
          <span class="trust-lbl">TRUST</span>
          <div class="trust-track">
            <div class="trust-fill" style="width:{trust:.0f}%; background:{trust_color};"></div>
          </div>
          <span class="trust-val" style="color:{trust_color};">{trust:.0f}</span>
        </div>

        <div class="insights">
          <div class="insight-box">
            <div class="insight-lbl">✅ Pros</div>
            <div class="insight-txt">{pros}</div>
          </div>
          <div class="insight-box">
            <div class="insight-lbl">⚠️ Cons</div>
            <div class="insight-txt">{cons}</div>
          </div>
        </div>

        <div class="ai-box">
          <div class="insight-lbl" style="margin-bottom:4px;">🧠 AI Analysis</div>
          <div class="insight-txt">{reasons}</div>
        </div>

        <div class="verdict">🎯 {verdict}</div>

        {cta_html}
      </div>
    </body>
    </html>
    """
    # height auto-sizes to card content; scrolling=False removes the iframe scrollbar
    components.html(card_html, height=520, scrolling=False)


# ---------------------------------------------------------------
# HERO SECTION
# ---------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">🧠 AI-Powered Deal Intelligence</div>
    <h1 class="hero-title">Coofy AI</h1>
    <p class="hero-subtitle">
        The smartest ecommerce copilot. Paste any product link — we'll
        <strong>detect fake discounts</strong>, <strong>rank deals</strong>,
        and give you an <strong>AI trust score</strong> in seconds.
    </p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------
# INPUT SECTION
# ---------------------------------------------------------------
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    url_input = st.text_input(
        label="Enter URL",
        placeholder="🔗  Paste any Amazon, Flipkart, or Myntra URL...",
        label_visibility="collapsed",
        key="url_input",
    )
    analyze_clicked = st.button("🚀  Analyze Deals", use_container_width=True, key="analyze_btn")


# ---------------------------------------------------------------
# ANALYSIS FLOW
# ---------------------------------------------------------------
if analyze_clicked and url_input:

    loading_placeholder = st.empty()

    stages = [
        ("🚀", "Launching browser engine..."),
        ("🌐", "Rendering ecommerce page..."),
        ("🔍", "Detecting products on page..."),
        ("🧠", "AI analyzing pricing patterns..."),
        ("📊", "Ranking deals & trust scores..."),
        ("✨", "Generating AI insights..."),
    ]

    for i, (icon, text) in enumerate(stages):
        steps_html = ""
        for j, (s_icon, s_text) in enumerate(stages):
            if j < i:
                steps_html += f'<div class="loading-step done">✅ {s_text}</div>'
            elif j == i:
                steps_html += f'<div class="loading-step active">⏳ {s_text}</div>'
            else:
                steps_html += f'<div class="loading-step">⬜ {s_text}</div>'

        loading_placeholder.markdown(f"""
        <div class="loading-container">
            <div class="loading-title">Analyzing deals...</div>
            <div class="loading-subtitle">Coofy AI is scanning the page with advanced AI</div>
            {steps_html}
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.6)

    try:
        response = requests.get(
            f"{BACKEND_URL}/analyze",
            params={"url": url_input},
            timeout=120,
        )

        loading_placeholder.empty()

        if response.status_code == 200:
            data = response.json()

            if data.get("success") and data.get("top_deals"):
                deals = data["top_deals"]

                avg_trust = sum(d.get("trust_score", 0) for d in deals) / len(deals) if deals else 0
                hot_deals = sum(1 for d in deals if "hot" in d.get("deal_quality_rating", "").lower())

                st.markdown(f"""
                <div class="stats-bar">
                    <div class="stat-item">
                        <div class="stat-value">{data.get('total_products_found', len(deals))}</div>
                        <div class="stat-label">Products Found</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{data.get('platform', 'Unknown')}</div>
                        <div class="stat-label">Platform</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{avg_trust:.0f}/100</div>
                        <div class="stat-label">Avg Trust Score</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">🔥 {hot_deals}</div>
                        <div class="stat-label">Hot Deals</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{data.get('analysis_time_seconds', 0):.1f}s</div>
                        <div class="stat-label">Analysis Time</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""
                <div style="text-align: center; margin: 2rem 0 1rem;">
                    <h2 style="font-size: 1.6rem; font-weight: 800; color: #e8e8ed; margin-bottom: 0.3rem;">
                        🏆 Top Ranked Deals
                    </h2>
                    <p style="color: #8b8b9e; font-size: 0.9rem;">
                        AI-analyzed and ranked from best to worst value
                    </p>
                </div>
                """, unsafe_allow_html=True)

                for idx, deal in enumerate(deals, 1):
                    render_deal_card(deal, idx)

                with st.expander("📄 View Raw JSON Response"):
                    st.json(data)

            else:
                error_msg = data.get("error", "No deals were found on this page.")
                st.markdown(f"""
                <div class="error-card">
                    <div class="error-title">⚠️ Analysis Issue</div>
                    <div class="error-text">{error_msg}<br><br>
                    <strong>Tips:</strong><br>
                    • Make sure the URL points to a valid ecommerce product or listing page<br>
                    • Try a different URL or product category<br>
                    • Some sites may block automated access
                    </div>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.markdown(f"""
            <div class="error-card">
                <div class="error-title">❌ Server Error ({response.status_code})</div>
                <div class="error-text">The backend returned an unexpected error.<br>
                Please make sure the FastAPI server is running at <code>{BACKEND_URL}</code></div>
            </div>
            """, unsafe_allow_html=True)

    except requests.exceptions.ConnectionError:
        loading_placeholder.empty()
        st.markdown(f"""
        <div class="error-card">
            <div class="error-title">🔌 Connection Error</div>
            <div class="error-text">
                Could not connect to the Coofy AI backend.<br><br>
                <strong>Start the backend first:</strong><br>
                <code>uvicorn app.api:app --reload</code><br><br>
                Make sure it's running at: <code>{BACKEND_URL}</code>
            </div>
        </div>
        """, unsafe_allow_html=True)

    except requests.exceptions.Timeout:
        loading_placeholder.empty()
        st.markdown("""
        <div class="error-card">
            <div class="error-title">⏱️ Timeout</div>
            <div class="error-text">
                The analysis took too long. This might happen with very large product pages.<br>
                Try a smaller listing page or a single product URL.
            </div>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        loading_placeholder.empty()
        st.markdown(f"""
        <div class="error-card">
            <div class="error-title">❌ Unexpected Error</div>
            <div class="error-text">{str(e)}</div>
        </div>
        """, unsafe_allow_html=True)

elif analyze_clicked and not url_input:
    st.markdown("""
    <div class="error-card">
        <div class="error-title">🔗 URL Required</div>
        <div class="error-text">Please paste an ecommerce URL above to start the analysis.</div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------
st.markdown("""
<div class="footer">
    <strong>Coofy AI</strong> — Ecommerce Deal Intelligence Platform<br>
    Built with FastAPI · Streamlit · Groq AI · Selenium<br>
    <span style="color: #7c5bf5;">Made for interviews. Built like a startup.</span>
</div>
""", unsafe_allow_html=True)