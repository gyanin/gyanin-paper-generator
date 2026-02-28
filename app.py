import streamlit as st
import pandas as pd
import random
from io import BytesIO
from reportlab.platypus import *
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

st.set_page_config(page_title="Gyanin ERP", layout="centered")

# ================= LOGIN =================
USERS = {
    "admin": {"password": "1234", "role": "admin"},
    "teacher": {"password": "1234", "role": "teacher"}
}

def login():
    st.sidebar.title("🔐 Login")
    u = st.sidebar.text_input("Username")
    p = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if u in USERS and USERS[u]["password"] == p:
            st.session_state["logged_in"] = True
            st.session_state["role"] = USERS[u]["role"]
        else:
            st.error("Invalid Login")

def logout():
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()
else:
    logout()

# ================= GOOGLE SHEET =================
sheet_id = "1Qy6io_C1oO9iqyGyhxvFywoskc_vIEXvb1s5z5hjcic"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=QuestionBank"

@st.cache_data
def load_data():
    return pd.read_csv(url)

df = load_data()

# ================= UI =================
st.title("🏫 Gyanin Academy - CBSE Paper Generator")

classes = sorted(df['Class'].astype(str).unique())
subjects = sorted(df['Subject'].unique())

c = st.selectbox("Class", classes)
s = st.selectbox("Subject", subjects)

filtered = df[(df['Class'].astype(str)==c) & (df['Subject']==s)]

# ================= SMART SELECT =================
def select_questions(df, qtype, count):
    subset = df[df['Question_Type'] == qtype]

    easy = subset[subset['Difficulty']=="Easy"]
    med = subset[subset['Difficulty']=="Medium"]
    hard = subset[subset['Difficulty']=="Hard"]

    result = pd.concat([
        easy.sample(min(len(easy), count//3), replace=True),
        med.sample(min(len(med), count//3), replace=True),
        hard.sample(min(len(hard), count - 2*(count//3)), replace=True)
    ])

    return result.sample(frac=1)

def generate_paper():
    return {
        "Section A (1×20=20)": select_questions(filtered,"MCQ",20),
        "Section B (2×10=20)": select_questions(filtered,"SHORT",10),
        "Section C (3×5=15)": select_questions(filtered,"3MARK",5),
        "Section D (Case Study 2×5=10)": select_questions(filtered,"CASE",2),
        "Section E (5×3=15)": select_questions(filtered,"LONG",3)
    }

# ================= PDF =================
def create_pdf(paper):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Logo
    try:
        story.append(Image("logo.png", width=1.5*inch, height=1.5*inch))
    except:
        pass

    # Header
    story.append(Paragraph("<b>GYANIN ACADEMY</b>", styles['Title']))
    story.append(Paragraph("8/2 Mandeville Garden, Kolkata - 700006", styles['Normal']))
    story.append(Paragraph("Ph: 8334006669", styles['Normal']))
    story.append(Spacer(1,10))

    story.append(Paragraph("<b>CBSE Class {} - {}</b>".format(c,s), styles['Heading2']))
    story.append(Paragraph("Time: 3 Hours     Maximum Marks: 80", styles['Normal']))
    story.append(Spacer(1,10))

    # Instructions
    instructions = [
        "All questions are compulsory.",
        "Use of calculator is not permitted.",
        "Marks are indicated against each question.",
        "Attempt all sections."
    ]

    story.append(Paragraph("<b>General Instructions:</b>", styles['Heading3']))
    for ins in instructions:
        story.append(Paragraph(f"- {ins}", styles['Normal']))

    # Sections
    for sec in paper:
        story.append(Spacer(1,10))
        story.append(Paragraph(f"<b>{sec}</b>", styles['Heading3']))

        for i,row in enumerate(paper[sec].itertuples(),1):
            story.append(Paragraph(f"Q{i}. {row.Question_Text}", styles['Normal']))

            if "MCQ" in sec:
                story.append(Paragraph(f"A. {row.Option_A}", styles['Normal']))
                story.append(Paragraph(f"B. {row.Option_B}", styles['Normal']))
                story.append(Paragraph(f"C. {row.Option_C}", styles['Normal']))
                story.append(Paragraph(f"D. {row.Option_D}", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ================= GENERATE =================
if st.button("Generate Full CBSE Paper"):
    paper = generate_paper()

    st.success("✅ Full CBSE Paper Generated")

    pdf = create_pdf(paper)

    st.download_button("📥 Download CBSE Paper", pdf, "Gyanin_CBSE_Paper.pdf")
