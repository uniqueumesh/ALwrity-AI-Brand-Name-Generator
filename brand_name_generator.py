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
import requests
import socket


def reset_socket_timeout():
    """Reset socket timeout to default to prevent hanging."""
    try:
        socket.setdefaulttimeout(None)
    except:
        pass


def is_likely_taken_business_name(name):
    """Enhanced business name pattern detection with conservative approach."""
    if not name or len(name.strip()) < 2:
        return True  # Conservative: reject very short names
    
    name_lower = name.lower().strip()
    
    # Enhanced common business name patterns (expanded list)
    common_patterns = [
        # Generic business words
        'tech', 'digital', 'smart', 'pro', 'max', 'ultra', 'mega', 'super',
        'quick', 'fast', 'easy', 'simple', 'best', 'top', 'prime', 'elite',
        'premium', 'gold', 'silver', 'platinum', 'diamond', 'crystal',
        # Scale indicators
        'global', 'world', 'universe', 'planet', 'space', 'cosmic', 'galaxy',
        'international', 'worldwide', 'universal', 'infinite', 'eternal',
        # Time references
        'future', 'next', 'new', 'modern', 'advanced', 'cutting', 'edge',
        'innovative', 'creative', 'dynamic', 'revolutionary', 'breakthrough',
        # Business types
        'solutions', 'systems', 'services', 'group', 'corp', 'inc', 'llc',
        'labs', 'works', 'studio', 'agency', 'consulting', 'enterprises',
        'ventures', 'holdings', 'industries', 'technologies', 'innovations',
        # Creative terms
        'creative', 'design', 'art', 'craft', 'forge', 'foundry', 'mill',
        'factory', 'workshop', 'atelier', 'boutique', 'gallery', 'studio',
        # Common problematic terms
        'mind', 'write', 'gen', 'smith', 'verb', 'intelli', 'scribble',
        'word', 'text', 'content', 'copy', 'script', 'draft', 'edit',
        'grammar', 'language', 'linguistic', 'vocabulary', 'dictionary'
    ]
    
    # Check for exact matches and partial matches
    for pattern in common_patterns:
        if pattern in name_lower:
            return True
    
    # Enhanced AI/Tech terms detection
    ai_tech_terms = [
        # Core technology terms
        'ai', 'ml', 'data', 'cloud', 'app', 'web', 'mobile', 'software',
        'platform', 'api', 'sdk', 'dev', 'code', 'tech', 'digital',
        # Innovation terms
        'intelli', 'smart', 'auto', 'robo', 'cyber', 'neo', 'quantum',
        'blockchain', 'crypto', 'fintech', 'edtech', 'healthtech',
        # Development terms
        'programming', 'coding', 'development', 'engineering', 'architecture',
        'framework', 'library', 'toolkit', 'suite', 'package', 'module',
        # Modern concepts
        'virtual', 'augmented', 'mixed', 'reality', 'metaverse', 'nft',
        'machine', 'learning', 'deep', 'neural', 'algorithm', 'model'
    ]
    
    for term in ai_tech_terms:
        if term in name_lower:
            return True
    
    # Check for common business name structures
    # Names ending with common business suffixes
    business_suffixes = ['corp', 'inc', 'llc', 'ltd', 'co', 'group', 'systems', 'solutions']
    for suffix in business_suffixes:
        if name_lower.endswith(suffix):
            return True
    
    # Names starting with common business prefixes
    business_prefixes = ['new', 'pro', 'smart', 'digital', 'global', 'world', 'future']
    for prefix in business_prefixes:
        if name_lower.startswith(prefix):
            return True
    
    # Check for overly generic combinations
    generic_combinations = [
        'new tech', 'pro solutions', 'smart systems', 'digital services',
        'global tech', 'world solutions', 'future systems', 'next generation'
    ]
    
    for combo in generic_combinations:
        if combo in name_lower:
            return True
    
    return False


