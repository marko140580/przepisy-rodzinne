
import streamlit as st
import json
import os
import re

st.set_page_config(page_title="Menedżer Przepisów", page_icon="🍲", layout="wide")

# Używamy wbudowanej bazy Streamlit do trwałego zapisu w chmurze
if "przepisy" not in st.session_state:
    if os.path.exists("baza_przepisow_v3.json"):
        try:
            with open("baza_przepisow_v3.json", "r", encoding="utf-8") as f:
                st.session_state.przepisy = json.load(f)
        except:
            st.session_state.przepisy = []
    else:
        st.session_state.przepisy = []

if "id_edytowanego" not in st.session_state:
    st.session_state.id_edytowanego = None

def zapisz_baze():
    with open("baza_przepisow_v3.json", "w", encoding="utf-8") as f:
        json.dump(st.session_state.przepisy, f, ensure_ascii=False, indent=4)

def pobierz_miniaturke_yt(adres_url):
    if "youtube.com" in adres_url or "youtu.be" in adres_url:
        regula = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        znaleziono = re.search(regula, adres_url)
        if znaleziono:
            return f"https://youtube.com{znaleziono.group(1)}/hqdefault.jpg"
    return "https://unsplash.com"

st.title("🍲 Menedżer Przepisów Social Media")

# PANEL BOCZNY - DODAWANIE PRZEPISU
with st.sidebar:
    st.header("➕ Dodaj przepis")
    with st.form("formularz_dodawania", clear_on_submit=True):
        tytul = st.text_input("Nazwa potrawy:")
        platforma = st.selectbox("Źródło:", ["YouTube", "TikTok", "Internet", "Inne"])
        kategoria = st.selectbox("Kategoria:", ["Obiady", "Śniadania", "Desery", "Alkohole", "Inne"])
        link = st.text_input("Link do wideo / strony:")
        urzadzenie = st.selectbox("Urządzenie:", ["Piekarnik", "Airfryer", "Kombiwar", "Patelnia", "Garnek", "Inne"])
        plik_foto = st.file_uploader("Dodaj zdjęcie potrawy:", type=["jpg", "jpeg", "png"])
        skladniki = st.text_area("Składniki:")
        instrukcja = st.text_area("Sposób przygotowania:")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1: czas = st.text_input("Czas:")
        with col_s2: temp = st.text_input("Temp:")
        
        sprawdzone = st.checkbox("Przepis sprawdzony ✅")
        mamy = st.checkbox("Przepis Mamy ❤️")
        internet = st.checkbox("Przepis z internetu 🌐")
        
        przycisk_zapisz = st.form_submit_button("Zapisz przepis w bazie", width="stretch")
        
        if przycisk_zapisz and tytul:
            identyfikator = str(os.urandom(4).hex())
            sciezka_foto = "https://unsplash.com"
            if link.strip():
                sciezka_foto = pobierz_miniaturke_yt(link)
                
            nowy_przepis = {
                "id": identyfikator, "tytul": tytul, "platforma": platforma, "kategoria": kategoria,
                "link": link, "urzadzenie": urzadzenie, "skladniki": skladniki, "instrukcja": instrukcja,
                "czas": czas, "temp": temp, "sprawdzone": sprawdzone, "mamy": mamy, "internet": internet, "foto": sciezka_foto
            }
            st.session_state.przepisy.append(nowy_przepis)
            zapisz_baze()
            st.success("Dodano!")
            st.rerun()

# PANEL GŁÓWNY - FILTRY
f_szukaj, f_kat, f_tagi, f_urzadzenie = st.columns(4)
with f_szukaj:
    szukaj = st.text_input("🔍 Szukaj potrawy:", placeholder="Wpisz słowo...")
with f_kat:
    kat_wybrane = st.multiselect("Kategoria:", ["Obiady", "Śniadania", "Desery", "Alkohole", "Inne"])
with f_tagi:
    tagi_wybrane = st.multiselect("Typ przepisu:", ["Tylko sprawdzone ✅", "Tylko Przepisy Mamy ❤️", "Tylko z internetu 🌐"])
with f_urzadzenie:
    urzadzenia_wybrane = st.multiselect("Urządzenie:", ["Piekarnik", "Airfryer", "Kombiwar", "Patelnia", "Garnek", "Inne"])

