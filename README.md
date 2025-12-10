# AI-Powered Urban Investment Recommendation Platform

This repository contains an AI-driven decision support system designed to analyze city-level needs (transportation, environment, health, infrastructure, social services) and generate data-informed investment recommendations for municipalities, institutions, and planners.

The system currently provides district-level transportation suggestions for Istanbul through a simple web interface. It integrates open data sources, APIs, scraping modules, and LLM-based reasoning (via OpenRouter + Sonnet Claude 4.5) to produce explainable, multi-criteria recommendations.

---

## 🇹🇷 Türkçe Açıklama

### 🏙️ Şehir Bazlı Yapay Zekâ Destekli Yatırım Öneri Sistemi

Bu proje, şehirlerin kritik ihtiyaçlarını analiz ederek kurumlara veri odaklı yatırım önerileri sunan yapay zekâ destekli bir karar destek platformudur.

**Mevcut prototip**, İstanbul ilçeleri için ulaşım önerileri üretmekte ve bunları web arayüzü üzerinden sunmaktadır. Sistem; açık veri portalları, API entegrasyonları, scraping yöntemleri ve LLM tabanlı analizleri bir araya getirerek çok kriterli ve açıklanabilir öneriler sağlar.

### 🚀 Özellikler

- İlçe Bazlı Ulaşım Analizi
- Çok Kaynaklı Veri Entegrasyonu
- LLM Destekli Politika Analizleri (Claude 4.5)
- Basit Web Arayüzü (HTML/CSS/JS)
- Modüler Mimari (Diğer şehirlere genişletilebilir)
- Geliştirme Aşamasında: GIS analizleri & MCDA

### 🧠 Sistem Mimarisi

- Veri Toplama Modülleri (API, scraping)
- Analiz Motoru (Python)
- LLM Öneri Motoru (OpenRouter + Claude 4.5)
- Web Sunucusu
- ETL Boru Hatları
- İlçe Bazlı Öneri Arayüzü

### 📌 Mevcut Durum

- İstanbul için ilk ulaşım öneri modeli çalışıyor.
- İlçe bazlı öneri üretebilen bir web arayüzü aktif.
- Bazı veriler erişilebilir olmadığı için prototipte tahmini veriler kullanılıyor.
- Veri erişimi sağlandıkça doğruluk artacak şekilde tasarlandı.
- Sağlık ve çevre gibi diğer alanlara yönelik prototipler geliştiriliyor.

---

## 🇬🇧 English Description

### 🏙️ AI-Assisted Urban Investment Recommendation Platform

This platform analyzes critical urban needs and provides data-driven investment suggestions for municipalities and institutions.

The current prototype generates district-level transportation recommendations for Istanbul and delivers them through a simple web interface. The system combines open data portals, scraping modules, API integrations, and LLM-based reasoning (Claude 4.5) to generate explainable, multi-criteria suggestions.

### 🚀 Features

- District-Level Transport Recommendations
- Multi-Source Data Integration
- LLM-Powered Policy Analysis
- Lightweight Web UI (HTML/CSS/JS)
- Modular Architecture (Easy to scale to new cities)
- In Development: GIS spatial analysis & MCDA

### 🧠 System Architecture

- Data Collection Modules (API, scraping)
- Python Analysis Engine
- LLM Recommendation Engine (OpenRouter + Claude 4.5)
- Web Server
- ETL Pipelines
- District Recommendation Interface

### 📌 Current Status

- The first transportation model for Istanbul is functional.
- Web-based district recommendation interface is live.
- Some datasets are inaccessible, so estimated values are used in parts of the prototype.
- Model accuracy will increase as real datasets become available.
- New prototypes for environment, health, and infrastructure are being developed.

---

## 📁 Project Structure (Sample)

- `kod/` – Python analysis modules, LLM engines, scraping tools
- `web/` – User-facing UI
- `veriler/` – Data files
- `requirements.txt` – Dependencies

---

## 📜 License

MIT License

---

Hazırlayan: Kerem Doğan
