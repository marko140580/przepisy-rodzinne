import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
import re

st.set_page_config(page_title="Menedżer Przepisów", page_icon="🍲", layout="wide")

# ==============================================================================
# TUTAJ WKLEJ CAŁY LINK DO TWOJEGO ARKUSZA GOOGLE (musi być jako Edytor dla każdego!)
LINK_ARKUSZA_GOOGLE = "TUTAJ_WKLEJ_CALY_LINK_DO_TWOJEGO_ARKUSZA_GOOGLE"
# ==============================================================================

# Funkcja bezpiecznego łączenia z bazą danych online
def wczytaj_dane_z_arkusza():
    try:
        połączenie = st.connection("gsheets", type=GSheetsConnection)
        df = połączenie.read(spreadsheet=LINK_ARKUSZA_GOOGLE, ttl="0")
        df = df.astype(str).replace("nan", "").fillna("")
        
        przepisy = []
        for _, wiersz in df.iterrows():
            if str(wiersz.get("tytul", "")).strip():
                przepisy.append({
                    "id": str(wiersz.get("id", os.urandom(4).hex())),
                    "tytul": str(wiersz.get("tytul", "")),
                    "platforma": str(wiersz.get("platforma", "Inne")),
                    "kategoria": str(wiersz.get("kategoria", "Obiady")),
                    "link": str(wiersz.get("link", "")),
                    "urzadzenie": str(wiersz.get("urzadzenie", "Inne")),
                    "skladniki": str(wiersz.get("skladniki", "")),
                    "instrukcja": str(wiersz.get("instrukcja", "")),
                    "czas": str(wiersz.get("czas", "")),
                    "temp": str(wiersz.get("temp", "")),
                    "sprawdzone": str(wiersz.get("sprawdzone", "False")) == "True",
                    "mamy": str(wiersz.get("mamy", "False")) == "True",
                    "internet": str(wiersz.get("internet", "False")) == "True",
                    "foto": str(wiersz.get("foto", ""))
                })
        return przepisy
    except Exception as e:
        return []

def zapisz_dane_do_arkusza(lista_przepisow):
    try:
        połączenie = st.connection("gsheets", type=GSheetsConnection)
        nowy_df = pd.DataFrame(lista_przepisow)
        połączenie.update(spreadsheet=LINK_ARKUSZA_GOOGLE, data=nowy_df)
        return True
    except:
        return False

def pobierz_miniaturke_sieciowa(adres_url):
    url_str = str(adres_url).strip()
    if not url_str:
        return "https://unsplash.com"
    if "youtube.com" in url_str or "youtu.be" in url_str:
        regula = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        znaleziono = re.search(regula, url_str)
        if znaleziono:
            return f"https://youtube.com{znaleziono.group(1)}/hqdefault.jpg"
    return "https://unsplash.com"

# Odświeżanie i ładowanie danych
if "przepisy" not in st.session_state or st.sidebar.button("🔄 Odśwież przepisy online", width="stretch"):
    st.session_state.przepisy = wczytaj_dane_z_arkusza()

# Okno edycji
@st.dialog("Edytuj przepis")
def okno_edycji(przepis_id):
    przepis = next((p for p in st.session_state.przepisy if p["id"] == p_id), None) if (p_id := przepis_id) else None
    if przepis:
        e_tytul = st.text_input("Nazwa potrawy:", value=przepis["tytul"])
        e_link = st.text_input("Link (TikTok / YouTube):", value=przepis["link"])
        e_foto = st.text_input("Link do zdjęcia www:", value=przepis["foto"])
        e_skladniki = st.text_area("Składniki:", value=przepis["skladniki"])
        e_instrukcja = st.text_area("Sposób przygotowania:", value=przepis["instrukcja"])
        
        col_e1, col_e2 = st.columns(2)
        with col_e1: e_czas = st.text_input("Czas:", value=przepis["czas"])
        with col_e2: e_temp = st.text_input("Temperatura:", value=przepis["temp"])
        
        if st.button("💾 Zapisz zmiany", width="stretch", type="primary"):
            przepis.update({
                "tytul": e_tytul, "link": e_link, "foto": e_foto,
                "skladniki": e_skladniki, "instrukcja": e_instrukcja,
                "czas": e_czas, "temp": e_temp
            })
            if zapisz_dane_do_arkusza(st.session_state.przepisy):
                st.success("Zapisano!")
                st.rerun()
            else:
                st.error("Błąd zapisu w Arkuszu. Sprawdź uprawnienia udostępniania!")

# INTERFEJS STRONY
st.title("🍲 Menedżer Przepisów Karolczak")

# POPRAWIONO: Link wpisany na sztywno, bez możliwości pomyłki serwera
with st.expander("🔗 Udostępnij tę aplikację rodzinie!", expanded=False):
    st.write("Skopiuj poniższy link i wyślij go bliskim:")
    st.code("https://przepisy-rodziny.streamlit.app/", language="text")

st.write("---")

