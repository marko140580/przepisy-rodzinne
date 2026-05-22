import streamlit as st
import json
import os
import re

st.set_page_config(page_title="Menedżer Przepisów", page_icon="🍲", layout="wide")

LINK_APLIKACJI = "https://streamlit.app"

# Bezpieczne ładowanie danych w chmurze
if "przepisy" not in st.session_state:
    if os.path.exists("baza_przepisow_v3.json"):
        try:
            with open("baza_przepisow_v3.json", "r", encoding="utf-8") as f:
                st.session_state.przepisy = json.load(f)
        except:
            st.session_state.przepisy = []
    else:
        st.session_state.przepisy = []

def zapisz_baze():
    with open("baza_przepisow_v3.json", "w", encoding="utf-8") as f:
        json.dump(st.session_state.przepisy, f, ensure_ascii=False, indent=4)

def pobierz_miniaturke_sieciowa(adres_url):
    url_str = str(adres_url).strip()
    if not url_str:
        return "https://unsplash.com"
    if "youtube.com" in url_str or "youtu.be" in url_str:
        regula = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        znaleziono = re.search(regula, url_str)
        if znaleziono:
            return f"https://youtube.com{znaleziono.group(1)}/hqdefault.jpg"
    if "tiktok.com" in url_str:
        return "https://unsplash.com"
    return "https://unsplash.com"

# DEKORATOR OKNA DIALOGOWEGO - Stabilne edytowanie w chmurze
@st.dialog("Edytuj przepis")
def okno_edycji(przepis_id):
    # Znajdź przepis w sesji
    przepis = next((p for p in st.session_state.przepisy if p["id"] == przepis_id), None)
    if przepis:
        e_tytul = st.text_input("Nazwa potrawy:", value=przepis["tytul"])
        e_link = st.text_input("Link (TikTok / YouTube):", value=przepis["link"])
        e_foto = st.text_input("Link do zdjęcia www:", value=przepis["foto"])
        e_skladniki = st.text_area("Składniki (jeden pod drugim):", value=przepis["skladniki"])
        e_instrukcja = st.text_area("Sposób przygotowania:", value=przepis["instrukcja"])
        
        col_e1, col_e2 = st.columns(2)
        with col_e1: e_czas = st.text_input("Czas:", value=przepis["czas"])
        with col_e2: e_temp = st.text_input("Temperatura:", value=przepis["temp"])
        
        if st.button("💾 Zapisz zmiany", width="stretch", type="primary"):
            if e_tytul:
                przepis.update({
                    "tytul": e_tytul, "link": e_link, "foto": e_foto,
                    "skladniki": e_skladniki, "instrukcja": e_instrukcja,
                    "czas": e_czas, "temp": e_temp
                })
                zapisz_baze()
                st.success("Zapisano!")
                st.rerun()
            else:
                st.error("Nazwa potrawy nie może być pusta!")

# GLÓWNA STRONA
st.title("🍲 Menedżer Przepisów Social Media")

with st.expander("🔗 Zgubiłeś link? Udostępnij tę aplikację rodzinie!", expanded=False):
    st.write("Skopiuj poniższy link i wyślij go przez Messenger, GG lub SMS:")
    st.code(LINK_APLIKACJI, language="text")

st.write("---")

# PANEL BOCZNY - DODAWANIE PRZEPISU
with st.sidebar:
    st.header("➕ Dodaj przepis")
    with st.form("formularz_dodawania", clear_on_submit=True):
        tytul = st.text_input("Nazwa potrawy:")
        platforma = st.selectbox("Źródło:", ["YouTube", "TikTok", "Internet", "Inne"])
        kategoria = st.selectbox("Kategoria:", ["Obiady", "Śniadania", "Desery", "Alkohole", "Inne"])
        link = st.text_input("Link do wideo / strony (opcjonalny):")
        urzadzenie = st.selectbox("Urządzenie:", ["Piekarnik", "Airfryer", "Kombiwar", "Patelnia", "Garnek", "Inne"])
        foto_www = st.text_input("Link do zdjęcia z internetu (opcjonalny):", placeholder="https://...jpg")
        skladniki = st.text_area("Składniki (jeden pod drugim):")
        instrukcja = st.text_area("Sposób przygotowania:")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1: czas = st.text_input("Czas (np. 30):")
        with col_s2: temp = st.text_input("Temp (np. 180):")
        
        sprawdzone = st.checkbox("Przepis sprawdzony ✅")
        mamy = st.checkbox("Przepis Mamy ❤️")
        internet = st.checkbox("Przepis z internetu 🌐")
        
        przycisk_zapisz = st.form_submit_button("Zapisz przepis w bazie", width="stretch")
        
        if przycisk_zapisz and tytul:
            identyfikator = str(os.urandom(4).hex())
            sciezka_foto = foto_www.strip() if foto_www.strip() else pobierz_miniaturke_sieciowa(link)
                
            nowy_przepis = {
                "id": identyfikator, "tytul": tytul, "platforma": platforma, "kategoria": kategoria,
                "link": link, "urzadzenie": urzadzenie, "skladniki": skladniki, "instrukcja": instrukcja,
                "czas": czas, "temp": temp, "sprawdzone": sprawdzone, "mamy": mamy, "internet": internet, "foto": sciezka_foto
            }
            st.session_state.przepisy.append(nowy_przepis)
            zapisz_baze()
            st.success("Dodano przepis!")
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

# FILTROWANIE
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

# WYŚWIETLANIE KAFELKÓW
if not wyswietlane:
    st.info("Brak przepisów lub książka kucharska jest pusta.")
else:
    kolumny_siatki = st.columns(3)
    for numer, przepis in enumerate(wyswietlane):
        cel_kolumna = kolumny_siatki[numer % 3]
        with cel_kolumna:
            with st.container(border=True):
                st.image(przepis["foto"], width="stretch")
                
                odznaki = []
                if p_sp := przepis.get("sprawdzone"): odznaki.append("✅ Sprawdzony")
                if p_in := przepis.get("internet"): odznaki.append("🌐 Internet")
                if p_ma := przepis.get("mamy"): odznaki.append("❤️ Przepis Mamy")
                str_odznaki = " | " + ", ".join(odznaki) if odznaki else ""
                
                st.subheader(f"{przepis['tytul']}{str_odznaki}")
                st.caption(f"📂 Kat: {przepis['kategoria']} | ⚙️ {przepis.get('urzadzenie', 'Inne')} | ⏱️ {przepis['czas']} min | 🌡️ {przepis['temp']}°C")
                
                col_skł, col_prz = st.columns(2)
                with col_skł:
                    st.write("**📝 Składniki:**")
                    st.text(przepis["skladniki"] if przepis["skladniki"].strip() else "Brak")
                with col_prz:
                    st.write("**🍳 Przygotowanie:**")
                    st.write(przepis["instrukcja"] if przepis["instrukcja"].strip() else "Brak")
                
                c_b1, c_b2, c_b3 = st.columns(3)
                with c_b1:
                    if przepis["link"].strip(): st.link_button("Link ↗", przepis["link"], width="stretch")
                    else: st.write("Brak")
                with c_b2:
                    # Wywołanie nowego, okienkowego systemu edycji
                    if st.button("✏️ Edytuj", key=f"e_{przepis['id']}", width="stretch"):
                        okno_edycji(przepis["id"])
                with c_b3:
                    if st.button("🗑️ Usuń", key=f"d_{przepis['id']}", type="secondary", width="stretch"):
                        st.session_state.przepisy = [x for x in st.session_state.przepisy if x["id"] != przepis["id"]]
                        zapisz_baze()
                        st.rerun()
