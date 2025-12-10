# Project Structure

## Directory Structure

```
IstanbulUlasimProjesi/
├── src/                          # Source code (renamed from 'kod')
│   ├── environment_analysis_engine.py
│   ├── ai_environment_recommendations.py
│   ├── health_analysis_engine.py
│   ├── transportation_analysis_engine.py
│   ├── web_server.py
│   └── ...
├── data/                         # Data files (renamed from 'veriler')
│   └── ham_veri/                 # Raw data
│       ├── _yesil_alanlar_verileri.xlsx
│       ├── yaysis_mahal_geo_data.geojson
│       └── saglik/               # Health data subdirectory
├── outputs/                      # Output files (renamed from 'ciktilar')
│   ├── ai_analiz_cevre_39ilce.json
│   ├── ai_cevre_onerileri_39ilce.json
│   └── ...
└── web/                          # Web interface files
    ├── index.html
    ├── cevre_html.html
    └── ...
```

## File Naming Convention

### Python Files (English)
- `environment_analysis_engine.py` - Environmental data analysis
- `ai_environment_recommendations.py` - AI recommendations for environment
- `health_analysis_engine.py` - Health data analysis
- `transportation_analysis_engine.py` - Transportation data analysis
- `web_server.py` - Flask web server

### Data Files (Turkish names kept for compatibility)
- Data files keep Turkish names as they contain Turkish data
- Output files keep Turkish names for backward compatibility

## Excel File Sheets

The `_yesil_alanlar_verileri.xlsx` file contains 6 sheets:
1. **Park Bahçe ve Yeşil Alanlar D.** - Main summary data
2. **Yeşil Alanlar Sayısı** - Green space counts by type
3. **2022 Bakımı Yapılan Ağaç Sayısı** - Trees maintained in 2022
4. **2022 Yılı Dikilen Ağaç Sayısı** - Trees planted in 2022
5. **Spor Alanları Sayıları** - Sports facilities counts
6. **Çocuk Oyun Grubu Sayısı** - Children's playground counts

All sheets are now processed by `environment_analysis_engine.py`.


