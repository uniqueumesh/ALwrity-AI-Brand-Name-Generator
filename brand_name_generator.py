import time
import os
import json
import streamlit as st
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
import pandas as pd
import io


def main():
    # Set page configuration
    st.set_page_config(
        page_title="Alwrity - Brand Name Generator",
        layout="wide",
    )
    
    # Remove the extra spaces from margin top.
    st.markdown("""
        <style>
        ::-webkit-scrollbar-track {
        background: #e1ebf9;
        }

        ::-webkit-scrollbar-thumb {
            background-color: #90CAF9;
            border-radius: 10px;
            border: 3px solid #e1ebf9;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #64B5F6;
        }

        ::-webkit-scrollbar {
            width: 16px;
        }
        div.stButton > button:first-child {
            background: #1565C0;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 10px 2px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
            font-weight: bold;
        }
        </style>
    """
    , unsafe_allow_html=True)

    # Hide top header line
    hide_decoration_bar_style = '<style>header {visibility: hidden;}</style>'
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

    # Hide footer
    hide_streamlit_footer = '<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>'
    st.markdown(hide_streamlit_footer, unsafe_allow_html=True)

    st.title("🏷️ Alwrity - AI Brand Name Generator")

    # --- API Key Input Section (moved below title) ---
    with st.expander("API Configuration 🔑", expanded=False):
        st.markdown('''If the default Gemini API key is unavailable or exceeds its limits, you can provide your own API key below.<br>
        <a href="https://aistudio.google.com/app/apikey" target="_blank">Get Gemini API Key</a>
        ''', unsafe_allow_html=True)
        user_gemini_api_key = st.text_input("Gemini API Key", type="password", help="Paste your Gemini API Key here if you have one. Otherwise, the tool will use the default key if available.")

    # Input section
    with st.expander("**PRO-TIP** - Follow the steps below for best results.", expanded=True):
        col1, col2 = st.columns([5, 5])

        with col1:
            input_business_type = st.text_input(
                '**🏢 What type of business are you starting?**',
                placeholder="e.g., Tech startup, Restaurant, Consulting firm",
                help="Describe your business type or industry."
            )
            input_keywords = st.text_input(
                '**🔑 Enter keywords related to your brand**',
                placeholder="e.g., innovation, quality, speed, trust",
                help="Use 2-4 words that represent your brand values or key concepts."
            )
            input_brand_personality = st.text_area(
                '**💭 Describe your brand personality** (Optional)',
                placeholder="e.g., Modern, friendly, professional, innovative, eco-friendly...",
                help="Describe how you want your brand to be perceived by customers."
            )

        with col2:
            input_name_style = st.selectbox(
                '🎨 Name Style Preference', 
                ('Modern & Tech', 'Classic & Traditional', 'Creative & Unique', 'Professional & Corporate', 'Playful & Fun', 'Luxury & Premium'),
                index=0
            )
            input_name_length = st.selectbox(
                '📏 Preferred Name Length', 
                ('Short (1-2 words)', 'Medium (2-3 words)', 'Long (3+ words)', 'Any Length'), 
                index=1
            )
            language_options = ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Latin", "Other"]
            input_language = st.selectbox(
                '🌐 Select Language', 
                options=language_options,
                index=0,
                help="Choose the language for your brand name."
            )
            if input_language == "Other":
                input_language = st.text_input(
                    'Specify Language', 
                    placeholder="e.g., Italian, Dutch",
                    help="Specify your preferred language."
                )
            # Add Target Market input
            input_target_market = st.text_input(
                '🎯 Target Market (Optional)',
                placeholder="e.g., B2B, Consumers, Millennials, Global",
                help="Specify your target market for more tailored names."
            )

    # Add option for number of names
    st.markdown('<h3 style="margin-top:2rem;">How many brand names do you want to generate?</h3>', unsafe_allow_html=True)
    num_names = st.slider('Number of brand name suggestions', min_value=1, max_value=15, value=8, help="Choose how many brand names to generate (1-15).")

    # Generate Brand Names button
    if st.button('**Generate Brand Names**'):
        with st.spinner("Generating brand names..."):
            if not input_business_type and not input_keywords:
                st.error('**🫣 Provide Inputs to generate Brand Names. Business type OR keywords are required!**')
            else:
                brand_names = generate_brand_names(
                    input_business_type, input_keywords, input_brand_personality, 
                    input_name_style, input_name_length, input_language, 
                    user_gemini_api_key, num_names, input_target_market
                )
                if brand_names:
                    st.session_state['brand_names'] = brand_names
                else:
                    st.error("💥 **Failed to generate brand names. Please try again!**")
            st.markdown(st.session_state['brand_names'])
            
            # Excel export for evaluation
            names_list = [name.strip().lstrip('0123456789. ') for name in st.session_state['brand_names'].split('\n') if name.strip()]
            df = pd.DataFrame({'Brand Name': names_list})
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer.seek(0)
            st.download_button(
                label="Download Brand Names as Excel for Evaluation",
                data=excel_buffer,
                file_name="brand_names.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


# Function to generate brand names
def generate_brand_names(input_business_type, input_keywords, input_brand_personality, input_name_style, input_name_length, input_language, user_gemini_api_key=None, num_names=8, input_target_market=None):
    """ Function to call upon LLM to get the work done. """
    
    # Refined prompt for brand name generation
    brand_guidelines = f"""
Generate {num_names} unique and creative brand names for the following business.

Business Requirements:
- Business Type: {input_business_type}
- Keywords/Values: {input_keywords}
- Brand Personality: {input_brand_personality}
- Name Style: {input_name_style}
- Name Length: {input_name_length}
- Language: {input_language}
- Target Market: {input_target_market}

Rules for Brand Name Generation:
- Each name must be unique and memorable
- Names should be easy to pronounce and spell
- Avoid generic or overused terms
- Consider trademark availability (avoid obvious conflicts)
- Make names brandable and distinctive
- If target market is specified, tailor names accordingly
- Match the requested name style and length preferences
- Write in this language: {input_language}
- Ensure names are culturally appropriate
- Make names sound professional and trustworthy
- Consider domain name availability potential
- Avoid names that are too similar to existing major brands

Generate {num_names} different brand name options. List only the names, one per line, without numbers or explanations.
"""

    brand_names = gemini_text_response(brand_guidelines, user_gemini_api_key)
    if brand_names == 'RATE_LIMIT':
        st.warning('⚠️ Gemini API rate limit or quota exceeded. Please try again later or use a different API key.')
        return None
    return brand_names


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def gemini_text_response(prompt, user_gemini_api_key=None):
    import google.generativeai as genai
    import os
    try:
        api_key = user_gemini_api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            st.error("GEMINI_API_KEY is missing. Please provide it in the API Configuration section or set it in the environment.")
            return None
        genai.configure(api_key=api_key)
    except Exception as err:
        st.error(f"Failed to configure Gemini: {err}")
        return None
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.4,
        "top_k": 1,
        "max_output_tokens": 1024
    }
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
    try:
        response = model.generate_content(prompt)
        if hasattr(response, 'code') and response.code == 429:
            return 'RATE_LIMIT'
        if hasattr(response, 'text') and ('rate limit' in response.text.lower() or 'quota' in response.text.lower()):
            return 'RATE_LIMIT'
        return response.text
    except Exception as err:
        if 'quota' in str(err).lower() or 'rate limit' in str(err).lower():
            return 'RATE_LIMIT'
        st.error(f"Failed to get response from Gemini: {err}. Retrying.")
        return None


if __name__ == "__main__":
    main()
