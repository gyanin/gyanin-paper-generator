import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.platypus import *
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Gyanin ERP", layout="centered")

# ===== GOOGLE SHEET =====
sheet_id = "1Qy6io_C1oO9iqyGyhxvFywoskc_vIEXvb1s5z5hjcic"

qb_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=QuestionBank"
users_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Users"

df = pd.read_csv(qb_url)
users_df = pd.read_csv(users_url)

# ===== LOGIN =====
def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

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

# ===== SESSION =====
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login()
    st.stop()
else:
    logout()

# ===== MAIN UI =====
st.title("📄 Gyanin Academy ERP")

classes = sorted(df['Class'].astype(str).unique())
subjects = sorted(df['Subject'].unique())

selected_class = st.selectbox("Class", classes)
selected_subject = st.selectbox("Subject", subjects)

filtered_df = df[
    (df['Class'].astype(str) == selected_class) &
    (df['Subject'] == selected_subject)
]

# ===== PAPER GENERATION =====
def generate_paper():
    return {
        "MCQ": filtered_df[filtered_df['Question_Type']=="MCQ"].head(5),
        "SHORT": filtered_df[filtered_df['Question_Type']=="SHORT"].head(2),
        "3MARK": filtered_df[filtered_df['Question_Type']=="3MARK"].head(2),
    }

def create_pdf(paper):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>GYANIN ACADEMY</b>", styles['Title']))
    story.append(Paragraph("Kolkata", styles['Normal']))
    story.append(Spacer(1,10))

    for sec in paper:
        story.append(Paragraph(f"<b>{sec}</b>", styles['Heading2']))
        for i,row in enumerate(paper[sec].itertuples(),1):
            story.append(Paragraph(f"Q{i}. {row.Question_Text}", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

if st.button("Generate Paper"):
    paper = generate_paper()
    pdf = create_pdf(paper)

    st.download_button("Download PDF", pdf, "paper.pdf")
