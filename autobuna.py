import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import base64

# --- KONFIGURIMI ---
st.set_page_config(page_title="AUTO BUNA PRO 2026", layout="wide", page_icon="🚗")

# Muajt në Shqip
MUAJT_SHQIP = {
    "01": "Janar", "02": "Shkurt", "03": "Mars", "04": "Prill",
    "05": "Maj", "06": "Qershor", "07": "Korrik", "08": "Gusht",
    "09": "Shtator", "10": "Tetor", "11": "Nëntor", "12": "Dhjetor"
}

# Stili i përmirësuar
st.markdown("""
    <style>
    .fatura-container { 
        padding: 40px; 
        border: 1px solid #000; 
        background-color: #fff; 
        color: #000; 
        font-family: 'Courier New', Courier, monospace;
        line-height: 1.5;
    }
    .signature-section {
        margin-top: 50px;
        display: flex;
        justify-content: space-between;
    }
    .signature-line {
        border-top: 1px solid #000;
        width: 200px;
        text-align: center;
        padding-top: 5px;
    }
    .stButton>button { background-color: #e60073; color: white; border-radius: 8px; font-weight: bold; }
    .delete-btn { color: #ff4b4b; cursor: pointer; border: 1px solid #ff4b4b; padding: 2px 5px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABAZA ---
FILE_STOKU = "stoku_v11.json"
FILE_HISTORIKU = "historiku_v11.json"
FILE_INVESTIMET = "investimet_v11.json"

def load_data(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f: return json.load(f)
    return []

def save_data(data, file):
    with open(file, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)

def create_pdf_download_link(html_content, filename="fatura.html"):
    """Krijon një link shkarkimi (Për PDF mund të përdoret Print -> Save as PDF nga HTML)"""
    b64 = base64.b64encode(html_content.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{filename}" style="text-decoration:none;"><button style="background-color:#28a745; color:white; padding:10px; border:none; border-radius:5px; width:100%; cursor:pointer;">💾 SHKARKO FATURËN (HTML/PDF)</button></a>'

stoku = load_data(FILE_STOKU)
historiku = load_data(FILE_HISTORIKU)
investimet = load_data(FILE_INVESTIMET)

# --- NAVIGIMI ---
with st.sidebar:
    st.title("🚗 AUTO BUNA")
    menu = st.radio("MENUJA:", ["📊 Dashboard", "📦 Gjendja e Stokut", "📥 Pranim Malli", "💸 Shitje & Faturë"])
    st.write("---")
    st.write("📍 Fushë Kosovë")

# --- 1. DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📈 Raporti Mujor i Biznesit")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        vitet = [str(year) for year in range(2024, 2051)]
        viti_zgjedhur = st.selectbox("Zgjidh Vitin:", vitet, index=vitet.index("2026"))
    with col_f2:
        muaji_emri = st.selectbox("Zgjidh Muajin:", list(MUAJT_SHQIP.values()), index=datetime.now().month-1)
    
    muaji_kod = [k for k, v in MUAJT_SHQIP.items() if v == muaji_emri][0]
    kerko_daten = f"{muaji_kod}-{viti_zgjedhur}"

    hyrje_totale = sum(float(i['shuma_blerjes']) for i in investimet if kerko_daten in i['data'])
    dalje_totale = sum(float(h['total']) for h in historiku if kerko_daten in h['data_shitjes'])

    st.write("##")
    c1, c2 = st.columns(2)
    c1.metric("Totali i Investuar", f"{hyrje_totale:,.2f} €")
    c2.metric("Totali i Shitur", f"{dalje_totale:,.2f} €")

# --- 2. GJENDJA E STOKUT (ME OPSION FSHIRJE) ---
elif menu == "📦 Gjendja e Stokut":
    st.title("📦 Malli aktual në Depo")
    search_query = st.text_input("🔍 Kërko mallin...", "").strip().upper()
    
    if stoku:
        df = pd.DataFrame(stoku)
        if search_query:
            mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
            df = df[mask]

        # Shfaqja e tabelës me mundësi fshirjeje
        for index, row in df.iterrows():
            with st.expander(f"📌 {row['marka']} {row['modeli']} - {row['ana']} ({row['sasia']} copë)"):
                col_info, col_del = st.columns([4, 1])
                col_info.write(f"**Data:** {row['data']} | **Viti:** {row['viti']} | **Blerja:** {row['blerja']}€ | **Përshkrimi:** {row['pershkrimi']}")
                if col_del.button("🗑️ FSHIJ", key=f"del_{index}"):
                    stoku.pop(index)
                    save_data(stoku, FILE_STOKU)
                    st.rerun()
    else:
        st.info("Depoja është e zbrazët.")

# --- 3. PRANIM MALLI ---
elif menu == "📥 Pranim Malli":
    st.title("📥 Regjistrim i Mallit të Ri")
    with st.form("forma_pranim", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1: d_r = st.date_input("Data e Pranimit:", datetime.now())
        with c2: marka = st.text_input("Marka:")
        with c3: modeli = st.text_input("Modeli:")
        c4, c5, c6 = st.columns(3)
        with c4: viti = st.text_input("Viti i Prodhimit:")
        with c5: ana = st.selectbox("Ana:", ["MAJTAS (L)", "DJATHTAS (R)", "SET (L+R)"])
        with c6: pershkrimi = st.text_input("Përshkrimi:")
        c7, c8 = st.columns(2)
        with c7: sasia = st.number_input("Sasia:", min_value=1)
        with c8: blerja = st.number_input("Çmimi Blerjes (€):", min_value=0.0)
        
        if st.form_submit_button("KONFIRMO DHE RUAJ"):
            data_str = d_r.strftime("%d-%m-%Y")
            stoku.append({"data": data_str, "marka": marka.upper(), "modeli": modeli.upper(), "viti": viti, "ana": ana, "pershkrimi": pershkrimi, "sasia": sasia, "blerja": blerja})
            investimet.append({"data": data_str, "shuma_blerjes": sasia * blerja})
            save_data(stoku, FILE_STOKU)
            save_data(investimet, FILE_INVESTIMET)
            st.success("U regjistrua!")

# --- 4. SHITJE & FATURË ---
elif menu == "💸 Shitje & Faturë":
    st.title("💸 Shitje dhe Faturim")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        klienti = st.text_input("Emri i Klientit:")
        data_sh = st.date_input("Data e Shitjes:", datetime.now())
    with col_s2:
        tipi = st.radio("Zgjidh:", ["Nga Stoku", "Shkrim i Lirë"])

    if tipi == "Nga Stoku" and stoku:
        opsionet = [f"{i['marka']} {i['modeli']} - {i['ana']} | {i['sasia']} në stok" for i in stoku]
        zgjedh = st.selectbox("Zgjidh produktin:", opsionet)
        idx_s = opsionet.index(zgjedh)
        p_fatura = zgjedh.split(" | ")[0]
        s_max = int(stoku[idx_s]['sasia'])
    else:
        p_fatura = st.text_input("Shkruaj mallin:")
        s_max = 1000
        idx_s = None

    c_p1, c_p2 = st.columns(2)
    with c_p1: s_sh = st.number_input("Sasia:", min_value=1, max_value=s_max)
    with c_p2: c_sh = st.number_input("Çmimi (€):", min_value=0.0)

    if st.button("KRYEJ SHITJEN"):
        total_f = s_sh * c_sh
        if tipi == "Nga Stoku" and idx_s is not None:
            stoku[idx_s]['sasia'] -= s_sh
            if stoku[idx_s]['sasia'] <= 0: stoku.pop(idx_s)
            save_data(stoku, FILE_STOKU)
        
        data_f = data_sh.strftime("%d-%m-%Y")
        historiku.append({"data_shitjes": data_f, "klienti": klienti, "produkti": p_fatura, "sasia": s_sh, "total": total_f})
        save_data(historiku, FILE_HISTORIKU)
        
        # HTML i Faturës për Print dhe Shkarkim
        fatura_html = f"""
        <div class='fatura-container'>
            <h1 style='text-align:center;'>AUTO BUNA</h1>
            <p style='text-align:center;'>Fushë Kosovë | Tel: +383 4X XXX XXX</p>
            <hr>
            <p><b>DATA:</b> {data_f}</p>
            <p><b>KLIENTI:</b> {klienti}</p>
            <p><b>PRODUKTI:</b> {p_fatura}</p>
            <p><b>SASIA:</b> {s_sh} copë</p>
            <p><b>ÇMIMI PËR NJËSI:</b> {c_sh:.2f} €</p>
            <hr>
            <h2 style='text-align:right;'>TOTALI: {total_f:.2f} €</h2>
            <br><br>
            <div class='signature-section'>
                <div class='signature-line'>Nënshkrimi i Shitësit</div>
                <div class='signature-line'>Nënshkrimi i Blerësit</div>
            </div>
            <p style='text-align:center; font-size:10px; margin-top:30px;'>Kjo faturë shërben si dëshmi për blerjen e mallit.</p>
        </div>
        """
        
        st.markdown(fatura_html, unsafe_allow_html=True)
        st.write("---")
        st.markdown(create_pdf_download_link(fatura_html, f"Fatura_{klienti}_{data_f}.html"), unsafe_allow_html=True)
        st.info("Për ta ruajtur si PDF: Hapni skedarin e shkarkuar dhe shtypni Ctrl+P (Print) -> Save as PDF.")
