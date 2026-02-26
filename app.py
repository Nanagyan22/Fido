import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import pandas as pd
import base64
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Fido Analytics Portal", layout="wide", initial_sidebar_state="collapsed")

# --- BRAND STYLING (FIDO COLORS) ---
# Primary: #D6086B (Magenta), Secondary: #A3F8FF (Aqua), Light: #FFFFFF (White)
st.markdown("""
    <style>
    /* =========================================
       1. MAIN BANNER TEXT (Inside the Top Box) 
       ========================================= */
    .main-title {
        color: #FFFFFF !important; /* <-- CHANGE MAIN TITLE COLOR HERE */
        margin: 0; 
        padding: 0; 
        font-size: 2.2rem; 
        line-height: 1.2;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main-subtitle {
        color: #FFFFFF !important; /* <-- CHANGE SUBTITLE COLOR HERE */
        margin: 0; 
        padding-top: 5px; 
        font-size: 1.1rem; 
        font-weight: 500;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* =========================================
       2. STREAMLIT HEADERS (st.header)
       ========================================= */
    h1, h2 {
        color: #D6086B !important; /* <-- CHANGE NATIVE HEADER COLOR HERE */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* =========================================
       3. STREAMLIT SUBHEADERS (st.subheader)
       ========================================= */
    h3, h4 {
        color: #D6086B !important; /* <-- CHANGE NATIVE SUBHEADER COLOR HERE */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* =========================================
       4. GENERAL APP STYLING
       ========================================= */
    /* Horizontal Rule Gradient */
    hr {
        border: 0;
        height: 3px;
        background-image: linear-gradient(to right, #D6086B, #A3F8FF);
    }
    
    /* Alert / Info Boxes */
    .stAlert {
        background-color: rgba(214, 8, 107, 0.05) !important;
        color: #D6086B !important;
        border-left: 4px solid #D6086B;
    }
    
    /* Radio Buttons */
    div.row-widget.stRadio > div {
        flex-direction: row;
        background-color: #FFFFFF;
        padding: 8px;
        border-radius: 8px;
        border: 2px solid #A3F8FF;
    }
    
    /* Sample Questions */
    .sample-q {
        font-size: 0.95rem;
        color: #D6086B;
        font-weight: 600;
        margin-bottom: 4px;
        padding-left: 10px;
        border-left: 2px solid #A3F8FF;
    }
    
    /* Main Header Container */
    .main-header {
        background-color: #D6086B; 
        padding: 25px; 
        border-radius: 12px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.15); 
        display: flex; 
        align-items: center; 
        gap: 25px; 
        margin-bottom: 25px;
        border-top: 5px solid #A3F8FF;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    try:
        # Load the loan summary data
        summary_df = pd.read_csv("Data summary.csv")
        return summary_df
    except Exception as e:
        return None

summary_df = load_data()

# --- PRE-CALCULATE AGGREGATIONS FOR AI ---
data_context = ""
if summary_df is not None:
    total_disbursed = summary_df['total_loans_disbursed'].sum()
    total_received = summary_df['total_loans_received'].sum()
    total_outstanding = summary_df['total_outstanding_loans'].sum()
    top_3_portfolios = summary_df[summary_df['portfolio_rank'] <= 3][['cohort', 'loan_recovery_rate_pct', 'loss_rate']]
    
    data_context = f"""
    PRE-CALCULATED LOAN AGGREGATIONS:
    - Total Overall Disbursed: GHS {total_disbursed:,.2f}
    - Total Overall Received: GHS {total_received:,.2f}
    - Total Overall Outstanding: GHS {total_outstanding:,.2f}
    
    TOP 3 BEST PERFORMING COHORTS:
    {top_3_portfolios.to_string(index=False)}
    """

# --- LOGO HANDLING ---
def get_image_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

logo_b64 = get_image_base64("logo.png")

if logo_b64:
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height: 60px; object-fit: contain; background-color: #FFFFFF; padding: 10px; border-radius: 8px; border: 2px solid #A3F8FF;">'
else:
    logo_html = '<span style="font-size: 3rem; background-color: #FFFFFF; padding: 5px; border-radius: 8px;">💳</span>'

# --- UI HEADER ---
st.markdown(f"""
<div class="main-header">
    <div>{logo_html}</div>
    <div>
        <h1 class="main-title">Fido Loan Portfolio & KYC Analytics</h1>
        <p class="main-subtitle">Data Analysis Assessment | By Gloria Odamten</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- TABS ---
tab1, tab2 = st.tabs(["📊 Interactive Dashboard & AI", "📄 Executive Insights & KYC Funnel"])

with tab1:
    col_dash, col_chat = st.columns([2.3, 1])

    with col_dash:
        view_selection = st.radio(
            "Toggle View:", 
            ["📈 Power BI Loan Portfolio", "📉 Raw Data Table"]
        )
        
        if view_selection == "📈 Power BI Loan Portfolio":
            st.subheader("Financial Cohort Performance")
            pbi_iframe = """
            <iframe title="Fido - Assessment_Dashboard" 
            width="100%" height="650" 
            src="https://app.powerbi.com/view?r=eyJrIjoiMzZlNzRlOWQtMGJiMS00NmEwLWJiMzQtM2VlNTgxYmEwMzE1IiwidCI6IjhkMWE2OWVjLTAzYjUtNDM0NS1hZTIxLWRhZDExMmY1ZmI0ZiIsImMiOjN9" 
            frameborder="0" allowFullScreen="true" style="border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"></iframe>
            """
            components.html(pbi_iframe, height=660)
        else:
            st.subheader("Raw Cohort Aggregations")
            st.info("This is the underlying data model driving the Power BI visual matrix.")
            if summary_df is not None:
                st.dataframe(summary_df, use_container_width=True, height=600)
            else:
                st.error("Missing 'Data summary.csv'. Please ensure it is in the root directory.")

    # --- AI CHATBOT SECTION ---
    with col_chat:
        st.subheader("🤖 Fido Data Assistant")
        st.info("Ask me about portfolio performance, the Top 3 cohorts, or the KYC drop-off analysis.")
        
        st.markdown("**💡 Try asking:**")
        st.markdown("<p class='sample-q'>1. Which are the top 3 best loan portfolios?</p>", unsafe_allow_html=True)
        st.markdown("<p class='sample-q'>2. What is the total outstanding loan balance?</p>", unsafe_allow_html=True)
        st.markdown("<p class='sample-q'>3. What happened to the KYC Funnel around June 26?</p>", unsafe_allow_html=True)
        st.markdown("<p class='sample-q'>4. How should we investigate the Liveness Check drop-off?</p>", unsafe_allow_html=True)
        st.write("")
        
        system_instruction = f"""
        You are the Senior Data Assistant for Fido, built by Data Analyst Gloria Odamten.
        You have complete knowledge of the Loan Portfolio Power BI dashboard and the KYC Funnel analysis.
        
        KYC FUNNEL ANALYSIS (PART 2 KNOWLEDGE):
        - Observation: Around June 26, the 3rd-party KYC success rate trended UP (Graph 2), but the Verification Completed view trended DOWN (Graph 1).
        - Possible Reasons: 
            1. An update to the Liveness V2 SDK made it stricter, causing genuine users to fail or abandon the flow before hitting the 3rd party.
            2. The 3rd party API improved their pass rate for *submitted* images, but our internal UI bug prevented users from successfully submitting them.
            3. Network timeouts or latency issues between the Liveness End step and the Verification Completed view.
        - Investigation Steps: 
            1. Query API error logs between Step 3 (Liveness End) and Step 4 (Verification).
            2. Segment the drop-off data by Device Type (iOS vs Android) and App Version.
            3. Check average session time between Liveness Start and Liveness End to see if users are getting stuck.

        LOAN PORTFOLIO (PART 1 KNOWLEDGE):
        {data_context}
        
        Always answer as Gloria's highly analytical AI assistant. Be concise. Use Fido's business context. If asked to rank the best portfolios, cite the Top 3 from the PRE-CALCULATED LOAN AGGREGATIONS.
        """
        
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! I am Gloria's AI Assistant. I have analyzed the Fido loan cohorts and the KYC funnel anomalies. How can I help you today?"}
            ]

        chat_container = st.container(height=360)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if prompt := st.chat_input("Ask about KPIs, portfolios, or the KYC funnel..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    
                    if not available_models:
                        bot_reply = "Error: Your API key is active, but it does not have access to any generation models. Check your Google AI Studio account."
                    else:
                        model_name = next((m for m in available_models if '1.5-flash' in m), available_models[0])
                        
                        model = genai.GenerativeModel(model_name)
                        
                        full_prompt = f"SYSTEM KNOWLEDGE & INSTRUCTIONS:\n{system_instruction}\n\n"
                        full_prompt += "--- CURRENT CONVERSATION ---\n"
                        full_prompt += "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                        
                        response = model.generate_content(full_prompt)
                        bot_reply = response.text
                        
                except Exception as e:
                    bot_reply = f"System Error: {e}"
                
                with st.chat_message("assistant"):
                    st.markdown(bot_reply)
            
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})

