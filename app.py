import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.platypus import *
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Gyanin ERP", layout="centered")

# ================= GOOGLE SHEET CONFIG =================
sheet_id = "1Qy6io_C1oO9iqyGyhxvFywoskc_vIEXvb1s5z5hjcic"

# 👉 IMPORTANT: Check gid from your sheet
question_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
users_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=1"

# ================= LOAD DATA =================
@st.cache_data
def load_data():
    df = pd.read_csv(question_url)
    users_df = pd.read_csv(users_url)

    # Clean login data
    users_df['Username'] = users_df['Username'].astype(str).str.strip()
    users_df['Password'] = users_df['Password'].astype(str).str.strip()

    df['Class'] = df['Class'].astype(str)

    return df, users_df

df, users_df = load_data()

# ================= LOGIN SYSTEM =================
def login():
    st.sidebar.title("🔐 Login")

    username = st.sidebar.text_input("Username").strip()
    password = st.sidebar.text_input("Password", type="password").strip()

    if st.sidebar.button("Login"):
        user = users_df[
            (users_df['Username'] == username) &
            (users_df['Password'] == password)
        ]

        if not user.empty:
            st.session_state['logged_in'] = True
            st.session_state['role'] = user.iloc[0]['Role']
            st.success("Login Successful")
        else:
            st.error("Invalid Credentials")

def logout():
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False

# ================= SESSION CONTROL =================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login()
    st.stop()
else:
    logout()

# ================= MAIN TITLE =================
st.title("🏫 Gyanin Academy ERP System")

# ================= ADMIN PANEL =================
if st.session_state['role'] == "admin":
    st.header("🛠 Admin Panel (Add Question)")

    qid = st.text_input("Question ID")
    qclass = st.text_input("Class")
    subject = st.text_input("Subject")
    chapter = st.text_input("Chapter")

    qtype = st.selectbox("Type", ["MCQ","SHORT","3MARK","CASE","LONG"])
    difficulty = st.selectbox("Difficulty", ["Easy","Medium","Hard"])

    qtext = st.text_area("Question Text")

    optA = st.text_input("Option A")
    optB = st.text_input("Option B")
    optC = st.text_input("Option C")
    optD = st.text_input("Option D")

    answer = st.text_input("Correct Answer")
    marks = st.text_input("Marks")
    solution = st.text_area("Solution")

    if st.button("Generate Row (Copy to Sheet)"):
        st.success("Copy this and paste into Google Sheet")

        st.code(f"{qid}\t{qclass}\t{subject}\t{chapter}\t{qtype}\t{difficulty}\t{qtext}\t{optA}\t{optB}\t{optC}\t{optD}\t{answer}\t{marks}\t{solution}\t0\t")

# ================= TEACHER PANEL =================
st.header("📄 Generate Question Paper")

classes = sorted(df['Class'].unique())
subjects = sorted(df['Subject'].unique())

selected_class = st.selectbox("Select Class", classes)
selected_subject = st.selectbox("Select Subject", subjects)

filtered_df = df[
    (df['Class'] == selected_class) &
    (df['Subject'] == selected_subject)
]

# ================= PAPER GENERATION =================
def generate_paper():
    return {
        "MCQ": filtered_df[filtered_df['Question_Type']=="MCQ"].head(5),
        "SHORT": filtered_df[filtered_df['Question_Type']=="SHORT"].head(2),
        "3MARK": filtered_df[filtered_df['Question_Type']=="3MARK"].head(2),
        "CASE": filtered_df[filtered_df['Question_Type']=="CASE"].head(1),
        "LONG": filtered_df[filtered_df['Question_Type']=="LONG"].head(1)
    }

# ================= PDF GENERATION =================
def create_pdf(paper):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>GYANIN ACADEMY</b>", styles['Title']))
    story.append(Paragraph("8/2 Mandeville Garden, Kolkata - 700006", styles['Normal']))
    story.append(Paragraph("Ph: 8334006669", styles['Normal']))
    story.append(Spacer(1,10))

    story.append(Paragraph("<b>Question Paper</b>", styles['Heading2']))
    story.append(Spacer(1,10))

    for sec in paper:
        story.append(Paragraph(f"<b>{sec}</b>", styles['Heading3']))

        for i,row in enumerate(paper[sec].itertuples(),1):
            story.append(Paragraph(f"Q{i}. {row.Question_Text}", styles['Normal']))

            if sec == "MCQ":
                story.append(Paragraph(f"A. {row.Option_A}", styles['Normal']))
                story.append(Paragraph(f"B. {row.Option_B}", styles['Normal']))
                story.append(Paragraph(f"C. {row.Option_C}", styles['Normal']))
                story.append(Paragraph(f"D. {row.Option_D}", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ================= GENERATE BUTTON =================
if st.button("Generate Paper"):
    paper = generate_paper()

    st.success("✅ Paper Generated")

    pdf = create_pdf(paper)

    st.download_button(
        "📥 Download PDF",
        pdf,
        "Gyanin_Paper.pdf"
    )

# ================= STUDENT PRACTICE =================
st.header("🧑‍🎓 Student Practice Test")

mcq = filtered_df[filtered_df['Question_Type']=="MCQ"].head(5)

score = 0

for i,row in enumerate(mcq.itertuples(),1):
    st.write(f"Q{i}. {row.Question_Text}")

    ans = st.radio(
        f"Choose answer for Q{i}",
        [row.Option_A, row.Option_B, row.Option_C, row.Option_D],
        key=i
    )

    if ans == row.Correct_Answer:
        score += 1

if st.button("Submit Test"):
    st.success(f"Score: {score}/5")
