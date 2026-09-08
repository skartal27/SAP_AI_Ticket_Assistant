import streamlit as st
import json
import random
from datetime import datetime
from PIL import Image
from pypdf import PdfReader
import google.generativeai as genai

# SATA Logolu Özel SVG Favicon
sata_favicon = """data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%230f2d59'/><text x='50%' y='58%' dominant-baseline='middle' text-anchor='middle' font-family='Arial, sans-serif' font-weight='bold' font-size='32' fill='%23ffffff'>SATA</text></svg>"""

# Sayfa Yapılandırması
st.set_page_config(
    page_title="SATA - SAP AI Ticket Assistant",
    page_icon=sata_favicon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- KURUMSAL SAP FIORI & SATA UI TEMASI ---
st.markdown("""
<style>
    /* Ana Gövde */
    .stApp {
        background-color: #f4f6f9;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }

    /* Sol Kenar Çubuğu */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #d9e1ec;
    }

    /* SAP Fiori Shell Header */
    .sap-fiori-header {
        background: linear-gradient(135deg, #0a2540 0%, #174276 100%);
        padding: 24px 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(10, 37, 64, 0.08);
    }
    .sap-fiori-header h1 {
        color: #ffffff !important;
        font-size: 1.85rem !important;
        font-weight: 700;
        margin: 0 0 6px 0 !important;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
    }
    .sap-fiori-header p {
        color: #cbdcf5 !important;
        font-size: 0.95rem;
        margin: 0;
    }

    /* SATA Rozetleri */
    .sap-tag {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: #e9f2ff;
        color: #0056b3;
        border: 1px solid #c8deff;
        margin-right: 8px;
    }
    .sap-tag-active {
        background-color: #e6f9f0;
        color: #0d8a4f;
        border-color: #a8ebd0;
    }

    /* Giriş Sekmeleri (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #e8edf3;
        padding: 6px;
        border-radius: 10px;
        border-bottom: none;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
        color: #475569;
        background-color: transparent;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #0070f2 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }

    /* Giriş Alanı Kartı */
    .sap-card {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 12px;
        border: 1px solid #e1e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        margin-top: 14px;
        margin-bottom: 22px;
    }

    /* SATA Governance & Approval Card */
    .sata-card {
        background: #ffffff;
        border: 1px solid #d0d7de;
        border-left: 6px solid #0070f2;
        border-radius: 8px;
        padding: 18px 22px;
        margin: 18px 0;
        box-shadow: 0 4px 12px rgba(0, 50, 120, 0.06);
    }
    .sata-badge {
        background-color: #0f2d59;
        color: #ffffff;
        font-weight: 700;
        padding: 3px 9px;
        border-radius: 4px;
        font-size: 0.8rem;
        letter-spacing: 0.5px;
        display: inline-block;
        margin-bottom: 6px;
    }

    /* Metrik Alanları */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 14px;
    }

    /* Sohbet Mesajları */
    div[data-testid="stChatMessage"] {
        background-color: #ffffff;
        border-radius: 10px;
        border: 1px solid #e5e9f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# --- MOCK SAP BAPI ENGINE ---
def mock_sap_bapi_goodsmvt_create(material: str, plant: str, movement_type: str, qty: float):
    doc_number = f"49{random.randint(10000000, 99999999)}"
    current_year = datetime.now().year
    return {
        "status": "SUCCESS",
        "material_document": doc_number,
        "doc_year": current_year,
        "parameters": {"MATERIAL": material, "PLANT": plant, "BWART": movement_type, "ENTRY_QNT": qty},
        "sap_return_message": f"S: M7 001 - Materialbeleg {doc_number} im Werk {plant} erfolgreich gebucht.",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# --- YARDIMCI FONKSİYONLAR ---
def load_knowledge_base():
    try:
        with open("data/sap_knowledge.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def extract_pdf_text(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Fehler beim Lesen der PDF: {e}"

# --- STATE YÖNETİMİ ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pending_bapi" not in st.session_state:
    st.session_state.pending_bapi = None

knowledge_base = load_knowledge_base()

# --- SEITENLEISTE (EINSTELLUNGEN) ---
with st.sidebar:
    st.markdown('<span class="sap-tag sap-tag-active">● Connected to ERP (PR1)</span>', unsafe_allow_html=True)
    st.header("⚙️ Einstellungen")
    
    ai_provider = st.selectbox(
        "KI-Anbieter",
        ["Gemini", "OpenAI (Demnächst)"],
        index=0
    )
    
    gemini_api_key = st.text_input(
        "Gemini API-Schlüssel:",
        type="password",
        help="Geben Sie hier Ihren Google AI Studio API-Schlüssel ein."
    )
    
    output_language = st.selectbox(
        "Ausgabesprache",
        ["Deutsch", "Englisch", "Türkisch"],
        index=0
    )
    
    sap_module = st.selectbox(
        "SAP-Modul",
        ["SAP MM (Materialwirtschaft)", "SAP SD (Vertrieb)", "SAP FI (Finanzwesen)"],
        index=0
    )
    
    st.write("")
    use_rag = st.checkbox(
        "📚 Knowledge Base (RAG) nutzen",
        value=True,
        help="Aktiviert die interne Wissensdatenbank für kundenspezifische SOPs und Z-Transaktionen."
    )
    
    st.markdown("---")
    if st.button("🗑️ Konversation zurücksetzen (Reset)", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.pending_bapi = None
        st.rerun()

# --- ANA EKRAN: SATA HEADER ---
st.markdown("""
<div class="sap-fiori-header">
    <h1>
        <span style="background-color: #0070f2; color: #ffffff; padding: 2px 14px; border-radius: 6px; font-size: 1.4rem; margin-right: 12px; font-weight: 800; letter-spacing: 0.5px;">SATA</span>
        SAP AI Ticket Assistant
    </h1>
    <p>Enterprise L1/L2 Diagnostic Copilot & Human-in-the-Loop Transaction Layer</p>
</div>
""", unsafe_allow_html=True)

# Sistem Bilgi Çubuğu (Badges)
rag_status_class = "sap-tag sap-tag-active" if use_rag else "sap-tag"
rag_status_text = "RAG: Aktiv" if use_rag else "RAG: Inaktiv"

st.markdown(f"""
<div style="margin-bottom: 20px;">
    <span class="sap-tag">Provider: {ai_provider}</span>
    <span class="sap-tag">Modul: {sap_module}</span>
    <span class="{rag_status_class}">{rag_status_text}</span>
</div>
""", unsafe_allow_html=True)

# --- 3 SEÇENEKLİ GİRİŞ ALANI (FIORI TABS) ---
submitted = False
active_text = ""
uploaded_image_file = None

tab1, tab2, tab3 = st.tabs([
    "✍️ Direkte Fehlerbeschreibung (Text)", 
    "📄 Incident-Report (PDF)", 
    "🖼️ SAP GUI Screenshot"
])

with tab1:
    st.markdown('<div class="sap-card">', unsafe_allow_html=True)
    user_text = st.text_area(
        "SAP-Fehlermeldung oder Problembeschreibung eingeben:", 
        height=100, 
        placeholder="z. B. M7 053 Buchen nur in Periode... im Buchungskreis 1000 zulässig."
    )
    if st.button("🚀 Diagnose starten", type="primary", key="btn_text"):
        if user_text.strip():
            active_text = user_text
            submitted = True
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="sap-card">', unsafe_allow_html=True)
    col_pdf1, col_pdf2 = st.columns([1.2, 1])
    with col_pdf1:
        uploaded_pdf = st.file_uploader("Ticketbericht / SOP (PDF) hochladen:", type=["pdf"], key="pdf_upl")
    with col_pdf2:
        pdf_note = st.text_input("Zusatznotiz zum Ticket (optional):", placeholder="z. B. Priorität P2, Bandstillstand droht", key="pdf_note")
    if st.button("📄 PDF analysieren", type="primary", key="btn_pdf"):
        if uploaded_pdf:
            extracted_text = extract_pdf_text(uploaded_pdf)
            active_text = f"Ticket-Bericht (PDF):\n{extracted_text}\n\nZusatznotiz: {pdf_note}"
            submitted = True
        else:
            st.warning("Bitte laden Sie zuerst eine PDF-Datei hoch.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="sap-card">', unsafe_allow_html=True)
    col_img1, col_img2 = st.columns([1.2, 1])
    with col_img1:
        uploaded_image = st.file_uploader("SAP GUI Screenshot auswählen:", type=["png", "jpg", "jpeg"], key="img_upl")
        if uploaded_image:
            st.image(uploaded_image, caption="Vorschau des Screenshots", width=340)
    with col_img2:
        img_note = st.text_input("Ergänzende Anmerkung (optional):", placeholder="z. B. Tritt beim Speichern in MIGO auf", key="img_note")
    if st.button("🖼️ Screenshot analysieren", type="primary", key="btn_img"):
        if uploaded_image:
            uploaded_image_file = Image.open(uploaded_image)
            active_text = f"Screenshot-Analyse angefordert. Notiz: {img_note if img_note else 'Keine Zusatznotiz'}"
            submitted = True
        else:
            st.warning("Bitte laden Sie zuerst einen Screenshot hoch.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- SOHBET DİYALOG ALANI ---
st.markdown("#### 💬 Support-Dialog & Lösungsschritte")

for msg in st.session_state.chat_history:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# --- SATA HUMAN-IN-THE-LOOP FREIGABE-SCHICHT ---
if st.session_state.pending_bapi:
    bapi_data = st.session_state.pending_bapi
    
    st.markdown(f"""
    <div class="sata-card">
        <span class="sata-badge">SATA</span>
        <span style="font-weight: 600; color: #0f2d59; font-size: 1rem; margin-left: 6px;">
            ERP Transaction Gateway &bull; Freigabepflichtiger Vorgang
        </span>
        <p style="margin: 6px 0 14px 0; color: #475569; font-size: 0.9rem;">
            SATA hat die Parameter für <b>BAPI_GOODSMVT_CREATE</b> validiert. Bitte prüfen und autorisieren Sie die Verbuchung:
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Material", bapi_data.get('material', '-'))
    col_m2.metric("Werk", bapi_data.get('plant', '-'))
    col_m3.metric("Bewegungsart (BWART)", bapi_data.get('movement_type', '-'))
    col_m4.metric("Menge", bapi_data.get('qty', 0))

    st.write("")
    btn_c1, btn_c2 = st.columns([1.5, 4])
    with btn_c1:
        if st.button("✅ SATA Freigabe erteilen", type="primary"):
            res = mock_sap_bapi_goodsmvt_create(
                bapi_data.get("material", "N/A"),
                bapi_data.get("plant", "N/A"),
                bapi_data.get("movement_type", "N/A"),
                bapi_data.get("qty", 0)
            )
            st.session_state.pending_bapi = None
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"✅ **[SATA Gateway] Buchung erfolgreich simuliert!**\n\n"
                           f"* **Materialbeleg:** `{res['material_document']}` ({res['doc_year']})\n"
                           f"* **SAP Meldung:** `{res['sap_return_message']}`\n"
                           f"* **Audit Trail:** Transaktion revisionssicher mit Zeitstempel `{res['timestamp']}` protokolliert."
            })
            st.rerun()
    with btn_c2:
        if st.button("❌ Vorgang verwerfen"):
            st.session_state.pending_bapi = None
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "⚠️ **[SATA Gateway] Vorgang abgebrochen:** Die Buchung wurde durch den Anwender abgelehnt. Kein ERP-Schreibzugriff erfolgt."
            })
            st.rerun()

