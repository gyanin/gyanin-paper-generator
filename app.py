import streamlit as st
import pandas as pd
from reportlab.platypus import *
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
# ===== LOGIN SYSTEM =====
def login(users_df):
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

st.set_page_config(page_title="Gyanin Academy", layout="centered")

st.title("📄 Gyanin Academy Question Paper Generator")
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login(users_df)
    st.stop()
else:
    logout()
# ===== GOOGLE SHEET CONNECTION =====
sheet_id = "1Qy6io_C1oO9iqyGyhxvFywoskc_vIEXvb1s5z5hjcic"
sheet_name = "QuestionBank"

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

@st.cache_data
def load_data():
    return pd.read_csv(url)

df = load_data()

# ===== FILTERS =====
classes = sorted(df['Class'].astype(str).unique())
subjects = sorted(df['Subject'].unique())

selected_class = st.selectbox("Select Class", classes)
selected_subject = st.selectbox("Select Subject", subjects)

filtered_df = df[
    (df['Class'].astype(str) == selected_class) &
    (df['Subject'] == selected_subject)
]

# ===== SMART SELECTION =====
def smart_select(df, total):
    easy = int(total*0.4)
    med = int(total*0.4)
    hard = total - easy - med

    return pd.concat([
        df[df['Difficulty']=='Easy'].head(easy),
        df[df['Difficulty']=='Medium'].head(med),
        df[df['Difficulty']=='Hard'].head(hard)
    ])

def generate_paper():
    return {
        "MCQ": smart_select(filtered_df[filtered_df['Question_Type']=="MCQ"], 5),
        "SHORT": smart_select(filtered_df[filtered_df['Question_Type']=="SHORT"], 2),
        "3MARK": smart_select(filtered_df[filtered_df['Question_Type']=="3MARK"], 2),
        "CASE": smart_select(filtered_df[filtered_df['Question_Type']=="CASE"], 1),
        "LONG": smart_select(filtered_df[filtered_df['Question_Type']=="LONG"], 1)
    }

# ===== PDF GENERATION =====
def create_pdf(paper):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>GYANIN ACADEMY</b>", styles['Title']))
    story.append(Paragraph("8/2 Mandeville Garden, Kolkata - 700006", styles['Normal']))
    story.append(Paragraph("Ph: 8334006669", styles['Normal']))
    story.append(Spacer(1,10))

    story.append(Paragraph("<b>Class X - Question Paper</b>", styles['Heading2']))
    story.append(Paragraph("Time: 3 Hours | Maximum Marks: 80", styles['Normal']))
    story.append(Spacer(1,10))

    story.append(Paragraph("<b>General Instructions:</b>", styles['Heading3']))
    instructions = [
        "All questions are compulsory.",
        "Use of calculator is not permitted.",
        "Draw neat diagrams wherever required."
    ]

    for ins in instructions:
        story.append(Paragraph(f"- {ins}", styles['Normal']))

    for sec in paper:
        story.append(Spacer(1,10))
        story.append(Paragraph(f"<b>{sec}</b>", styles['Heading3']))

        for i,row in enumerate(paper[sec].itertuples(),1):
            story.append(Paragraph(f"Q{i}. {row.Question_Text}", styles['Normal']))

            if sec=="MCQ":
                story.append(Paragraph(f"A. {row.Option_A}", styles['Normal']))
                story.append(Paragraph(f"B. {row.Option_B}", styles['Normal']))
                story.append(Paragraph(f"C. {row.Option_C}", styles['Normal']))
                story.append(Paragraph(f"D. {row.Option_D}", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ===== BUTTON =====
if st.button("Generate Paper"):

    paper = generate_paper()

    st.success("Paper Generated!")

    pdf = create_pdf(paper)

    st.download_button(
        "Download PDF",
        pdf,
        "Gyanin_Paper.pdf"
    )
users_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Users"
users_df = pd.read_csv(users_url)