def check_domain_availability(domain_name):
    """Enhanced domain checking with conservative validation and improved error handling."""
    if not domain_name or not domain_name.strip():
        return False  # Conservative: reject empty names
    
    try:
        # Enhanced cleaning of the domain name
        clean_name = domain_name.lower().strip()
        # Remove spaces, special chars, and common separators
        clean_name = clean_name.replace(' ', '').replace('-', '').replace('_', '').replace('.', '')
        # Remove common business suffixes more aggressively
        business_suffixes = ['inc', 'llc', 'corp', 'ltd', 'co', 'group', 'systems', 'solutions', 'tech', 'digital']
        for suffix in business_suffixes:
            if clean_name.endswith(suffix):
                clean_name = clean_name[:-len(suffix)]
        
        # Validate cleaned name
        if len(clean_name) < 2:
            return False  # Conservative: reject very short names
        
        # Check for invalid characters
        if not clean_name.isalnum():
            return False  # Conservative: reject names with special characters
        
        # Step 1: Enhanced domain extension checking with timeout
        extensions = ['.com', '.net', '.org', '.io', '.co', '.biz', '.info']
        domain_taken_count = 0
        
        for ext in extensions:
            try:
                test_domain = clean_name + ext
                # Add timeout to prevent hanging
                socket.setdefaulttimeout(3)  # 3 second timeout
                socket.gethostbyname(test_domain)
                domain_taken_count += 1
                # If any major extension is taken, consider it taken
                if ext in ['.com', '.net', '.org']:
                    return False
            except socket.gaierror:
                continue  # This extension is available
            except socket.timeout:
                # Conservative: if timeout, assume taken
                return False
            except Exception:
                # Conservative: if any error, assume taken
                return False
        
        # Step 2: Enhanced business pattern check
        if is_likely_taken_business_name(clean_name):
            return False
        
        # Step 3: Additional conservative checks
        # Check for common dictionary words that are likely taken
        common_words = [
            'apple', 'google', 'microsoft', 'amazon', 'facebook', 'twitter',
            'linkedin', 'instagram', 'youtube', 'netflix', 'spotify', 'uber',
            'airbnb', 'tesla', 'spacex', 'openai', 'anthropic', 'stripe',
            'paypal', 'square', 'shopify', 'salesforce', 'oracle', 'ibm'
        ]
        
        if clean_name in common_words:
            return False
        
        # Step 4: Check for suspicious patterns
        # Names that are too generic or common
        if len(clean_name) <= 4 and clean_name.isalpha():
            return False  # Conservative: reject very short generic names
        
        # Names with repeated characters (likely taken)
        if len(set(clean_name)) < len(clean_name) * 0.6:
            return False  # Conservative: reject names with too many repeated chars
        
        # Step 5: Final conservative decision
        # If multiple extensions are taken, be more conservative
        if domain_taken_count >= 2:
            return False
        
        # Only return True if we're confident it's available
        reset_socket_timeout()  # Reset timeout
        return True
        
    except Exception as e:
        # Conservative: assume taken if any error occurs
        reset_socket_timeout()  # Reset timeout
        return False