# Takip Soruları Girişi
follow_up = st.chat_input("Ihre Antwort / Rückfrage eingeben...")
if follow_up:
    active_text = follow_up
    submitted = True

# --- LLM ÇAĞRISI ---
if submitted:
    if not gemini_api_key:
        st.error("Bitte tragen Sie zuerst Ihren Gemini API-Schlüssel in den Einstellungen ein.")
    else:
        st.session_state.chat_history.append({"role": "user", "content": active_text})
        
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-3.6-flash")

        rag_context = json.dumps(knowledge_base, ensure_ascii=False) if use_rag else "Keine RAG-Wissensdatenbank aktiv."

        system_prompt = f"""
        Du bist ein Senior SAP Support Copilot namens SATA für das Modul {sap_module}.
        Ausgabesprache: {output_language}.
        
        Wissensbasis (RAG):
        {rag_context}
        
        Richtlinien:
        1. Analysiere Fehlermeldungen strukturiert: Ursache, Transaktionscode (T-Code) und Lösungsschritte.
        2. Frage bei fehlenden Pflichtdaten (z. B. Werk, Materialnummer) präzise nach.
        3. Wenn der Benutzer ausdrücklich eine Buchung/Korrektur wünscht und alle Daten (Material, Werk, Bewegungsart, Menge) vorhanden sind, füge am Ende deiner Antwort folgendes JSON an:
           TRIGGER_BAPI: {{"material": "MAT_NR", "plant": "WERK", "movement_type": "BWART", "qty": MENGE}}
        """

        full_prompt = f"{system_prompt}\n\nBenutzeranfrage: {active_text}"

        try:
            with st.spinner("SATA analysiert das Ticket..."):
                contents = [full_prompt]
                if uploaded_image_file:
                    contents.append(uploaded_image_file)

                response = model.generate_content(contents)
                raw_text = response.text

                if "TRIGGER_BAPI:" in raw_text:
                    parts = raw_text.split("TRIGGER_BAPI:")
                    display_text = parts[0].strip()
                    try:
                        st.session_state.pending_bapi = json.loads(parts[1].strip())
                    except Exception:
                        pass
                else:
                    display_text = raw_text

                st.session_state.chat_history.append({"role": "assistant", "content": display_text})
                st.rerun()

        except Exception as e:
            st.error(f"Fehler bei der Kommunikation mit dem LLM: {e}")