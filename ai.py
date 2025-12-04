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
    # ... di dalam fungsi generate_recipe(bahan_input) ...

    # Prompt Engineering Baru: Lebih ketat, minta variasi, dan inovasi!
    prompt_saya = f"""
    Anda adalah asisten masak profesional yang berfokus pada masakan rumahan Indonesia.
    Tugas Anda adalah membuat 1 (satu) rekomendasi resep masakan Indonesia yang **kreatif, tidak umum, dan variatif**.
    Gunakan bahan-bahan utama berikut: **{bahan_input}**.
    
    Persyaratan Ekstra:
    1. Hindari resep yang sangat umum (misal: hanya Tumis Kangkung, Dadar Telur, atau Sayur Bening).
    2. Resep harus praktis dan menggunakan bumbu yang umum ada di dapur Indonesia.
    3. Jika memungkinkan, berikan rekomendasi dari **masakan daerah yang berbeda** (Sumatera, Jawa, Sulawesi, dll.).
    
    Format Jawaban (Wajib):
    
    ## 🍲 Nama Masakan: [NAMA RESEP YANG ENAK DAN UNIK]
    
    ### 🛒 Bahan yang Diperlukan (Di luar Bahan Utama):
    * [List bahan tambahan, misal: Cabai, Santan, Minyak, dll]
    
    ### 👨‍🍳 Langkah Memasak:
    1. [Langkah 1]
    2. [Langkah 2]
    3. [Langkah 3, dst]
    
    ---
    
    **💡 Opsi Lain:** Jika resep di atas kurang sreg, Anda bisa mencoba resep berikut: [Sebutkan 1-2 ide nama masakan lain, tanpa detail resep].
    
    Selamat bekerja!
    """
    
    # ... sisa fungsi tetap sama ...
    
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

