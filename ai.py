import streamlit as st
from google import genai
from google.genai.errors import APIError

# --- BAGIAN 1: KONFIGURASI DAN INICIALISASI ---

# Ambil API Key dari Streamlit Secrets (Key harus ditaruh di .streamlit/secrets.toml)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("⚠️ Bro, API Key lo belum diset di file .streamlit/secrets.toml!")
    st.stop()

# Inisialisasi klien Gemini
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Gagal koneksi ke Gemini API: {e}")
    st.stop()

# Set model yang akan digunakan
MODEL = "gemini-2.5-flash"

# --- BAGIAN 2: SETUP STREAMLIT CHAT UI dan DIVERSIFIKASI ---

st.title("👨‍🍳 Tukang Sayur AI Chat: Resep Interaktif")
st.caption("Masukin bahan lo, lalu lo bisa minta menu lain, ganti rasa, atau tambah bahan!")

# Inisialisasi Riwayat Chat di Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Inisialisasi Chat Session Gemini (Kunci Interaktivitas)
if "chat" not in st.session_state:

    # === SYSTEM INSTRUCTION (SINGLE SOURCE OF TRUTH UNTUK DIVERSIFIKASI) ===
    # Instruksi ini kita berikan di history chat untuk menghindari error 'system_instruction'
    system_instruction = (
        "Anda adalah Asisten Masak AI yang sangat kreatif, berfokus pada masakan rumahan "
        "Indonesia dari berbagai daerah. Dalam setiap respons, Anda **wajib** memberikan "
        "resep yang variatif dan tidak monoton. Respon pertama Anda harus meminta daftar bahan. "
        "Setelah user memberikan daftar bahan, berikan 1 rekomendasi resep dalam format Markdown rapi."
        "Jika user memberikan instruksi lanjutan (misal: 'ganti', 'pedas', 'tambah'), "
        "Anda harus merespon dengan rekomendasi resep baru, tanpa mengulang resep sebelumnya, "
        "dan tetap menggunakan bahan utama dari pesan pertama user."
    )
    # =======================================================

    try:
        # 1. Siapkan pesan inisial yang berisi instruksi sistem dan respons AI pertama
        # Perhatikan: Ini adalah cara yang benar untuk memberikan System Instruction ke Chat API
        initial_history = [
            {"role": "user", "parts": [{"text": system_instruction}]},
            {"role": "model", "parts": [
                {"text": "Halo Bro! Saya Asisten Masak lo. Bahan-bahan apa aja yang lo punya sekarang? Sebutin aja semua!"}]},
        ]

        # 2. Kita buat chat session menggunakan history yang sudah ada
        st.session_state["chat"] = client.chats.create(
            model=MODEL,
            history=initial_history  # Gunakan history untuk system instruction
        )

        # 3. Tambahkan pesan pertama AI ke riwayat chat UI (agar langsung muncul di layar)
        st.session_state.messages.append(
            {"role": "assistant", "content": initial_history[1]['parts'][0]['text']})

    except Exception as e:
        st.error(f"Gagal membuat sesi chat Gemini: {e}")
        st.stop()

# --- BAGIAN 3: MENAMPILKAN RIWAYAT CHAT ---

# Tampilkan semua riwayat chat yang sudah disimpan
# --- BAGIAN 3: MENAMPILKAN RIWAYAT CHAT ---

# Tampilkan semua riwayat chat yang sudah disimpan
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"]) # <-- INI PERBAIKANNYA!
