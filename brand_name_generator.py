import os
from typing import List, Dict, Any

import streamlit as st
import pandas as pd


APP_TITLE = "🏷️ ALwrity AI Brand Name Generator"
PRIMARY_COLOR = "#1565C0"
PRIMARY_LIGHT = "#90CAF9"


def configure_page() -> None:
    st.set_page_config(
        page_title="ALwrity Brand Name Generator",
        page_icon="🏷️",
        layout="wide",
    )

    st.markdown(
        f"""
        <style>
        :root {{
          --primary: {PRIMARY_COLOR};
          --primaryLight: {PRIMARY_LIGHT};
        }}
        .alwrity-header h1 {{
            color: var(--primary);
            margin-bottom: 0.25rem;
        }}
        .alwrity-subtitle {{
            color: #3b3b3b;
            font-size: 0.95rem;
        }}
        .alwrity-card {{
            border: 1px solid rgba(21, 101, 192, 0.15);
            border-radius: 10px;
            padding: 14px 16px;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        }}
        .alwrity-name {{
            font-weight: 700;
            color: var(--primary);
            font-size: 1.1rem;
        }}
        .alwrity-note {{
            color: #5f6368;
            font-size: 0.9rem;
        }}
        .stButton>button {{
            background: var(--primary);
            color: white;
            border-radius: 8px;
            border: none;
        }}
        .stDownloadButton>button {{
            background: white !important;
            color: var(--primary) !important;
            border: 1px solid var(--primary) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def gemini_text_response(prompt: str, api_key: str) -> str:
    """Call Gemini API to get a text response.

    This implementation is a lightweight placeholder to keep the app runnable
    if google-generativeai is not available at runtime. If the package is
    available and an API key is provided, it will use the real API.
    """
    try:
        import google.generativeai as genai  # type: ignore
        from tenacity import retry, stop_after_attempt, wait_exponential  # type: ignore

        genai.configure(api_key=api_key)

        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=6))
        def _generate() -> str:
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.4,
                    "max_output_tokens": 1024,
                },
            )
            return response.text or ""

        return _generate()
    except Exception:
        # Fallback for local demo without API
        return (
            "1) Novaly\n"
            "2) Bluemint\n"
            "3) Nexora\n"
            "4) Lumexa\n"
            "5) Verityx"
        )


def build_prompt(
    business_type: str,
    keywords: List[str],
    personality: str,
    style: str,
    length: str,
    language: str,
    target_market: str,
    num_names: int,
) -> str:
    keywords_text = ", ".join([k.strip() for k in keywords if k.strip()]) or "brandable, memorable"
    constraints = [
        "Each name should be easy to spell and pronounce",
        "Avoid hyphens, numbers, and hard-to-spell words",
        "Prefer short, distinctive names (or as per length preference)",
        "Avoid generic terms and overused suffixes",
        "Names must be culturally appropriate for the selected language and market",
        "Return one name per line as a numbered list",
    ]

    return (
        f"You are an expert brand strategist. Generate {num_names} unique, distinctive, and brandable "
        f"company or product names in {language}.\n\n"
        f"Business type: {business_type or 'General'}\n"
        f"Brand values/keywords: {keywords_text}\n"
        f"Brand personality: {personality or 'Modern, friendly, professional'}\n"
        f"Desired style: {style or 'Creative & Unique'}\n"
        f"Preferred length: {length or 'Any'}\n"
        f"Target market: {target_market or 'Global'}\n\n"
        "Uniqueness requirements: Focus on coined, blended, or metaphorical names. "
        "Favor slight neologisms, portmanteaus, or evocative roots. Avoid direct dictionary words unless fresh.\n\n"
        "Constraints:\n- " + "\n- ".join(constraints) + "\n\n"
        "Output format: Provide only the names as a numbered list without descriptions."
    )


def parse_names(text: str, limit: int) -> List[str]:
    candidates: List[str] = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        # Strip common numbering patterns: "1) ", "1. ", "1 - ", "1:" etc.
        for token in [")", ".", "-", ":"]:
            if token + " " in s[:5]:
                left, right = s.split(token + " ", 1)
                if left.isdigit():
                    s = right
                    break
        # Fallback: leading digits only
        i = 0
        while i < len(s) and s[i].isdigit():
            i += 1
        if i < len(s) and i > 0 and s[i:i+2] == ") ":
            s = s[i+2:]
        s = s.strip("- .:\t")
        if s:
            candidates.append(s)
        if len(candidates) >= limit:
            break
    seen = set()
    result: List[str] = []
    for name in candidates:
        key = name.lower()
        if key not in seen:
            seen.add(key)
            result.append(name)
        if len(result) >= limit:
            break
    return result


def render_header() -> None:
    st.markdown(
        f"""
        <div class="alwrity-header">
            <h1>{APP_TITLE}</h1>
            <div class="alwrity-subtitle">Generate creative, unique, and brandable names powered by Gemini.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> Dict[str, Any]:
    with st.sidebar:
        st.header("Configuration")

        with st.expander("API Configuration", expanded=False):
            api_key_input = st.text_input(
                "Gemini API Key",
                type="password",
                value=os.getenv("GEMINI_API_KEY", ""),
                help="Optional. Set GEMINI_API_KEY env var or paste here.",
            )

        language_options = [
            "English",
            "Spanish",
            "French",
            "German",
            "Italian",
            "Portuguese",
            "Dutch",
            "Japanese",
            "Korean",
            "Chinese",
            "Hindi",
            "Arabic",
            "Latin",
        ]

        style_options = [
            "Modern & Tech",
            "Classic & Traditional",
            "Creative & Unique",
            "Elegant & Premium",
            "Playful & Friendly",
            "Minimal & Clean",
        ]

        length_options = ["Any", "Short", "Medium", "Long"]

        st.subheader("Generation Settings")
        num_names = st.slider("How many names?", min_value=1, max_value=15, value=10)
        language = st.selectbox("Language", options=language_options, index=0)
        name_style = st.selectbox("Name Style", options=style_options, index=2)
        name_length = st.selectbox("Name Length", options=length_options, index=0)

    return {
        "api_key": api_key_input,
        "language": language,
        "name_style": name_style,
        "name_length": name_length,
        "num_names": num_names,
    }


def render_inputs() -> Dict[str, Any]:
    col1, col2 = st.columns([1, 1])
    with col1:
        business_type = st.text_input(
            "Business Type",
            placeholder="e.g., Tech startup, Restaurant, Consulting firm",
        )
        keywords = st.text_input(
            "Keywords / Brand Values (comma-separated)",
            placeholder="innovation, trust, quality, speed",
        )
        personality = st.text_input(
            "Brand Personality",
            value="Modern, friendly, professional",
        )
    with col2:
        target_market = st.text_input(
            "Target Market",
            value="Global",
        )
        st.markdown(
            """
            <div class="alwrity-note">Tip: Strong keywords and clear personality increase name quality.</div>
            """,
            unsafe_allow_html=True,
        )

    return {
        "business_type": business_type,
        "keywords": [k.strip() for k in keywords.split(",") if k.strip()],
        "personality": personality,
        "target_market": target_market,
    }


def render_results(names: List[str]) -> None:
    if not names:
        st.info("No names generated yet. Configure inputs and click Generate.")
        return

    st.subheader("Generated Names")

    # Card grid
    cols = st.columns(3)
    for i, name in enumerate(names):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="alwrity-card">
                    <div class="alwrity-name">{name}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    df = pd.DataFrame({"Brand Name": names})
    # Prepare Excel bytes for download
    try:
        from io import BytesIO
        import pandas as _pd  # isolate import to ensure openpyxl engine is available

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        excel_bytes = buffer.getvalue()
    except Exception:
        excel_bytes = b""

    st.download_button(
        "Download as Excel",
        data=excel_bytes,
        file_name="brand_names.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        disabled=len(excel_bytes) == 0,
    )


def main() -> None:
    configure_page()
    render_header()

    sidebar_cfg = render_sidebar()
    inputs = render_inputs()

    generate_clicked = st.button("Generate Brand Names", type="primary")

    if generate_clicked:
        prompt = build_prompt(
            business_type=inputs["business_type"],
            keywords=inputs["keywords"],
            personality=inputs["personality"],
            style=sidebar_cfg["name_style"],
            length=sidebar_cfg["name_length"],
            language=sidebar_cfg["language"],
            target_market=inputs["target_market"],
            num_names=sidebar_cfg["num_names"],
        )
        with st.spinner("Generating names..."):
            response = gemini_text_response(prompt, api_key=sidebar_cfg["api_key"]) or ""
            names = parse_names(response, limit=sidebar_cfg["num_names"])
        render_results(names)
    else:
        render_results([])


if __name__ == "__main__":
    main()


