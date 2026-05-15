import streamlit as st
import json
import os
import time
import re
from groq import Groq

st.set_page_config(page_title="Trung tam Hoc tap", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
}
.app-header {
    text-align: center;
    padding: 25px 20px;
    margin-bottom: 30px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}
.app-title {
    font-size: 2rem;
    font-weight: bold;
    color: white;
}
.app-subtitle {
    font-size: 0.9rem;
    color: #e0d4ff;
}
div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
}
div[data-testid="stSidebar"] * {
    color: white !important;
}
.stButton button {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 30px;
    padding: 8px 20px;
    font-weight: bold;
    transition: 0.3s;
}
.stButton button:hover {
    transform: scale(1.02);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}
div[data-testid="column"] {
    background-color: rgba(255,255,255,0.9);
    border-radius: 20px;
    padding: 20px;
    margin: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    transition: 0.3s;
}
div[data-testid="column"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}
.info-box {
    background-color: #e0f7fa;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 20px;
}
</style>

<div class="app-header">
    <div class="app-title">TRUNG TAM HOC TAP</div>
    <div class="app-subtitle">He sinh thai hoc tap thong minh | Hoc vui, nho lau</div>
</div>

<div class="info-box">
    Huong dan nhanh: Chon cong cu ben trai -> Nhap du lieu -> Bam nut de thuc hien.
</div>
""", unsafe_allow_html=True)

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

FLASHCARD_FILE = "the_hoc.json"

def load_cards():
    if os.path.exists(FLASHCARD_FILE):
        with open(FLASHCARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_cards(cards):
    with open(FLASHCARD_FILE, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)

def the_hoc_ui():
    st.subheader("The hoc thong minh")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("Them the moi")
        mat_truoc = st.text_input("Mat truoc (cau hoi / tu vung)")
        mat_sau = st.text_area("Mat sau (dap an / nghia)")
        if st.button("Luu the", use_container_width=True):
            if mat_truoc and mat_sau:
                cards = load_cards()
                cards.append({"front": mat_truoc, "back": mat_sau})
                save_cards(cards)
                st.success("Da them the!")
                st.balloons()
    with col2:
        st.markdown("On tap")
        cards = load_cards()
        if cards:
            if "card_idx" not in st.session_state:
                st.session_state.card_idx = 0
                st.session_state.show_back = False
            the = cards[st.session_state.card_idx]
            st.info(f"The {st.session_state.card_idx + 1}/{len(cards)}")
            st.markdown(f"**Mat truoc:** {the['front']}")
            if st.button("Xem dap an", use_container_width=True):
                st.session_state.show_back = True
            if st.session_state.show_back:
                st.success(f"**Mat sau:** {the['back']}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("The truoc", use_container_width=True):
                    st.session_state.card_idx = (st.session_state.card_idx - 1) % len(cards)
                    st.session_state.show_back = False
            with c2:
                if st.button("The sau", use_container_width=True):
                    st.session_state.card_idx = (st.session_state.card_idx + 1) % len(cards)
                    st.session_state.show_back = False
        else:
            st.warning("Chua co the nao. Hay them the o cot ben trai.")

def gia_su_ai_ui():
    st.subheader("Gia su AI")
    cau_hoi = st.text_area("Nhap cau hoi / bai toan cua ban", height=150)
    if st.button("Hoi gia su AI", use_container_width=True):
        if cau_hoi:
            with st.spinner("AI dang suy nghi..."):
                prompt = f"Hay giai bai toan sau: {cau_hoi}. Tra loi bang tieng Viet, chi tiet."
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                st.markdown("**Cau tra loi:**")
                st.info(res.choices[0].message.content)

def tao_de_ui():
    st.subheader("Tao de trac nghiem")
    chu_de = st.text_input("Chu de")
    so_cau = st.number_input("So cau hoi", 1, 20, 5)
    if st.button("Tao de", use_container_width=True):
        if chu_de:
            with st.spinner("Dang tao de..."):
                prompt = f"""Tao {so_cau} cau hoi trac nghiem ve '{chu_de}'. Moi cau co 4 dap an A, B, C, D. Dap an dung la mot chu cai (A, B, C hoac D). Tra ve dung dinh dang JSON list, vi du:
