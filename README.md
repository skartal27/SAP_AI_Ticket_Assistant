# SATA - SAP MM AI Ticket & Diagnostic Assistant

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sap-ai-ticket-assistant-sata.streamlit.app)
[![SAP S/4HANA](https://img.shields.io/badge/SAP-S%2F4HANA%20MM-0073E6.svg)](https://www.sap.com/)
[![Compliance](https://img.shields.io/badge/EU%20AI%20Act-Compliant%20(HitL)-green.svg)]()

> 🌐 **Live Demo:** [sap-ai-ticket-assistant-sata.streamlit.app](https://sap-ai-ticket-assistant-sata.streamlit.app)

**SATA** ist ein domänenspezifischer, multimodaler KI-Copilot für den **SAP MM (Materialwirtschaft)** L1/L2-Support mit integrierter **Human-in-the-Loop (HitL)** ERP-Governance.

---

## 🎯 Kernfunktionen

* **Multimodale Schnittstelle:** Direkte Texteingabe, Ticket-PDF-Analyse und SAP GUI Screenshot-OCR.
* **SAP MM Diagnostics:** Schnelle Ursachenanalyse und Transaktionscode-Empfehlungen (`MIGO`, `MM01`, `MMPV`, `MMRV`, `MMBE`).
* **SATA Governance Gateway:** Keine unkontrollierten ERP-Schreibzugriffe. Transaktionen (`BAPI_GOODSMVT_CREATE`) erfordern eine explizite Benutzerfreigabe mit revisionssicherem Audit-Log nach EU AI Act Vorgaben.
* **Enterprise Security:** Sichere API-Verwaltung über Streamlit Secrets (keine offenen API-Schlüssel).

---

## 🏗️ Systemarchitektur

```text
[ SAP GUI / User Incident ] ───► (Text / PDF / Screenshot OCR)
                                              │
                                              ▼
[ Diagnostic Copilot Engine ] ◄───► [ Curated SAP Knowledge & Rules ]
                                              │
                                              ▼
[ Human-in-the-Loop Layer ] ────► [ Revisionssicherer Audit Trail ]
                                              │ (Freigabe durch Consultant)
                                              ▼
                                 [ SAP ERP Action Advice ]
```

---

## 🚀 Ausführung

1. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Konfiguration:**
   Erstelle `.streamlit/secrets.toml`:
   ```toml
   GEMINI_API_KEY = "DEIN_API_SCHLÜSSEL"
   ```

3. **Anwendung starten:**
   ```bash
   streamlit run app.py
   ```

---

## 👨‍💻 Kontakt & Entwicklung

**Mahmut Şahin**  
*Zertifizierter SAP S/4HANA Berater (MM/SD)*  
* Spezialisierung: SAP S/4HANA Logistik, Geschäftsprozessintegration & Enterprise AI Assistenzsysteme.
