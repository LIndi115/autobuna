import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import base64

# --- 1. KONFIGURIMI I CLOUD (FIREBASE) ---
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        cred = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://herolind-6ca5f-default-rtdb.europe-west1.firebasedatabase.app/'
        })
    except Exception as e:
        st.error(f"Gabim në lidhjen me Cloud: {e}")

def load_cloud(path):
    res = db.reference(path).get()
    return res if res is not None else []

def save_cloud(path, data):
    db.reference(path).set(data)

# --- 2. KONFIGURIMI I UI ---
st.set_page_config(page_title="AUTO BUNA PRO 2026", layout="wide", page_icon="🚗")

st.markdown("""
    <style>
    .fatura-container { padding: 40px; border: 1px solid #000; background-color: #fff; color: #000; font-family: 'Courier New', monospace; }
    .stButton>button { background-color: #e60073; color: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

stoku = load_cloud('stoku')
historiku = load_cloud('historiku')
investimet = load_cloud('investimet')

# --- 3. NAVIGIMI ---
with st.sidebar:
    st.title("🚗 AUTO BUNA")
    menu = st.radio("MENUJA:", ["📊 Dashboard", "📦 Gjendja e Stokut", "📥 Pranim Malli", "💸 Shitje & Faturë"])
    st.info("📍 Fushë Kosovë")

# --- 4. LOGJIKA ---

if menu == "📊 Dashboard":
    st.title("📊 Pasqyra e Biznesit")
    # Llogaritja e thjeshtë për test
    hyrje = sum(float(i.get('shuma_blerjes', 0)) for i in investimet)
    dalje = sum(float(h.get('total', 0)) for h in historiku)
    c1, c2 = st.columns(2)
    c1.metric("Totali i Investuar", f"{hyrje:,.2f} €")
    c2.metric("Totali i Shitur", f"{dalje:,.2f} €")

elif menu == "📦 Gjendja e Stokut":
    st.title("📦 Gjendja e Stokut (Live)")
    search = st.text_input("🔍 Kërko...", "").upper()
    
    if stoku:
        # Përdorim .get() për të shmangur KeyError nëse mungon ndonjë fushë si 'ana'
        for index, row in enumerate(stoku):
            m = row.get('marka', 'Pa emër')
            mod = row.get('modeli', '-')
            a = row.get('ana', 'Nuk është specifikuar')
            s = row.get('sasia', 0)
            
            if search in m or search in mod:
                with st.expander(f"📌 {m} {mod} - {a}"):
                    st.write(f"**Sasia:** {s} | **Blerja:** {row.get('blerja', 0)}€")
                    if st.button("🗑️ FSHIJ", key=f"del_{index}"):
                        stoku.pop(index)
                        save_cloud('stoku', stoku)
                        st.rerun()
    else:
        st.info("Depoja është e zbrazët.")

elif menu == "📥 Pranim Malli":
    st.title("📥 Regjistrim i Ri")
    with st.form("forma_pranim"):
        marka = st.text_input("Marka:").upper()
        modeli = st.text_input("Modeli:").upper()
        ana = st.selectbox("Ana:", ["MAJTAS (L)", "DJATHTAS (R)", "SET (L+R)", "Nuk ka anë"])
        sasia = st.number_input("Sasia:", min_value=1)
        blerja = st.number_input("Çmimi Blerjes (€):", min_value=0.0)
        
        if st.form_submit_button("RUAJ NË CLOUD"):
            data_str = datetime.now().strftime("%d-%m-%Y")
            stoku.append({"data": data_str, "marka": marka, "modeli": modeli, "ana": ana, "sasia": sasia, "blerja": blerja})
            investimet.append({"data": data_str, "shuma_blerjes": sasia * blerja})
            save_cloud('stoku', stoku)
            save_cloud('investimet', investimet)
            st.success("U ruajt!")

elif menu == "💸 Shitje & Faturë":
    st.title("💸 Shitje")
    if stoku:
        klienti = st.text_input("Klienti:")
        opsionet = [f"{i.get('marka')} {i.get('modeli')} ({i.get('sasia')})" for i in stoku]
        zgjedh = st.selectbox("Produkti:", opsionet)
        idx = opsionet.index(zgjedh)
        s_sh = st.number_input("Sasia:", min_value=1, max_value=int(stoku[idx].get('sasia', 1)))
        c_sh = st.number_input("Çmimi:", min_value=0.0)
        
        if st.button("KRYEJ SHITJEN"):
            stoku[idx]['sasia'] -= s_sh
            total = s_sh * c_sh
            historiku.append({"klienti": klienti, "total": total, "data_shitjes": datetime.now().strftime("%d-%m-%Y")})
            if stoku[idx]['sasia'] <= 0: stoku.pop(idx)
            save_cloud('stoku', stoku)
            save_cloud('historiku', historiku)
            st.success(f"Shitja u krye! Total: {total} €")
