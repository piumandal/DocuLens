import os
import tempfile
from html import escape

import streamlit as st
from dotenv import load_dotenv
from google import genai


# ============================================================
# CONFIG
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="DocuLens — AI Document Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HELPERS
# ============================================================

def html(markup: str):
    """Render HTML safely.

    Markdown treats lines indented 4+ spaces as code blocks, and blank
    lines can end an HTML block early. So strip indentation and blank
    lines from every line before rendering.
    """
    cleaned = "\n".join(
        line.strip() for line in markup.strip().splitlines() if line.strip()
    )
    st.markdown(cleaned, unsafe_allow_html=True)


def section_card(title: str, content: str):
    """Card with an HTML heading and real Markdown content."""
    with st.container(border=True):
        html(f'<div class="section-heading">{title}</div>')
        st.markdown(content.strip() or "_Nothing found._")


# ============================================================
# CUSTOM CSS
# ============================================================

html(
    """
    <style>

    /* ---------- Global ---------- */

    .stApp {
        background: #f7f8fc;
    }

    .main .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* ---------- Sidebar ---------- */

    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #1f2937;
    }

    [data-testid="stSidebar"] * {
        color: #e5e7eb;
    }

    .sidebar-logo {
        font-size: 26px;
        font-weight: 800;
        color: white;
        margin-bottom: 5px;
    }

    .sidebar-subtitle {
        color: #9ca3af;
        font-size: 13px;
        margin-bottom: 30px;
    }

    .sidebar-section {
        color: #6b7280;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin: 25px 0 10px 0;
    }

    /* ---------- Header ---------- */

    .hero {
        background: linear-gradient(135deg, #ffffff 0%, #f3f4ff 100%);
        border: 1px solid #e5e7eb;
        border-radius: 24px;
        padding: 34px 38px;
        margin-bottom: 28px;
        box-shadow: 0 8px 30px rgba(15, 23, 42, 0.04);
    }

    .hero-badge {
        display: inline-block;
        background: #eef2ff;
        color: #4f46e5;
        border-radius: 999px;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 14px;
    }

    .hero-title {
        font-size: 42px;
        line-height: 1.1;
        font-weight: 800;
        color: #111827;
        margin: 0;
        padding: 0;
    }

    .hero-description {
        color: #6b7280;
        font-size: 16px;
        margin-top: 12px;
        max-width: 700px;
    }

    /* ---------- Cards ---------- */

    .card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 5px 20px rgba(15, 23, 42, 0.035);
        margin-bottom: 18px;
    }

    .card-title {
        font-size: 17px;
        font-weight: 750;
        color: #111827;
        margin-bottom: 6px;
    }

    .card-description {
        color: #6b7280;
        font-size: 13px;
        margin-bottom: 15px;
    }

    /* ---------- Upload ---------- */

    .upload-container {
        background: white;
        border: 2px dashed #c7d2fe;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin-bottom: 20px;
    }

    .upload-icon {
        font-size: 42px;
        margin-bottom: 10px;
    }

    .upload-title {
        font-size: 20px;
        font-weight: 750;
        color: #111827;
    }

    .upload-text {
        color: #6b7280;
        font-size: 14px;
    }

    /* ---------- File info ---------- */

    .file-card {
        display: flex;
        align-items: center;
        gap: 15px;
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 15px;
        margin: 12px 0 20px 0;
    }

    .file-icon {
        width: 45px;
        height: 45px;
        border-radius: 12px;
        background: #eef2ff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 23px;
    }

    .file-name {
        font-weight: 700;
        color: #111827;
    }

    .file-status {
        font-size: 12px;
        color: #10b981;
        margin-top: 3px;
    }

    /* ---------- Metric cards ---------- */

    .metric {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 18px;
        text-align: center;
    }

    .metric-number {
        font-size: 26px;
        font-weight: 800;
        color: #111827;
    }

    .metric-label {
        color: #6b7280;
        font-size: 12px;
    }

    /* ---------- Analysis ---------- */

    .analysis-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #111827;
        color: white;
        padding: 22px 25px;
        border-radius: 18px;
        margin: 28px 0 20px 0;
    }

    .analysis-title {
        font-size: 21px;
        font-weight: 750;
    }

    .analysis-subtitle {
        color: #9ca3af;
        font-size: 13px;
    }

    .section-heading {
        font-size: 19px;
        font-weight: 750;
        color: #111827;
        margin-bottom: 6px;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: white;
        border-radius: 18px;
    }

    /* ---------- Footer ---------- */

    .footer {
        text-align: center;
        color: #9ca3af;
        font-size: 12px;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #e5e7eb;
    }

    /* ---------- Buttons ---------- */

    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
        min-height: 44px;
        border: none;
    }

    /* ---------- Hide Streamlit branding ---------- */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """
)


