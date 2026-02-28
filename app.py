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
    st.sidebar.title("Login")
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
st.title("🏫 Gyanin Academy - CBSE Generator")

classes = sorted(df['Class'].astype(str).unique())
subjects = sorted(df['Subject'].unique())

c = st.selectbox("Class", classes)
s = st.selectbox("Subject", subjects)

filtered = df[(df['Class'].astype(str)==c) & (df['Subject']==s)]

# ================= SELECT FUNCTION =================
def select_questions(df, qtype, count):
    subset = df[df['Question_Type'] == qtype]
    return subset.sample(min(len(subset), count)).reset_index(drop=True)

# ================= GENERATE SET =================
def generate_set():
    return {
        "MCQ": select_questions(filtered,"MCQ",20),
        "SHORT": select_questions(filtered,"SHORT",10),
        "3MARK": select_questions(filtered,"3MARK",5),
        "CASE": select_questions(filtered,"CASE",2),
        "LONG": select_questions(filtered,"LONG",3)
    }

# ================= PDF =================
def create_pdf(paper, set_name="A", answers=False):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    try:
        story.append(Image("logo.png", width=1.5*inch, height=1.5*inch))
    except:
        pass

    story.append(Paragraph(f"<b>GYANIN ACADEMY - SET {set_name}</b>", styles['Title']))
    story.append(Paragraph(f"Class {c} - {s}", styles['Normal']))
    story.append(Paragraph("Time: 3 Hours | Max Marks: 80", styles['Normal']))
    story.append(Spacer(1,10))

    sections = {
        "MCQ": "Section A (1×20)",
        "SHORT": "Section B (2×10)",
        "3MARK": "Section C (3×5)",
        "CASE": "Section D",
        "LONG": "Section E"
    }

    qnum = 1

    for key in paper:
        story.append(Spacer(1,10))
        story.append(Paragraph(f"<b>{sections[key]}</b>", styles['Heading3']))

        for row in paper[key].itertuples():
            story.append(Paragraph(f"Q{qnum}. {row.Question_Text}", styles['Normal']))

            if key == "MCQ":
                story.append(Paragraph(f"A. {row.Option_A}", styles['Normal']))
                story.append(Paragraph(f"B. {row.Option_B}", styles['Normal']))
                story.append(Paragraph(f"C. {row.Option_C}", styles['Normal']))
                story.append(Paragraph(f"D. {row.Option_D}", styles['Normal']))

            if answers:
                story.append(Paragraph(f"Answer: {row.Correct_Answer}", styles['Normal']))

            qnum += 1

    doc.build(story)
    buffer.seek(0)
    return buffer

# ================= BUTTON =================
num_sets = st.selectbox("Number of Sets", [1,2,3])

if st.button("Generate Papers"):

    for i in range(num_sets):
        set_name = chr(65+i)  # A, B, C
        paper = generate_set()

        pdf = create_pdf(paper, set_name, answers=False)
        ans_pdf = create_pdf(paper, set_name, answers=True)

        st.download_button(
            f"Download Set {set_name}",
            pdf,
            f"Paper_Set_{set_name}.pdf"
        )

        st.download_button(
            f"Download Answer Key {set_name}",
            ans_pdf,
            f"Answer_Set_{set_name}.pdf"
        )
