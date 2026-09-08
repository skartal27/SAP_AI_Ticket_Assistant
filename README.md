# 🔷 SATA - SAP MM AI Ticket & Diagnostic Assistant

**SATA** ist ein domänenspezifischer, multimodaler KI-Copilot für den **SAP MM (Materialwirtschaft)** L1/L2-Support mit integrierter **Human-in-the-Loop (HitL)** ERP-Governance.

---

## 🎯 Kernfunktionen
* **Multimodale Schnittstelle:** Direkte Texteingabe, Ticket-PDF-Analyse und SAP GUI Screenshot-OCR.
* **SAP MM Diagnostics:** Schnelle Ursachenanalyse und Transaktionscode-Empfehlungen (`MIGO`, `MM01`, `MMPV`, `MMRV`, `MMBE`).
* **SATA Governance Gateway:** Keine automatisierten ERP-Schreibzugriffe. Transaktionen (`BAPI_GOODSMVT_CREATE`) erfordern eine explizite Benutzerfreigabe mit revisionssicherem Audit-Log.

---

## 🚀 Ausführung
1. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt