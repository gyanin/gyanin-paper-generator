import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.platypus import *
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

st.set_page_config(page_title="Gyanin ERP", layout="centered")

# ================= LOGIN (SAFE METHOD) =================
USERS = {
    "admin": {"password": "1234", "role": "admin"},
    "teacher": {"password": "1234", "role": "teacher"}
}

def login():
    st.sidebar.title("🔐 Login")

    user = st.sidebar.text_input("Username")
    pwd = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if user in USERS and USERS[user]["password"] == pwd:
            st.session_state["logged_in"] = True
            st.session_state["role"] = USERS[user]["role"]
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
st.title("🏫 Gyanin Academy ERP")

classes = sorted(df['Class'].astype(str).unique())
subjects = sorted(df['Subject'].unique())

c = st.selectbox("Class", classes)
s = st.selectbox("Subject", subjects)

filtered = df[(df['Class'].astype(str)==c) & (df['Subject']==s)]

# ================= PAPER =================
def generate_paper():
    return {
        "Section A (1×20)": filtered[filtered['Question_Type']=="MCQ"].head(5),
        "Section B (2 Marks)": filtered[filtered['Question_Type']=="SHORT"].head(2),
        "Section C (3 Marks)": filtered[filtered['Question_Type']=="3MARK"].head(2),
        "Section D (Case Study)": filtered[filtered['Question_Type']=="CASE"].head(1),
        "Section E (Long Answer)": filtered[filtered['Question_Type']=="LONG"].head(1)
    }

# ================= PDF =================
def create_pdf(paper):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # LOGO
    try:
        story.append(Image("logo.png", width=1.5*inch, height=1.5*inch))
    except:
        pass

    # HEADER
    story.append(Paragraph("<b>GYANIN ACADEMY</b>", styles['Title']))
    story.append(Paragraph("8/2 Mandeville Garden, Kolkata - 700006", styles['Normal']))
    story.append(Paragraph("Ph: 8334006669", styles['Normal']))
    story.append(Spacer(1,10))

    story.append(Paragraph("<b>CBSE Pattern Question Paper</b>", styles['Heading2']))
    story.append(Paragraph("Time: 3 Hours     Maximum Marks: 80", styles['Normal']))

    story.append(Spacer(1,10))

    # Instructions
    story.append(Paragraph("<b>General Instructions:</b>", styles['Heading3']))
    ins = [
        "All questions are compulsory.",
        "Use of calculator is not permitted.",
        "Draw neat diagrams wherever required."
    ]
    for i in ins:
        story.append(Paragraph(f"- {i}", styles['Normal']))

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

# ================= ADMIN PANEL =================
if st.session_state["role"] == "admin":
    st.header("🛠 Admin Panel")

    st.info("Add questions directly in Google Sheet for now (safe mode)")

# ================= GENERATE =================
if st.button("Generate Paper"):
    paper = generate_paper()

    st.success("Paper Generated")

    pdf = create_pdf(paper)

    st.download_button("📥 Download PDF", pdf, "Gyanin_Paper.pdf")
