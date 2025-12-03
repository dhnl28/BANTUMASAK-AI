import streamlit as st
from google import genai
from google.genai.errors import APIError

# --- BAGIAN 1: KONFIGURASI DAN INICIALISASI (SUDAH DIUBAH) ---

# 1. Ambil API Key dari Streamlit Secrets
# Kita minta Streamlit cari variabel GEMINI_API_KEY di file secrets.toml
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    # Kalo key gak ketemu di secrets.toml
    st.error("⚠️ Bro, API Key lo belum diset di file .streamlit/secrets.toml!")
    st.error("Tolong buat file itu dan isi GEMINI_API_KEY = \"KEY_LO\" ")
    st.stop() # Hentikan aplikasi

# Inisialisasi klien Gemini
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Gagal koneksi ke Gemini API: {e}")
    st.stop()

# --- BAGIAN 2: FUNGSI UTAMA (OTAK AI) ---

def generate_recipe(bahan_input):
    """
    Fungsi ini yang akan kontak ke Gemini dan meminta resep.
    """
    # Prompt Engineering: Kunci sukses AI ada di sini!
    prompt_saya = f"""
    Anda adalah asisten masak profesional yang berfokus pada masakan rumahan Indonesia. 
    Tugas Anda adalah membuat 1 (satu) rekomendasi resep masakan Indonesia yang lezat dan realistis, 
    berdasarkan bahan-bahan utama berikut: **{bahan_input}**.
    
    Persyaratan:
    1. Resep harus praktis dan menggunakan bumbu yang umum ada di dapur Indonesia (bawang, garam, dsb.).
    2. Format jawaban harus rapi dan jelas.
    
    Format Hasil:
    
    ## 🍲 Nama Masakan: [NAMA RESEP YANG ENAK]
    
    ### 🛒 Bahan yang Diperlukan (Di luar Bahan Utama):
    * [List bahan tambahan, misal: Cabai, Santan, Minyak, dll]
    
    ### 👨‍🍳 Langkah Memasak:
    1. [Langkah 1]
    2. [Langkah 2]
    3. [Langkah 3, dst]
    
    Selamat bekerja!
    """
    
    # Panggil model Gemini (kita pakai gemini-2.5-flash karena cepat dan pintar)
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_saya
        )
        return response.text
        
    except APIError as e:
        return f"🚨 API Error: Terjadi masalah saat menghubungi Gemini. ({e})"
    except Exception as e:
        return f"🚨 Error: Terjadi kesalahan tak terduga: {e}"

# --- BAGIAN 3: INTERFACE STREAMLIT (TAMPILAN) ---

# Atur tampilan judul dan deskripsi aplikasi
st.title("👨‍🍳 Tukang Sayur AI: Rekomendasi Resep Kilat")
st.caption("Dibangun menggunakan Python, Streamlit, dan Google Gemini API.")
st.write("Bro, masukin bahan-bahan yang lo punya sekarang, nanti gue cariin resep masakan Indonesia yang cocok!")

# Input area untuk bahan-bahan
bahan_user = st.text_area(
    "Contoh: Bayam, Jagung Manis, Kemiri, Bawang Merah",
    height=150,
    placeholder="Coba ketik bahan yang lo beli di tukang sayur..."
)

# Tombol untuk eksekusi
if st.button("Cari Resep, Gas!"):
    if bahan_user:
        # Tampilkan status loading saat AI bekerja
        with st.spinner('AI sedang meramu resep... 🧠'):
            # Panggil fungsi utama kita
            resep_final = generate_recipe(bahan_user)
        
        # Tampilkan hasilnya
        st.markdown("---")
        st.header("✅ Hasil Resep Rekomendasi:")
        st.code(resep_final)
        st.markdown("---")
        st.success("Selamat mencoba, Bro! Jangan lupa bagi-bagi masakannya.")

    else:

        st.warning("Jangan kosong, Bro! Isi dulu bahannya!")