# ============================================================
# SESSION STATE
# ============================================================

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "uploaded_name" not in st.session_state:
    st.session_state.uploaded_name = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    html(
        """
        <div class="sidebar-logo">📄 DocuLens</div>
        <div class="sidebar-subtitle">AI-powered document intelligence</div>
        """
    )

    html('<div class="sidebar-section">Workspace</div>')

    page = st.radio(
        "Navigation",
        [
            "📊 Document Analyzer",
            "🕘 History",
            "⚙️ Settings",
        ],
        label_visibility="collapsed",
    )

    html('<div class="sidebar-section">Supported files</div>')

    html(
        """
        <div style="font-size:13px;color:#9ca3af;line-height:1.8;">
        📄 PDF documents<br>
        🖼️ PNG images<br>
        🖼️ JPG / JPEG images
        </div>
        """
    )

    html('<div class="sidebar-section">AI capabilities</div>')

    html(
        """
        <div style="font-size:13px;color:#9ca3af;line-height:1.8;">
        ✓ Document understanding<br>
        ✓ OCR & visual analysis<br>
        ✓ Important dates<br>
        ✓ Action extraction<br>
        ✓ Risk & warning detection<br>
        ✓ Plain-language summaries
        </div>
        """
    )


# ============================================================
# SETTINGS PAGE
# ============================================================

if page == "⚙️ Settings":

    html(
        """
        <div class="hero">
            <div class="hero-badge">⚙️ SETTINGS</div>
            <h1 class="hero-title">DocuLens Settings</h1>
            <p class="hero-description">
                Configure your document analysis workspace.
            </p>
        </div>
        """
    )

    st.subheader("AI Configuration")

    st.info("DocuLens currently uses Gemini for document understanding.")

    st.text_input(
        "Model",
        value="gemma-4-26b-a4b-it",
        disabled=True,
    )

    st.checkbox("Use simple language", value=True)
    st.checkbox("Extract important dates", value=True)
    st.checkbox("Detect warnings and restrictions", value=True)

    st.stop()


# ============================================================
# HISTORY PAGE
# ============================================================

if page == "🕘 History":

    html(
        """
        <div class="hero">
            <div class="hero-badge">🕘 HISTORY</div>
            <h1 class="hero-title">Recent Documents</h1>
            <p class="hero-description">
                Your recent document analysis sessions will appear here.
            </p>
        </div>
        """
    )

    if st.session_state.uploaded_name:

        html(
            f"""
            <div class="file-card">
                <div class="file-icon">📄</div>
                <div>
                    <div class="file-name">{escape(st.session_state.uploaded_name)}</div>
                    <div class="file-status">✓ Analyzed in this session</div>
                </div>
            </div>
            """
        )

    else:
        st.info("No analyzed documents yet.")

    st.stop()


# ============================================================
# MAIN HERO
# ============================================================

html(
    """
    <div class="hero">
        <div class="hero-badge">✨ AI DOCUMENT INTELLIGENCE</div>
        <h1 class="hero-title">Understand your documents.<br>In seconds.</h1>
        <p class="hero-description">
            Upload a PDF or image and let DocuLens extract the
            information that actually matters — summaries,
            important dates, actions, and warnings.
        </p>
    </div>
    """
)


# ============================================================
# API CHECK
# ============================================================

if not api_key:

    st.error(
        "⚠️ Gemini API key not found. "
        "Please add GEMINI_API_KEY to your .env file."
    )

    st.code(
        "GEMINI_API_KEY=your_api_key_here",
        language="bash",
    )

    st.stop()


client = genai.Client(api_key=api_key)


# ============================================================
# TOP METRICS
# ============================================================

metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:
    html(
        """
        <div class="metric">
            <div class="metric-number">📄</div>
            <div class="metric-label">Document AI</div>
        </div>
        """
    )

with metric2:
    html(
        """
        <div class="metric">
            <div class="metric-number">OCR</div>
            <div class="metric-label">Text extraction</div>
        </div>
        """
    )

with metric3:
    html(
        """
        <div class="metric">
            <div class="metric-number">⚡</div>
            <div class="metric-label">Fast analysis</div>
        </div>
        """
    )

with metric4:
    html(
        """
        <div class="metric">
            <div class="metric-number">🔒</div>
            <div class="metric-label">Private session</div>
        </div>
        """
    )


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# UPLOAD AREA
# ============================================================

html(
    """
    <div class="upload-container">
        <div class="upload-icon">☁️</div>
        <div class="upload-title">Drop your document here</div>
        <div class="upload-text">
            PDF, PNG, JPG or JPEG · Upload a document to begin
        </div>
    </div>
    """
)


uploaded_file = st.file_uploader(
    "Choose a document",
    type=["pdf", "png", "jpg", "jpeg"],
    label_visibility="collapsed",
)


# ============================================================
# DOCUMENT PREVIEW
# ============================================================

