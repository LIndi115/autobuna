import streamlit as st
import pandas as pd
import os

# Konfigurimi i Sistemit
DATA_FILE = "arkiva_e_firmes.csv"
PASSWORD = "infra"  # Fjalekalimi i ri i shkurter
FIRM_NAME = "INFRA PROJECT SHPK"

def load_data():
    cols = ["Klienti", "Statusi", "Vlera_Totale", "Paguar", "Kosto_Shtese", "Pershkrimi"]
    if os.path.exists(DATA_FILE):
        try:
            temp_df = pd.read_csv(DATA_FILE)
            for col in cols:
                if col not in temp_df.columns:
                    temp_df[col] = 0.0 if col in ["Vlera_Totale", "Paguar", "Kosto_Shtese"] else ""
            return temp_df[cols]
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

st.set_page_config(page_title=FIRM_NAME, layout="wide", page_icon="🏗️")

# --- DIZAJNI "PREMIUM CORPORATE" ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0e1117; }}
    [data-testid="stSidebar"] {{ background-color: #050505; border-right: 2px solid #ffc107; }}
    
    /* Kartat Moderne */
    .metric-box {{
        background: rgba(255, 255, 255, 0.03);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(255, 193, 7, 0.2);
        text-align: center;
        transition: 0.4s;
    }}
    .metric-box:hover {{
        border: 1px solid #ffc107;
        background: rgba(255, 193, 7, 0.05);
        transform: translateY(-5px);
    }}
    
    /* Titujt */
    .firm-title {{
        font-family: 'Inter', sans-serif;
        color: #ffc107;
        font-weight: 900;
        letter-spacing: 2px;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 20px;
    }}
    
    /* Inputet dhe Formularat */
    .stTextInput>div>div>input {{ background-color: #1a1c23; color: white; border: 1px solid #333; }}
    .stButton>button {{
        background: #ffc107; color: black !important; font-weight: bold;
        border-radius: 12px; border: none; width: 100%; transition: 0.3s;
    }}
    .stButton>button:hover {{ background: #e5ad06; transform: scale(1.02); }}
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMI I HYRJES ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown(f"<h1 class='firm-title'>🏗️ {FIRM_NAME}</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1.2,1])
    with c2:
        st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
        st.markdown("<p style='color: gray;'>Sistemi i Autorizuar i Menaxhimit</p>", unsafe_allow_html=True)
        pass_input = st.text_input("", type="password", placeholder="Shkruaj fjalëkalimin...")
        if st.button("HYR NË PANEL"):
            if pass_input == PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Qasja u refuzua!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- PROGRAMI ---
if 'projekte' not in st.session_state:
    st.session_state.projekte = load_data()

df = st.session_state.projekte

# SIDEBAR BRANDING
st.sidebar.markdown(f"<h3 style='color:#ffc107; text-align:center;'>{FIRM_NAME}</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")
nav = st.sidebar.radio("MENYJA:", ["💎 Dashboard", "🕵️ Arkiva / Search", "📝 Regjistro Punë"])

if nav == "💎 Dashboard":
    st.markdown(f"<h2 style='color:white;'>📊 Pasqyra Financiare</h2>", unsafe_allow_html=True)
    if not df.empty:
        total_puna = df['Vlera_Totale'].sum() + df['Kosto_Shtese'].sum()
        total_paguar = df['Paguar'].sum()
        total_borxh = total_puna - total_paguar
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-box'><small>TOTALI KONTRATUAR</small><h2 style='color:#ffc107;'>{total_puna:,.2f} €</h2></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-box'><small>ARKËTUAR (CASH)</small><h2 style='color:#00ff88;'>{total_paguar:,.2f} €</h2></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-box'><small>BORXHE AKTIVE</small><h2 style='color:#ff4b4b;'>{total_borxh:,.2f} €</h2></div>", unsafe_allow_html=True)
    else:
        st.info("Mirësevini. Sistemi është bosh, shtoni projektin e parë.")

elif nav == "🕵️ Arkiva / Search":
    st.markdown("<h2 style='color:white;'>🔍 Kërkimi i Klientëve</h2>", unsafe_allow_html=True)
    if df.empty:
        st.warning("Nuk ka klientë në arkivë.")
    else:
        search = st.text_input("Shkruaj emrin e klientit:", placeholder="Psh: Agon Berisha...")
        filtered = df[df['Klienti'].str.contains(search, case=False, na=False)]
        
        if not filtered.empty:
            sel_client = st.selectbox("Zgjidh për të parë kartelën:", filtered['Klienti'].unique())
            p = df[df['Klienti'] == sel_client].iloc[0]
            v_finale = p['Vlera_Totale'] + p['Kosto_Shtese']
            b_mbetur = v_finale - p['Paguar']
            prog = (p['Paguar'] / v_finale) if v_finale > 0 else 0
            
            st.markdown(f"<div class='metric-box' style='text-align:left;'>", unsafe_allow_html=True)
            col_l, col_r = st.columns(2)
            with col_l:
                st.markdown(f"<h3 style='color:#ffc107;'>👤 {sel_client}</h3>", unsafe_allow_html=True)
                st.write(f"📍 Statusi: **{p['Statusi']}**")
                st.write(f"💰 Kontrata: **{p['Vlera_Totale']:,.2f} €**")
                st.write(f"🛠️ Shtesë: **{p['Kosto_Shtese']:,.2f} €**")
            with col_r:
                st.markdown("<h4>📈 Statusi i Pagesës</h4>", unsafe_allow_html=True)
                st.progress(prog)
                st.success(f"✅ Paguar: {p['Paguar']:,.2f} €")
                st.error(f"⚠️ Borxh: {b_mbetur:,.2f} €")
            st.markdown(f"<hr><p style='color:gray;'>📝 <b>Shënime:</b> {p['Pershkrimi']}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

elif nav == "📝 Regjistro Punë":
    st.markdown("<h2 style='color:white;'>➕ Shto Kontratë të Re</h2>", unsafe_allow_html=True)
    with st.form("new_infra", clear_on_submit=True):
        f1, f2 = st.columns(2)
        emri = f1.text_input("Klienti / Objekti")
        vlera = f1.number_input("Vlera e Kontratës (€)", min_value=0.0)
        pag = f2.number_input("Pagesa e parë (€)", min_value=0.0)
        sht = f2.number_input("Kosto shtesë (€)", min_value=0.0)
        stat = st.selectbox("Statusi", ["Në Fillim", "Në Punë", "I Kryer"])
        desc = st.text_area("Specifikat e punës")
        if st.form_submit_button("RUAJ TË DHËNAT"):
            if emri:
                new_data = {"Klienti": emri, "Statusi": stat, "Vlera_Totale": vlera, "Paguar": pag, "Kosto_Shtese": sht, "Pershkrimi": desc}
                st.session_state.projekte = pd.concat([st.session_state.projekte, pd.DataFrame([new_data])], ignore_index=True)
                save_data(st.session_state.projekte)
                st.success("Të dhënat u arkivuan!")
                st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("🔓 LOGOUT"):
    st.session_state.authenticated = False
    st.rerun()
