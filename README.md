# 🏷️ ALwrity AI Brand Name Generator

Generate creative, unique, and brandable names for your business using the power of AI. This tool helps entrepreneurs, startups, and businesses find the perfect brand name that resonates with their target audience.

## ✨ Features

- **AI-Powered Generation**: Uses Google's Gemini 2.5 Flash model for intelligent brand name creation
- **Customizable Inputs**: Specify business type, keywords, brand personality, and target market
- **Style Preferences**: Choose from Modern & Tech, Classic & Traditional, Creative & Unique, and more
- **Multi-Language Support**: Generate names in English, Spanish, French, German, Chinese, Japanese, Latin, and more
- **Length Control**: Specify preferred name length (Short, Medium, Long, or Any)
- **Export Functionality**: Download generated names as Excel files for evaluation
- **Professional UI**: Clean, modern interface matching the Alwrity design system
- **API Integration**: Support for custom Gemini API keys with fallback to default

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/uniqueumesh/ALwrity-AI-Brand-Name-Generator.git
   cd ALwrity-AI-Brand-Name-Generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key** (Optional)
   ```bash
   # Windows
   set GEMINI_API_KEY=your_api_key_here
   
   # macOS/Linux
   export GEMINI_API_KEY=your_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run brand_name_generator.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

## 🎯 How to Use

### Step 1: Configure API (Optional)
- Expand the "API Configuration" section
- Enter your Gemini API key if you have one
- The tool will use the default key if none is provided

### Step 2: Input Your Requirements
- **Business Type**: Describe your business (e.g., "Tech startup", "Restaurant", "Consulting firm")
- **Keywords**: Enter brand values (e.g., "innovation", "quality", "trust", "speed")
- **Brand Personality**: Describe how you want to be perceived (e.g., "Modern, friendly, professional")
- **Name Style**: Choose from predefined styles
- **Name Length**: Select preferred length
- **Language**: Choose your target language
- **Target Market**: Specify your audience (e.g., "B2B", "Millennials", "Global")

### Step 3: Generate Names
- Choose how many names to generate (1-15)
- Click "Generate Brand Names"
- Review the AI-generated suggestions

### Step 4: Export Results
- Download the generated names as an Excel file
- Use the file for team evaluation and A/B testing

## 🛠️ Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and Excel export
- **OpenPyXL**: Excel file handling
- **Google Generative AI**: Gemini API integration
- **Tenacity**: Robust retry mechanism for API calls

### API Configuration
The tool uses Google's Gemini 2.5 Flash model with the following settings:
- Temperature: 0.7 (balanced creativity)
- Top-p: 0.4 (focused generation)
- Max tokens: 1024 (sufficient for multiple names)

## 🎨 Design Philosophy

This tool follows the Alwrity design system with:
- **Consistent Color Scheme**: Blue theme (#1565C0, #90CAF9)
- **Professional Layout**: Wide layout with expandable sections
- **User-Friendly Interface**: Clear instructions and helpful tooltips
- **Responsive Design**: Works on desktop and mobile devices

## 📊 Use Cases

- **Startups**: Find memorable names for new ventures
- **Product Launches**: Generate names for new products or services
- **Rebranding**: Discover fresh names for existing businesses
- **Side Projects**: Quick name generation for personal projects
- **Agencies**: Help clients find the perfect brand names

## 🔧 Customization

### Adding New Languages
Edit the `language_options` list in the code to add support for additional languages.

### Modifying Name Styles
Update the `input_name_style` selectbox options to include custom style preferences.

### Adjusting AI Parameters
Modify the `generation_config` in the `gemini_text_response` function to change AI behavior.

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure your Gemini API key is valid
   - Check if you've exceeded API quotas
   - Try using the default key if available

2. **No Names Generated**
   - Verify you've provided business type or keywords
   - Check your internet connection
   - Try reducing the number of names requested

3. **Export Issues**
   - Ensure you have write permissions in the download directory
   - Check if Excel is properly installed

## 🤝 Contributing

We welcome contributions! Please feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Gemini AI](https://ai.google.dev/)
- Part of the [Alwrity](https://alwrity.com) AI tool suite

## 📞 Support

For support, feature requests, or questions:
- Create an issue on GitHub
- Contact us through the Alwrity platform

---

**Made with ❤️ by the Alwrity team**