[
  {{"question": "Cau hoi 1?", "options": ["A. Dap an 1", "B. Dap an 2", "C. Dap an 3", "D. Dap an 4"], "correct": "A"}},
  {{"question": "Cau hoi 2?", "options": ["A. Dap an 1", "B. Dap an 2", "C. Dap an 3", "D. Dap an 4"], "correct": "B"}}
]
Chi tra ve JSON, khong giai thich them."""
                try:
                    res = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.5
                    )
                    text = res.choices[0].message.content
                    json_match = re.search(r'\[.*\]', text, re.DOTALL)
                    if json_match:
                        cau_hois = json.loads(json_match.group())
                    else:
                        cau_hois = json.loads(text)
                    st.session_state.quiz_questions = cau_hois
                    st.session_state.quiz_answers = {}
                    st.success(f"Da tao {len(cau_hois)} cau hoi!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Loi tao de: {e}")
                    st.code(text if 'text' in locals() else "Khong co phan hoi tu AI")
    if "quiz_questions" in st.session_state:
        for i, q in enumerate(st.session_state.quiz_questions):
            st.markdown(f"**{i+1}. {q['question']}**")
            dap_an = st.radio(
                "Chon dap an",
                q['options'],
                key=f"quiz_{i}",
                index=None,
                format_func=lambda x: x
            )
            st.session_state.quiz_answers[i] = dap_an
        if st.button("Nop bai", use_container_width=True):
            diem = 0
            ket_qua = []
            for i, q in enumerate(st.session_state.quiz_questions):
                chon = st.session_state.quiz_answers.get(i)
                correct_option = q['correct']
                if len(correct_option) == 1 and correct_option in ['A','B','C','D']:
                    for opt in q['options']:
                        if opt.startswith(correct_option + '.'):
                            correct_full = opt
                            break
                    else:
                        correct_full = correct_option
                else:
                    correct_full = correct_option
                
                if chon == correct_full:
                    diem += 1
                    ket_qua.append(f"Cau {i+1}: Dung")
                else:
                    ket_qua.append(f"Cau {i+1}: Sai (Dap an dung: {correct_full})")
            st.balloons()
            st.success(f"Dung {diem}/{len(st.session_state.quiz_questions)}")
            with st.expander("Xem chi tiet"):
                for kq in ket_qua:
                    st.write(kq)

def hen_gio_ui():
    st.subheader("Hen gio hoc tap (Pomodoro)")
    phut_hoc = st.number_input("Phut hoc", 1, 60, 25)
    phut_nghi = st.number_input("Phut nghi", 1, 30, 5)
    if "pomo_state" not in st.session_state:
        st.session_state.pomo_state = "hoc"
        st.session_state.pomo_time = phut_hoc * 60
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Bat dau", use_container_width=True):
            st.session_state.pomo_state = "hoc"
            st.session_state.pomo_time = phut_hoc * 60
    with col2:
        if st.button("Dat lai", use_container_width=True):
            st.session_state.pomo_state = "hoc"
            st.session_state.pomo_time = phut_hoc * 60
    with col3:
        if st.button("Nghi ngay", use_container_width=True):
            st.session_state.pomo_state = "nghi"
            st.session_state.pomo_time = phut_nghi * 60
    phut = st.session_state.pomo_time // 60
    giay = st.session_state.pomo_time % 60
    st.markdown(f"<h1 style='text-align: center; font-size: 3rem;'>{phut:02d}:{giay:02d}</h1>", unsafe_allow_html=True)
    tong = phut_hoc * 60 if st.session_state.pomo_state == "hoc" else phut_nghi * 60
    st.progress(1 - st.session_state.pomo_time / tong)

def ghi_chu_ui():
    st.subheader("Ghi chu thong minh")
    ghi_chu = st.text_area("Nhap noi dung ghi chu", height=200)
    if st.button("Tom tat bang AI", use_container_width=True):
        if ghi_chu:
            with st.spinner("Dang tom tat..."):
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"Hay tom tat noi dung sau:\n\n{ghi_chu}"}]
                )
                st.markdown("**Tom tat:**")
                st.success(res.choices[0].message.content)

def lo_trinh_ui():
    st.subheader("Lo trinh hoc tap ca nhan")
    muc_tieu = st.text_input("Muc tieu hoc tap cua ban")
    so_ngay = st.number_input("So ngay", 7, 365, 30)
    if st.button("Tao lo trinh", use_container_width=True):
        if muc_tieu:
            with st.spinner("AI dang xay dung lo trinh..."):
                prompt = f"Hay tao lo trinh hoc tap trong {so_ngay} ngay de dat muc tieu: {muc_tieu}."
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.markdown("**Lo trinh hoc tap:**")
                st.info(res.choices[0].message.content)

st.sidebar.markdown("## CONG CU")
cong_cu = st.sidebar.selectbox("Chon cong cu", [
    "The hoc thong minh",
    "Gia su AI",
    "Tao de trac nghiem",
    "Hen gio hoc tap",
    "Ghi chu thong minh",
    "Lo trinh hoc tap"
])

if cong_cu == "The hoc thong minh":
    the_hoc_ui()
elif cong_cu == "Gia su AI":
    gia_su_ai_ui()
elif cong_cu == "Tao de trac nghiem":
    tao_de_ui()
elif cong_cu == "Hen gio hoc tap":
    hen_gio_ui()
elif cong_cu == "Ghi chu thong minh":
    ghi_chu_ui()
else:
    lo_trinh_ui()

st.sidebar.markdown("---")
st.sidebar.markdown("📂 Du lieu the hoc luu trong file `the_hoc.json`")
st.sidebar.markdown("---")
st.sidebar.markdown("👨‍💻 **Tac gia:** Nguyen The Anh")
st.sidebar.markdown("📧 baovy06101991@gmail.com")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; padding: 20px;'>"
    "📚 TRUNG TAM HOC TAP | Tac gia: Nguyen The Anh | 📧 baovy06101991@gmail.com"
    "</div>",
    unsafe_allow_html=True
)
