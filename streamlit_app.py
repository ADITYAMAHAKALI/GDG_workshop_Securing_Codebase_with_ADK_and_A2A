# streamlit_app.py

import streamlit as st
import time
from io import BytesIO
from orchestrator import run_scan_sync

st.set_page_config(
    page_title="🛡️ ADK + A2A Repo Security Scanner",
    page_icon="🧠",
    layout="wide",
)

# --- Title + Intro ---
st.markdown("<h1 style='text-align: center;'>🛡️ Securing Your Codebase with ADK + A2A + Gemini</h1>",
            unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align:center; color:gray;'>
    <b>3-Agent Security Pipeline:</b>  
    Scanner → Analyzer → Reporter  
    powered by <b>Google Agent Development Kit</b>, <b>Agent2Agent</b> protocol, and <b>Gemini</b> models.
    </div>
    """,
    unsafe_allow_html=True,
)
st.divider()

# --- Input Section ---
st.subheader("🔍 Scan a GitHub Repository")

with st.expander("ℹ️ Instructions", expanded=False):
    st.markdown("""
    - Start your **three agents**:
      - `scanner_agent` → port **8001**
      - `analyzer_agent` → port **8002**
      - `reporter_agent` → port **8003**
    - Enter a public GitHub repo URL (use your sample vulnerable repo for the demo)
    - Click **Run Scan** to trigger the full 3-agent pipeline  
    """)

default_url = "https://github.com/ADITYAMAHAKALI/gdg-vuln-sample-repo"
repo_url = st.text_input(
    "🔗 GitHub Repository URL",
    value=default_url,
    placeholder="https://github.com/owner/repo",
)

run_button = st.button("🚀 Run Scan", use_container_width=True)

# --- Main Scan Logic ---
if run_button:
    if not repo_url.strip():
        st.error("⚠️ Please enter a GitHub repository URL.")
    else:
        with st.spinner("🧠 Scanning your repository using 3-agent pipeline..."):
            try:
                start_time = time.time()
                report_md = run_scan_sync(repo_url.strip())
                end_time = time.time()

                st.success(
                    f"✅ Scan complete! (took {end_time - start_time:.1f}s)")

                with st.expander("📜 View Security Report (Markdown)", expanded=True):
                    st.markdown(report_md)

                # --- Download section ---
                st.download_button(
                    label="💾 Download Markdown Report",
                    data=BytesIO(report_md.encode("utf-8")),
                    file_name=f"security_report_{repo_url.split('/')[-1]}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

            except Exception as e:
                st.error(f"❌ Scan failed: {e}")
                st.info(
                    "Tip: Check if all agents (8001, 8002, 8003) are running properly.")