# --- TAB 2: EXECUTIVE REPORT ---
with tab2:
    st.header("Executive Summary: Portfolio & Funnel Diagnostics")
    st.write("This section synthesizes the findings from the 7-year loan portfolio analysis (Part 1) and the KYC onboarding anomaly (Part 2).")
    
    st.divider()
    
    col_insight1, col_insight2 = st.columns(2)
    
    with col_insight1:
        st.subheader("💰 Part 1: Loan Portfolio Health")
        st.write("**Top Performers:** By grouping data into monthly cohorts, we identified the top 3 best-performing portfolios based on recovery and low default rates. (e.g., Aug 2020).")
        st.write("**Risk vs. Volume:** The Power BI dashboard highlights that while total disbursements scaled, certain cohorts carried disproportionate loss rates, signaling a need to tighten credit criteria during specific economic windows.")
        st.info("**Action:** Align marketing acquisition strategies to mirror the customer profiles from our Top 3 ranking cohorts.")
        
    with col_insight2:
        st.subheader("📉 Part 2: The June 26 KYC Anomaly")
        st.write("**The Incident:** Around June 26, the 3rd-party success rate spiked, yet actual completed verifications dropped. This indicates a localized failure in the 'Liveness' stage of the onboarding funnel.")
        st.write("**Root Cause Hypothesis:** A strict update to the Liveness V2 parameters or a UI latency issue is causing users to abandon the app *before* their data is sent to the 3rd party for final verification.")
        st.info("**Action:** Pull API error logs between `Liveness - V2 - end` and `Verification Completed` and segment drop-offs by device OS.")

    st.divider()
    
    st.subheader("🚀 Next Steps for Data Strategy")
    st.markdown("""
    1. **Implement Cohort Monitoring:** Set up automated alerts in Power BI when any new monthly cohort's `loss_rate` exceeds the historical average of the top 5 portfolios.
    2. **Funnel Telemetry:** Introduce micro-event tracking inside the Liveness V2 screen to capture *where* users are failing (e.g., poor lighting, timeout, camera permission denial).
    3. **A/B Testing:** Roll back Liveness parameters to pre-June 26 levels for a control group of users to isolate the variable causing the drop-off.
    """)