def generate_names_with_domain_validation(input_business_type, input_keywords, input_brand_personality, input_name_style, input_name_length, input_language, user_gemini_api_key=None, num_names=8, input_target_market=None):
    """Generate brand names with enhanced domain validation loop and improved error handling."""
    max_attempts = 3  # Optimized for performance
    target_names = num_names
    unique_names = []
    attempt = 0
    total_checked = 0
    total_rejected = 0
    
    # Enhanced progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    st.info(f"🔍 **Enhanced Validation Mode:** Generating names with conservative domain checking...")
    st.info(f"**Target:** {target_names} unique names | **Max Attempts:** {max_attempts}")
    
    while len(unique_names) < target_names and attempt < max_attempts:
        attempt += 1
        status_text.text(f"🔄 **Attempt {attempt}/{max_attempts}:** Generating and validating names...")
        
        try:
            # Generate names using AI with error handling
            brand_names = generate_brand_names(
                input_business_type, input_keywords, input_brand_personality, 
                input_name_style, input_name_length, input_language, 
                user_gemini_api_key, num_names, input_target_market
            )
            
            if not brand_names:
                st.error("❌ **AI Generation Failed:** Please check your API key and try again.")
                return None
            
            # Parse generated names with enhanced cleaning
            names_list = []
            for name in brand_names.split('\n'):
                cleaned_name = name.strip().lstrip('0123456789. -•*')
                if cleaned_name and len(cleaned_name) > 1:
                    names_list.append(cleaned_name)
            
            if not names_list:
                st.warning("⚠️ **No Valid Names Generated:** Try different inputs.")
                continue
            
            # Enhanced validation loop with detailed feedback
            for name in names_list:
                if name and name not in unique_names:  # Avoid duplicates
                    total_checked += 1
                    
                    # Enhanced domain availability check
                    try:
                        domain_available = check_domain_availability(name)
                        
                        if domain_available:
                            unique_names.append(name)
                            st.success(f"✅ **Unique Found:** {name}")
                            if len(unique_names) >= target_names:
                                break
                        else:
                            total_rejected += 1
                            st.warning(f"⚠️ **Rejected:** {name} (likely taken)")
                            
                    except Exception as e:
                        total_rejected += 1
                        st.warning(f"⚠️ **Validation Error:** {name} (assumed taken)")
            
            # Update progress
            progress = min(len(unique_names) / target_names, 1.0)
            progress_bar.progress(progress)
            
            # Show detailed progress
            status_text.text(f"📊 **Progress:** {len(unique_names)}/{target_names} unique names found | {total_checked} checked | {total_rejected} rejected")
            
            # If we have enough names, break
            if len(unique_names) >= target_names:
                break
                
            # If we need more names and have attempts left
            if len(unique_names) < target_names and attempt < max_attempts:
                st.write("🔄 **Generating more names...**")
                
        except Exception as e:
            st.error(f"❌ **Attempt {attempt} Failed:** {str(e)}")
            continue
    
    # Final results with enhanced feedback
    progress_bar.progress(1.0)
    
    if len(unique_names) == 0:
        st.error("❌ **No Unique Names Found**")
        st.warning("💡 **Suggestions:**")
        st.write("- Try more specific or creative keywords")
        st.write("- Use different business type descriptions")
        st.write("- Consider different name styles or languages")
        st.write("- The validation is now very conservative to ensure quality")
        return None
        
    elif len(unique_names) < target_names:
        st.warning(f"⚠️ **Partial Success:** Found {len(unique_names)} unique names (target was {target_names})")
        st.info("💡 **Note:** Enhanced validation is very conservative to ensure quality. Fewer but better names!")
        
    else:
        st.success(f"🎉 **Success:** Found {len(unique_names)} unique names!")
    
    # Final statistics
    st.info(f"📈 **Validation Stats:** {total_checked} names checked | {total_rejected} rejected | {len(unique_names)} approved")
    
    return unique_names


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
                placeholder="e.g., AI-powered fitness app for seniors, Artisanal coffee roastery, Sustainable fashion brand",
                help="Be specific! Instead of 'restaurant', try 'farm-to-table vegan restaurant' or 'AI-powered fitness app for seniors'"
            )
            input_keywords = st.text_input(
                '**🔑 Enter keywords related to your brand**',
                placeholder="e.g., zen-like, minimalist, artisanal, eco-conscious, futuristic",
                help="Use unique, specific words! Instead of 'innovation, quality', try 'zen-like, minimalist, artisanal' or 'eco-conscious, futuristic, sustainable'"
            )
            input_brand_personality = st.text_area(
                '**💭 Describe your brand personality** (Optional)',
                placeholder="e.g., Scandinavian-inspired, community-focused, artisanal, zen-like, futuristic, bohemian",
                help="Be creative! Instead of 'modern, friendly', try 'Scandinavian-inspired, community-focused' or 'zen-like, minimalist, artisanal'"
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
                placeholder="e.g., eco-conscious millennials in urban areas, health-conscious professionals, creative entrepreneurs",
                help="Be specific! Instead of 'consumers', try 'eco-conscious millennials in urban areas' or 'health-conscious professionals aged 25-40'"
            )

    # Add option for number of names
    st.markdown('<h3 style="margin-top:2rem;">How many brand names do you want to generate?</h3>', unsafe_allow_html=True)
    num_names = st.slider('Number of brand name suggestions', min_value=1, max_value=10, value=5, help="Choose how many brand names to generate (1-10).")

    # Generate Brand Names button
    if st.button('**Generate Brand Names**'):
        if not input_business_type and not input_keywords:
            st.error('**🫣 Provide Inputs to generate Brand Names. Business type OR keywords are required!**')
        else:
            # Use enhanced domain validation loop
            unique_names = generate_names_with_domain_validation(
                input_business_type, input_keywords, input_brand_personality, 
                input_name_style, input_name_length, input_language, 
                user_gemini_api_key, num_names, input_target_market
            )
            
            if unique_names:
                # Store unique names in session state
                st.session_state['unique_names'] = unique_names
                
                # Display unique names
                st.markdown('<h3 style="margin-top:2rem; color:#1976D2;">🎯 Unique Brand Names (Domain Available)</h3>', unsafe_allow_html=True)
                
                for i, name in enumerate(unique_names, 1):
                    st.markdown(f"""
                    <div style="
                        background-color: #f8f9fa;
                        border-left: 4px solid #4caf50;
                        padding: 15px;
                        margin: 10px 0;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    ">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div>
                                <span style="
                                    background-color: #4caf50;
                                    color: white;
                                    padding: 5px 10px;
                                    border-radius: 15px;
                                    font-size: 14px;
                                    font-weight: bold;
                                    margin-right: 15px;
                                ">{i}</span>
                                <span style="
                                    font-size: 18px;
                                    font-weight: 600;
                                    color: #333;
                                ">{name}</span>
                            </div>
                            <div style="
                                font-size: 14px;
                                font-weight: 500;
                                padding: 5px 10px;
                                border-radius: 15px;
                                background-color: #e8f5e8;
                                color: #2e7d32;
                            ">
                                ✅ Domain Available
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Excel export for evaluation
                df = pd.DataFrame({'Brand Name': unique_names})
                excel_buffer = io.BytesIO()
                df.to_excel(excel_buffer, index=False, engine='openpyxl')
                excel_buffer.seek(0)
                st.download_button(
                    label="Download Unique Brand Names as Excel",
                    data=excel_buffer,
                    file_name="unique_brand_names.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("💥 **Failed to generate unique brand names. Please try again!**")


# Function to generate brand names
def generate_brand_names(input_business_type, input_keywords, input_brand_personality, input_name_style, input_name_length, input_language, user_gemini_api_key=None, num_names=8, input_target_market=None):
    """ Function to call upon LLM to get the work done. """
    
    # Enhanced prompt for unique brand name generation
    brand_guidelines = f"""
Generate {num_names} COMPLETELY UNIQUE and never-before-seen brand names for the following business.

Business Requirements:
- Business Type: {input_business_type}
- Keywords/Values: {input_keywords}
- Brand Personality: {input_brand_personality}
- Name Style: {input_name_style}
- Name Length: {input_name_length}
- Language: {input_language}
- Target Market: {input_target_market}

CRITICAL UNIQUENESS REQUIREMENTS:
- Create names that have NEVER been used by any existing brand
- Avoid ALL common industry terms, generic words, and overused patterns
- Do NOT use names that sound similar to existing major brands
- Generate truly original combinations that don't exist anywhere
- Create innovative word combinations and creative twists
- Use abstract concepts, made-up words, and unique linguistic combinations

CREATIVITY AND INNOVATION RULES:
- Use portmanteau techniques (combining words creatively)
- Incorporate abstract concepts and emotional elements
- Create made-up words that sound natural and brandable
- Use less common languages, roots, and linguistic elements
- Apply creative spelling variations and unique pronunciations
- Combine unexpected word pairs for memorable results

INDUSTRY-SPECIFIC UNIQUENESS RULES:
- AVOID common suffixes: -ly, -ify, -tech, -hub, -lab, -works, -solutions
- AVOID generic prefixes: new-, pro-, smart-, digital-, eco-
- AVOID overused industry terms and clichéd combinations
- Create industry-specific creative alternatives
- Use unconventional approaches for the business type

QUALITY AND BRANDABILITY REQUIREMENTS:
- Names must be easy to pronounce and spell
- Ensure cultural appropriateness for {input_language}
- Make names sound professional and trustworthy
- Consider domain name availability potential
- Match the requested name style: {input_name_style}
- Match the requested name length: {input_name_length}
- Tailor to target market: {input_target_market}

GENERATION INSTRUCTIONS:
- Think creatively and outside conventional naming patterns
- Use divergent thinking to create unexpected combinations
- Focus on memorability and distinctiveness
- Ensure each name is completely different from the others
- Create names that stand out in the marketplace

Generate {num_names} completely unique, innovative brand name options. List only the names, one per line, without numbers or explanations.
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
        "temperature": 0.9,
        "top_p": 0.6,
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
