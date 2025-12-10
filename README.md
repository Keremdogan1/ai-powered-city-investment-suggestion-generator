# AI-Powered City Investment Suggestion Generator

An AI-driven decision support system providing district-level investment recommendations for Istanbul. With sufficient databases, this system can be applied to other cities as well.

## 🏗️ Project Structure

```
IstanbulUlasimProjesi/
├── src/                          # Source code
│   ├── environment_analysis_engine.py
│   ├── ai_environment_recommendations.py
│   ├── health_analysis_engine.py
│   ├── transportation_analysis_engine.py
│   └── web_server.py
├── data/                         # Data files
│   └── ham_veri/                 # Raw data
├── outputs/                      # Generated outputs
└── web/                          # Web interface
```

## 🚀 Features

- **District-Level Analysis**: Comprehensive analysis for all 39 districts of Istanbul
- **Multi-Category Support**: Transportation, Health, and Environment modules
- **AI-Powered Recommendations**: Claude Sonnet 4.5 integration via OpenRouter
- **Data Integration**: Multiple data sources including Excel, CSV, and GeoJSON
- **Web Interface**: Flask-based web server with interactive dashboards

## 📋 Requirements

See `src/requirements.txt` for Python dependencies.

## 🔐 Environment Variables

Create a `.env` file in the project root:

```
OPENROUTER_API_KEY=your-api-key-here
```

**Note**: `.env` is already in `.gitignore` for security.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r src/requirements.txt
```

### 2. Set Up Environment
```bash
# Create .env file with your API key
echo "OPENROUTER_API_KEY=your-key-here" > .env
```

### 3. Run Analysis Engines

**Environment Analysis:**
```bash
python src/environment_analysis_engine.py
python src/ai_environment_recommendations.py
```

**Health Analysis:**
```bash
python src/health_data_estimation.py
python src/health_analysis_engine.py
python src/ai_health_recommendations.py
```

**Transportation Analysis:**
```bash
python src/transportation_analysis_engine.py
python src/ai_transportation_recommendations.py
```

### 4. Start Web Server
```bash
python src/web_server.py
```

Access the web interface at: `http://localhost:5000`

## 📊 Data Sources

- **Population Data**: District-level population statistics
- **Transportation**: Metro stations, parking facilities, traffic data
- **Health**: Hospital counts, bed capacity, healthcare infrastructure
- **Environment**: Green spaces, parks, GeoJSON spatial data
- **Excel Files**: Multi-sheet Excel files with comprehensive statistics

## 🔄 Recent Updates

- ✅ Renamed all directories and files to English
- ✅ Integrated all 6 Excel sheets in environment analysis
- ✅ GeoJSON data processing for district-level analysis
- ✅ Updated project structure for better organization
- ✅ Comprehensive `.gitignore` including `.env` protection

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

Kerem Doğan

## 🔗 Repository

[GitHub Repository](https://github.com/Keremdogan1/ai-powered-city-investment-suggestion-generator)