if uploaded_file:

    st.session_state.uploaded_name = uploaded_file.name

    file_size_mb = uploaded_file.size / (1024 * 1024)

    left, right = st.columns([2.5, 1])

    with left:

        html(
            f"""
            <div class="file-card">
                <div class="file-icon">📄</div>
                <div>
                    <div class="file-name">{escape(uploaded_file.name)}</div>
                    <div class="file-status">✓ Ready for analysis</div>
                </div>
            </div>
            """
        )

    with right:

        st.caption(f"{uploaded_file.type} · {file_size_mb:.2f} MB")

    # Preview images
    if uploaded_file.type.startswith("image"):

        st.image(
            uploaded_file,
            caption="Document preview",
            width="stretch",
        )

    elif uploaded_file.type == "application/pdf":

        st.info(
            "📑 PDF uploaded successfully. "
            "DocuLens will analyze the document directly."
        )

    # ========================================================
    # ANALYZE BUTTON
    # ========================================================

    analyze = st.button(
        "🔍 Analyze Document",
        type="primary",
        width="stretch",
    )

    if analyze:

        with st.status(
            "🤖 DocuLens is analyzing your document...",
            expanded=True,
        ) as status:

            temp_file = None

            try:

                st.write("📤 Uploading document to Gemini...")

                suffix = os.path.splitext(uploaded_file.name)[1]

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix,
                ) as tmp:

                    tmp.write(uploaded_file.getbuffer())
                    temp_file = tmp.name

                gemini_file = client.files.upload(file=temp_file)

                st.write("🧠 Understanding document content...")

                prompt = """
You are DocuLens, an intelligent document understanding assistant.

Analyze the uploaded document carefully.

Use ONLY information that is actually present in the document.
Never invent or assume information.

Return your answer using EXACTLY these sections:

## 📖 Simple Summary

Explain what this document is about in simple language.
Keep it concise but useful.

## ⭐ Important Points

List the most important facts, requirements,
conditions, amounts, or information.

## 📅 Important Dates

Identify all important dates, deadlines,
renewal dates, expiration dates, or time limits.

If there are none, write:
"No important dates found."

## ✅ What You Need To Do

Give the reader a practical step-by-step action list.

Only include actions supported by the document.

## ⚠️ Important Warnings

Mention important conditions, restrictions,
fees, penalties, risks, limitations,
or things the reader should be careful about.

If none are present, write:
"No major warnings found."

Keep the language simple and easy to understand.
"""

                response = client.models.generate_content(
                    model="gemma-4-26b-a4b-it",
                    contents=[
                        gemini_file,
                        prompt,
                    ],
                )

                st.write("✨ Preparing your results...")

                status.update(
                    label="✅ Analysis complete",
                    state="complete",
                    expanded=False,
                )

                st.session_state.analysis = response.text

            except Exception as e:

                status.update(
                    label="❌ Analysis failed",
                    state="error",
                )

                st.error(
                    "Something went wrong while analyzing the document."
                )

                st.exception(e)

            finally:

                if temp_file:
                    try:
                        os.remove(temp_file)
                    except OSError:
                        pass


# ============================================================
# ANALYSIS RESULTS
# ============================================================

if st.session_state.analysis:

    html(
        """
        <div class="analysis-header">
            <div>
                <div class="analysis-title">🧠 DocuLens Analysis</div>
                <div class="analysis-subtitle">
                    AI-generated insights from your document
                </div>
            </div>
            <div>✨ AI</div>
        </div>
        """
    )

    # --------------------------------------------------------
    # Parse sections
    # --------------------------------------------------------

    analysis = st.session_state.analysis

    sections = {
        "📖 Simple Summary": "",
        "⭐ Important Points": "",
        "📅 Important Dates": "",
        "✅ What You Need To Do": "",
        "⚠️ Important Warnings": "",
    }

    current_section = None

    for line in analysis.splitlines():

        clean_line = line.strip()

        matched_section = None

        for section in sections:

            if (
                clean_line.lower()
                .replace("#", "")
                .strip()
                .startswith(section.lower())
            ):
                matched_section = section
                break

        if matched_section:
            current_section = matched_section

        elif current_section:
            sections[current_section] += line + "\n"

    # --------------------------------------------------------
    # Render result cards
    # --------------------------------------------------------

    section_card("📖 Simple Summary", sections["📖 Simple Summary"])
    section_card("⭐ Important Points", sections["⭐ Important Points"])

    col1, col2 = st.columns(2)

    with col1:
        section_card("📅 Important Dates", sections["📅 Important Dates"])

    with col2:
        section_card("✅ What You Need To Do", sections["✅ What You Need To Do"])

    section_card("⚠️ Important Warnings", sections["⚠️ Important Warnings"])

    # --------------------------------------------------------
    # Raw response
    # --------------------------------------------------------

    with st.expander("🔎 View complete AI response"):
        st.markdown(analysis)


# ============================================================
# EMPTY STATE
# ============================================================

if not uploaded_file and not st.session_state.analysis:

    html(
        """
        <div style="text-align:center;padding:55px 20px;color:#9ca3af;">
            <div style="font-size:52px;">📄</div>
            <div style="font-size:20px;font-weight:700;color:#374151;margin-top:12px;">
                Your document workspace is ready
            </div>
            <div style="font-size:14px;margin-top:8px;">
                Upload a document above to extract meaningful insights with AI.
            </div>
        </div>
        """
    )


# ============================================================
# FOOTER
# ============================================================

html(
    """
    <div class="footer">
        DocuLens · AI-powered document intelligence
        <br>
        Built with Streamlit + Gemini
    </div>
    """
)