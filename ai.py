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
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- BAGIAN 4: INPUT USER DAN PENGIRIMAN PROMPT (FINAL FIX) ---

# Input teks klasik (Lebih stabil dan kompatibel dengan browser lama)
prompt_input = st.text_input(
    "Masukkan bahan atau instruksi lanjutan (Contoh: 'Bayam, Jagung') atau ('Ganti yang lebih pedas')",
    key="user_input_key"
)

# Tombol untuk mengirim prompt
if st.button("Kirim Prompt"):
    
    # Ambil teks dari input
    prompt = prompt_input
    
    if prompt:
        
        # 1. Tampilkan prompt user di UI
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Tambahkan prompt user ke riwayat chat
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 3. Kirim pesan ke Gemini dan dapatkan respons
        try:
            # Gunakan send_message() untuk chat berkelanjutan
            response = st.session_state.chat.send_message(prompt)

            # 4. Tampilkan respons Gemini di UI
            with st.chat_message("assistant"):
                st.markdown(response.text)

            # 5. Tambahkan respons Gemini ke riwayat chat
            st.session_state.messages.append(
                {"role": "assistant", "content": response.text})

            # Kosongkan input setelah dikirim
            st.session_state.user_input_key = "" # Reset teks input

        except APIError as e:
            with st.chat_message("assistant"):
                st.error(f"🚨 API Error: Terjadi masalah saat menghubungi Gemini. ({e})")
        except Exception as e:
            with st.chat_message("assistant"):
                st.error(f"🚨 Error: Terjadi kesalahan tak terduga: {e}")
    else:
        st.warning("Input tidak boleh kosong!")

# --- END OF CODE ---
