import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.platypus import *
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Gyanin ERP", layout="centered")

st.title("🏫 Gyanin Academy Question Paper Generator")

# ================= GOOGLE SHEET =================
sheet_id = "1Qy6io_C1oO9iqyGyhxvFywoskc_vIEXvb1s5z5hjcic"

question_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=QuestionBank"

@st.cache_data
def load_data():
    return pd.read_csv(question_url)

df = load_data()

# ================= FILTER =================
classes = sorted(df['Class'].astype(str).unique())
subjects = sorted(df['Subject'].unique())

selected_class = st.selectbox("Select Class", classes)
selected_subject = st.selectbox("Select Subject", subjects)

filtered_df = df[
    (df['Class'].astype(str) == selected_class) &
    (df['Subject'] == selected_subject)
]

# ================= PAPER GENERATION =================
def generate_paper():
    return {
        "Section A (MCQ)": filtered_df[filtered_df['Question_Type']=="MCQ"].head(5),
        "Section B (Short)": filtered_df[filtered_df['Question_Type']=="SHORT"].head(2),
        "Section C (3 Marks)": filtered_df[filtered_df['Question_Type']=="3MARK"].head(2),
        "Section D (Case Study)": filtered_df[filtered_df['Question_Type']=="CASE"].head(1),
        "Section E (Long)": filtered_df[filtered_df['Question_Type']=="LONG"].head(1)
    }

# ================= PDF =================
def create_pdf(paper):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Header
    story.append(Paragraph("<b>GYANIN ACADEMY</b>", styles['Title']))
    story.append(Paragraph("8/2 Mandeville Garden, Kolkata - 700006", styles['Normal']))
    story.append(Paragraph("Ph: 8334006669", styles['Normal']))
    story.append(Spacer(1,10))

    story.append(Paragraph("<b>CBSE Pattern Question Paper</b>", styles['Heading2']))
    story.append(Spacer(1,10))

    # Instructions
    story.append(Paragraph("<b>General Instructions:</b>", styles['Heading3']))
    instructions = [
        "All questions are compulsory.",
        "Use of calculator is not permitted.",
        "Marks are indicated against each question."
    ]

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

# ================= BUTTON =================
if st.button("Generate Paper"):

    paper = generate_paper()

    st.success("✅ Paper Generated")

    # Show preview
    for sec in paper:
        st.subheader(sec)
        for _,row in paper[sec].iterrows():
            st.write(row['Question_Text'])

    # PDF
    pdf = create_pdf(paper)

    st.download_button(
        "📥 Download PDF",
        pdf,
        "Gyanin_Paper.pdf"
    )
