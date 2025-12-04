import streamlit as st
from google import genai
from google.genai.errors import APIError

# --- BAGIAN 1: KONFIGURASI DAN INICIALISASI ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("⚠️ Bro, API Key lo belum diset di file .streamlit/secrets.toml!")
    st.stop()

MODEL = "gemini-2.5-flash"

if "gemini_client" not in st.session_state:
    try:
        st.session_state["gemini_client"] = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Gagal koneksi ke Gemini API: {e}")
        st.stop()
        
client = st.session_state["gemini_client"]

# --- BAGIAN 2: SETUP STREAMLIT CHAT UI dan DIVERSIFIKASI ---

st.title("👨‍🍳 Tukang Sayur AI Chat: Resep Interaktif")
st.caption("Masukin bahan lo, lalu lo bisa minta menu lain, ganti rasa, atau tambah bahan!")

# Memastikan 'messages' selalu ada di Session State
st.session_state.setdefault("messages", [])

# Inisialisasi Chat Session Gemini
if "chat" not in st.session_state:

    system_instruction = (
        "Anda adalah Asisten Masak AI yang sangat kreatif, berfokus pada masakan rumahan "
        "Indonesia dari berbagai daerah. Dalam setiap respons, Anda **wajib** memberikan "
        "resep yang variatif dan tidak monoton. Respon pertama Anda harus meminta daftar bahan. "
        "Setelah user memberikan daftar bahan, berikan 1 rekomendasi resep dalam format Markdown rapi."
        "Jika user memberikan instruksi lanjutan (misal: 'ganti', 'pedas', 'tambah'), "
        "Anda harus merespon dengan rekomendasi resep baru, tanpa mengulang resep sebelumnya, "
        "dan tetap menggunakan bahan utama dari pesan pertama user."
    )

    try:
        initial_history = [
            {"role": "user", "parts": [{"text": system_instruction}]},
            {"role": "model", "parts": [
                {"text": "Halo Bro! Saya Asisten Masak lo. Bahan-bahan apa aja yang lo punya sekarang? Sebutin aja semua!"}]},
        ]

        st.session_state["chat"] = client.chats.create(
            model=MODEL,
            history=initial_history
        )

        st.session_state.messages.append(
            {"role": "assistant", "content": initial_history[1]['parts'][0]['text']})

    except Exception as e:
        st.error(f"Gagal membuat sesi chat Gemini: {e}")
        st.stop()

# --- BAGIAN 3: MENAMPILKAN RIWAYAT CHAT ---

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- BAGIAN 4: INPUT USER DAN PENGIRIMAN PROMPT (FINAL FIX) ---

# Input teks klasik
prompt_input = st.text_input(
    "Masukkan bahan atau instruksi lanjutan (Contoh: 'Bayam, Jagung') atau ('Ganti yang lebih pedas')",
    key="user_input_key"
)

# Tombol untuk mengirim prompt, TANPA on_click!
if st.button("Kirim Prompt"):
    
    prompt = prompt_input
    
    if prompt: # Cek jika input TIDAK kosong
        
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            if st.session_state["chat"] is None:
                st.error("🚨 Sesi chat belum terinisialisasi. Coba refresh halaman.")
                st.stop()
                
            response = st.session_state.chat.send_message(prompt)

            with st.chat_message("assistant"):
                st.markdown(response.text)

            st.session_state.messages.append(
                {"role": "assistant", "content": response.text})

            # KITA HAPUS st.session_state.user_input_key = "" DI SINI!

        except APIError as e:
            with st.chat_message("assistant"):
                st.error(f"🚨 API Error: Terjadi masalah saat menghubungi Gemini. ({e})")
        except Exception as e:
            with st.chat_message("assistant"):
                st.error(f"🚨 Error: Terjadi kesalahan tak terduga: {e}")
                st.session_state["chat"] = None
    else:
        # Ini hanya muncul jika lo klik tombol tapi tidak ada teks di input
        st.warning("Input tidak boleh kosong!")

# --- END OF CODE ---