# PANEL BOCZNY - DODAWANIE
with st.sidebar:
    st.header("➕ Dodaj przepis")
    with st.form("formularz_dodawania", clear_on_submit=True):
        tytul = st.text_input("Nazwa potrawy:")
        platforma = st.selectbox("Źródło:", ["YouTube", "TikTok", "Internet", "Inne"])
        kategoria = st.selectbox("Kategoria:", ["Obiady", "Śniadania", "Desery", "Alkohole", "Inne"])
        link = st.text_input("Link do wideo / strony:")
        urzadzenie = st.selectbox("Urządzenie:", ["Piekarnik", "Airfryer", "Kombiwar", "Patelnia", "Garnek", "Inne"])
        foto_www = st.text_input("Link do zdjęcia www:", placeholder="https://...jpg")
        skladniki = st.text_area("Składniki:")
        instrukcja = st.text_area("Sposób przygotowania:")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1: czas = st.text_input("Czas:")
        with col_s2: temp = st.text_input("Temp:")
        
        sprawdzone = st.checkbox("Przepis sprawdzony ✅")
        mamy = st.checkbox("Przepis Mamy ❤️")
        internet = st.checkbox("Przepis z internetu 🌐")
        
        przycisk_zapisz = st.form_submit_button("Zapisz przepis w bazie online", width="stretch")
        
        if przycisk_zapisz and tytul:
            identyfikator = str(os.urandom(4).hex())
            sciezka_foto = foto_www.strip() if foto_www.strip() else pobierz_miniaturke_sieciowa(link)
                
            nowy_przepis = {
                "id": identyfikator, "tytul": tytul, "platforma": platforma, "kategoria": kategoria,
                "link": link, "urzadzenie": urzadzenie, "skladniki": skladniki, "instrukcja": instrukcja,
                "czas": czas, "temp": temp, "sprawdzone": sprawdzone, "mamy": mamy, "internet": internet, "foto": sciezka_foto
            }
            st.session_state.przepisy.append(nowy_przepis)
            if zapisz_dane_do_arkusza(st.session_state.przepisy):
                st.success("Dodano przepis do tabeli online!")
                st.rerun()
            else:
                st.error("Błąd połączenia z Arkuszem Google!")

# FILTRY
f_szukaj, f_kat, f_tagi, f_urzadzenie = st.columns(4)
with f_szukaj: szukaj = st.text_input("🔍 Szukaj potrawy:")
with f_kat: kat_wybrane = st.multiselect("Kategoria:", ["Obiady", "Śniadania", "Desery", "Alkohole", "Inne"])
with f_tagi: tagi_wybrane = st.multiselect("Typ przepisu:", ["Tylko sprawdzone ✅", "Tylko Przepisy Mamy ❤️", "Tylko z internetu 🌐"])
with f_urzadzenie: urzadzenia_wybrane = st.multiselect("Urządzenie:", ["Piekarnik", "Airfryer", "Kombiwar", "Patelnia", "Garnek", "Inne"])

wyswietlane = st.session_state.przepisy
if szukaj: wyswietlane = [p for p in wyswietlane if szukaj.lower() in p["tytul"].lower()]
if kat_wybrane: wyswietlane = [p for p in wyswietlane if p["kategoria"] in kat_wybrane]
if urzadzenia_wybrane: wyswietlane = [p for p in wyswietlane if p.get("urzadzenie", "Inne") in urzadzenia_wybrane]

# WYŚWIETLANIE KAFELKÓW
if not wyswietlane:
    st.info("Książka kucharska online jest pusta lub ładuje dane...")
else:
    kolumny_siatki = st.columns(3)
    for numer, przepis in enumerate(wyswietlane):
        cel_kolumna = kolumny_siatki[numer % 3]
        with cel_kolumna:
            with st.container(border=True):
                st.image(przepis["foto"], width="stretch")
                st.subheader(przepis['tytul'])
                st.caption(f"📂 Kat: {przepis['kategoria']} | ⚙️ {przepis.get('urzadzenie', 'Inne')} | ⏱️ {przepis['czas']} min | 🌡️ {przepis['temp']}°C")
                
                col_skł, col_prz = st.columns(2)
                with col_skł:
                    st.write("**📝 Składniki:**")
                    st.text(przepis["skladniki"])
                with col_prz:
                    st.write("**🍳 Przygotowanie:**")
                    st.write(przepis["instrukcja"])
                
                c_b1, c_b2, c_b3 = st.columns(3)
                with c_b1:
                    if przepis["link"].strip(): st.link_button("Link ↗", przepis["link"], width="stretch")
                    else: st.write("Brak")
                with c_b2:
                    if st.button("✏️ Edytuj", key=f"e_{przepis['id']}", width="stretch"): okno_edycji(przepis["id"])
                with c_b3:
                    if st.button("🗑️ Usuń", key=f"d_{przepis['id']}", type="secondary", width="stretch"):
                        st.session_state.przepisy = [x for x in st.session_state.przepisy if x["id"] != przepis["id"]]
