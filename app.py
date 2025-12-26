import streamlit as st
import google.generativeai as genai

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="AI Scientific Editor Pro",
    page_icon="🧬",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {font-size: 30px; font-weight: bold; color: #2C3E50;}
    .step-container {background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px;}
    .reviewer-box {background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 5px solid #ffc107; margin-bottom: 10px;}
    .success-box {background-color: #d4edda; padding: 15px; border-radius: 5px; border-left: 5px solid #28a745;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR & API SETUP ---
st.sidebar.title("⚙️ Konfigurasi")
st.sidebar.info("Dibuat untuk membantu publikasi Jurnal Internasional (Scopus Q1/Q2)")

api_key = st.sidebar.text_input("Masukkan Google Gemini API Key:", type="password")
model_choice = st.sidebar.selectbox("Pilih Model:", ["gemini-1.5-flash", "gemini-1.5-pro"])

if api_key:
    genai.configure(api_key=api_key)

# --- FUNGSI GENERATOR AI ---
def get_gemini_response(prompt):
    if not api_key:
        return "Error: API Key belum dimasukkan."
    try:
        model = genai.GenerativeModel(model_choice)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- STATE MANAGEMENT ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'draft' not in st.session_state: st.session_state.draft = ""
if 'paper_type' not in st.session_state: st.session_state.paper_type = "Original Article"
if 'selected_title' not in st.session_state: st.session_state.selected_title = ""
if 'pre_paper' not in st.session_state: st.session_state.pre_paper = ""
if 'reviews' not in st.session_state: st.session_state.reviews = ""
if 'post_paper' not in st.session_state: st.session_state.post_paper = ""

# --- MAIN APP ---
st.markdown('<div class="main-header">🧬 AI Agent: Premium Scientific Publication</div>', unsafe_allow_html=True)

# === STEP 1: INPUT DRAFT ===
if st.session_state.step == 1:
    with st.container():
        st.markdown("### 1️⃣ Upload Draft & Tipe Naskah")
        st.session_state.paper_type = st.selectbox("Pilih Tipe Naskah:", 
            ["Original Article", "SLR/Meta-Analysis", "Case Report"])
        
        draft_input = st.text_area("Masukkan Draft Kasar / Abstrak / Poin-poin Data:", height=250)
        
        if st.button("Analisis & Buat Judul 🚀"):
            if draft_input and api_key:
                st.session_state.draft = draft_input
                st.session_state.step = 2
                st.rerun()
            elif not api_key:
                st.error("Masukkan API Key di sidebar dulu ya!")
            else:
                st.warning("Mohon isi draft naskah.")

# === STEP 2: TITLE BRAINSTORMING ===
elif st.session_state.step == 2:
    st.markdown("### 2️⃣ Pemilihan Judul (Scored 1-10)")
    
    if 'titles_generated' not in st.session_state:
        prompt_title = f"""
        Bertindak sebagai Editor Jurnal Q1 (Nature/Lancet). Berdasarkan draft ini: 
        "{st.session_state.draft[:1000]}"...
        
        Tugas: Berikan 5 usulan judul terbaik.
        Kriteria: Akademis, Menarik, Spesifik.
        Output Format: List bullet, sertakan Skor (1-10) dan Alasan singkat.
        """
        with st.spinner("AI sedang berpikir keras..."):
            st.session_state.titles_generated = get_gemini_response(prompt_title)
            
    st.info(st.session_state.titles_generated)
    
    user_title = st.text_input("Salin & Tempel judul yang Anda pilih di sini:")
    
    if st.button("Setujui Judul & Tulis Pre-Paper 📝"):
        if user_title:
            st.session_state.selected_title = user_title
            st.session_state.step = 3
            st.rerun()

# === STEP 3: PRE-PAPER GENERATION ===
elif st.session_state.step == 3:
    st.markdown(f"### 3️⃣ Pre-Paper Draft: {st.session_state.paper_type}")
    
    if st.session_state.pre_paper == "":
        structure_prompt = ""
        if st.session_state.paper_type == "Original Article":
            structure_prompt = "Struktur: Abstract (Intro, Methods, Results, Conclusion, Keywords MeSH), Introduction (Akhiri dgn Novelty & Aim), Methods, Results (Deskripsikan Tabel/Gambar), Discussion (FOKUS PATOFISIOLOGI & Biomolekuler), Conclusion, References (Vancouver, Real DOI)."
        elif st.session_state.paper_type == "SLR/Meta-Analysis":
            structure_prompt = "Struktur: Abstract (Structured), Introduction (Novelty & Aim), Methods (PRISMA compliant), Results (Table/Chart description), Discussion (Pathophysiology perspective), Conclusion, References (Vancouver, Real DOI)."
        else: 
            structure_prompt = "Struktur: Abstract, Introduction, Case Presentation (Detail klinis), Discussion (Pathophysiology of the case), Conclusion, References."

        full_prompt = f"""
        Role: Senior Medical Writer. Buat naskah ilmiah lengkap.
        Judul: {st.session_state.selected_title}
        Draft User: {st.session_state.draft}
        Instruksi Khusus: {structure_prompt}
        """
        
        with st.spinner("Menulis naskah awal..."):
            st.session_state.pre_paper = get_gemini_response(full_prompt)
    
    st.text_area("Hasil Pre-Paper:", st.session_state.pre_paper, height=400)
    st.download_button("Download Pre-Paper (.txt)", st.session_state.pre_paper)
    
    if st.button("Lanjut ke Proses Review 🕵️‍♂️"):
        st.session_state.step = 4
        st.rerun()

# === STEP 4: REVIEWER SIMULATION ===
elif st.session_state.step == 4:
    st.markdown("### 4️⃣ Simulasi Peer Review")
    
    if st.session_state.reviews == "":
        with st.spinner("Mengirim naskah ke Reviewer..."):
            prompt_review = f"""
            Role: Reviewer Jurnal Internasional. Review naskah ini: {st.session_state.pre_paper}.
            Output: Kritik pedas substantif (Reviewer 1: Metodologi, Reviewer 2: Patofisiologi).
            """
            st.session_state.reviews = get_gemini_response(prompt_review)
    
    st.markdown('<div class="reviewer-box">' + st.session_state.reviews.replace('\n', '<br>') + '</div>', unsafe_allow_html=True)
    st.download_button("Download Hasil Review", st.session_state.reviews)
    
    if st.button("Generate Post-Paper (Final Version) ✨"):
        st.session_state.step = 5
        st.rerun()

# === STEP 5: POST-PAPER FINALIZATION ===
elif st.session_state.step == 5:
    st.markdown("### 5️⃣ Post-Paper (Publication Ready)")
    
    if st.session_state.post_paper == "":
        with st.spinner("Finalizing Manuscript..."):
            prompt_final = f"""
            Role: Professional Editor. Revisi naskah '{st.session_state.selected_title}' berdasarkan review: {st.session_state.reviews}.
            Syarat: Minimal 6000 kata (jika memungkinkan), gunakan HTML <table> untuk data, References Vancouver style.
            Konten Basis: {st.session_state.pre_paper}
            """
            st.session_state.post_paper = get_gemini_response(prompt_final)
    
    st.components.v1.html(st.session_state.post_paper, height=600, scrolling=True)
    st.download_button("Download Full HTML (.html)", st.session_state.post_paper, file_name="manuscript_final.html")
    
    if st.button("Mulai Project Baru 🔄"):
        st.session_state.clear()
        st.rerun()