# OKNO EDYCJI
if st.session_state.id_edytowanego is not None:
    przepis_do_edytowania = next((p for p in st.session_state.przepisy if p["id"] == st.session_state.id_edytowanego), None)
    if przepis_do_edytowania is not None:
        st.warning(f"✏️ Edycja przepisu: {przepis_do_edytowania['tytul']}")
        with st.form("formularz_edycji"):
            e_tytul = st.text_input("Nazwa potrawy:", value=przepis_do_edytowania["tytul"])
            e_link = st.text_input("Link:", value=przepis_do_edytowania["link"])
            e_skladniki = st.text_area("Składniki:", value=przepis_do_edytowania["skladniki"])
            e_instrukcja = st.text_area("Przygotowanie:", value=przepis_do_edytowania["instrukcja"])
            e_czas = st.text_input("Czas:", value=przepis_do_edytowania["czas"])
            e_temp = st.text_input("Temperatura:", value=przepis_do_edytowania["temp"])
            e_sprawdzone = st.checkbox("Sprawdzone ✅", value=przepis_do_edytowania.get("sprawdzone", False))
            e_mamy = st.checkbox("Przepis Mamy ❤️", value=przepis_do_edytowania.get("mamy", False))
            e_internet = st.checkbox("Z internetu 🌐", value=przepis_do_edytowania.get("internet", False))
            
            btn_z1, btn_z2 = st.columns(2)
            with btn_z1: zapisz_zm = st.form_submit_button("💾 Zapisz", width="stretch")
            with btn_z2: anuluj_zm = st.form_submit_button("❌ Anuluj", width="stretch")
            
            if zapisz_zm and e_tytul:
                przepis_do_edytowania.update({
                    "tytul": e_tytul, "link": e_link, "skladniki": e_skladniki, "instrukcja": e_instrukcja,
                    "czas": e_czas, "temp": e_temp, "sprawdzone": e_sprawdzone, "mamy": e_mamy, "internet": e_internet
                })
                zapisz_baze()
                st.session_state.id_edytowanego = None
                st.rerun()
            if anuluj_zm:
                st.session_state.id_edytowanego = None
                st.rerun()

# PRZETWARZANIE FILTRÓW
wyswietlane = []
for p in st.session_state.przepisy:
    stan = True
    if szukaj and szukaj.lower() not in p["tytul"].lower() and szukaj.lower() not in p["skladniki"].lower(): stan = False
    if kat_wybrane and p["kategoria"] not in kat_wybrane: stan = False
    if urzadzenia_wybrane and p.get("urzadzenie", "Inne") not in urzadzenia_wybrane: stan = False
    if "Tylko sprawdzone ✅" in tagi_wybrane and not p.get("sprawdzone"): stan = False
    if "Tylko Przepisy Mamy ❤️" in tagi_wybrane and not p.get("mamy"): stan = False
    if "Tylko z internetu 🌐" in tagi_wybrane and not p.get("internet"): stan = False
    if stan: wyswietlane.append(p)

st.write("---")

# WYŚWIETLANIE
if not wyswietlane:
    st.info("Brak przepisów lub książka kucharska jest pusta.")
else:
    for przepis in wyswietlane:
        with st.container(border=True):
            st.image(przepis["foto"], width=300)
            
            odznaki = []
            if przepis.get("sprawdzone"): odznaki.append("✅ Sprawdzony")
            if przepis.get("internet"): odznaki.append("🌐 Internet")
            if przepis.get("mamy"): odznaki.append("❤️ Przepis Mamy")
            str_odznaki = " | " + ", ".join(odznaki) if odznaki else ""
            
            st.subheader(f"{przepis['tytul']} ({przepis['platforma']}){str_odznaki}")
            st.caption(f"📂 Kategoria: {przepis['kategoria']} | ⚙️ Urządzenie: {przepis.get('urzadzenie', 'Inne')} | ⏱️ Czas: {przepis['czas']} | 🌡️ Temp: {przepis['temp']}")
            
            col_skł, col_prz = st.columns(2)
            with col_skł:
                st.write("**📝 Składniki:**")
                st.text(przepis["skladniki"] if przepis["skladniki"].strip() else "Brak")
            with col_prz:
                st.write("**🍳 Przygotowanie:**")
                st.write(przepis["instrukcja"] if przepis["instrukcja"].strip() else "Brak")
            
            c_b1, c_b2, c_b3 = st.columns(3)
            with c_b1:
                if przepis["link"].strip(): st.link_button("Otwórz Link ↗", przepis["link"], width="stretch")
                else: st.write("Brak odnośnika")
            with c_b2:
                if st.button("✏️ Edytuj", key=f"e_{przepis['id']}", width="stretch"):
                    st.session_state.id_edytowanego = przepis["id"]
                    st.rerun()
            with c_b3:
                if st.button("🗑️ Usuń", key=f"d_{przepis['id']}", type="secondary", width="stretch"):
                    st.session_state.przepisy = [x for x in st.session_state.przepisy if x["id"] != przepis["id"]]
                    zapisz_baze()
                    st.rerun()
