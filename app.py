import streamlit as st
import pandas as pd
from reportlab.platypus import *
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

st.set_page_config(page_title="Gyanin Academy", layout="centered")

st.title("📄 Gyanin Academy Question Paper Generator")

# LOAD DATA
sheet_id = "1Qy6io_C1oO9iqyGyhxvFywoskc_vIEXvb1s5z5hjcicr"
sheet_name = "QuestionBank"

url = f"https://docs.google.com/spreadsheets/d/{Gyanin Question Generator}/gviz/tq?tqx=out:csv&sheet={1Qy6io_C1oO9iqyGyhxvFywoskc_vIEXvb1s5z5hjcic}"

@st.cache_data
def load_data():
    return pd.read_csv(url)

df = load_data()

# FILTERS
classes = sorted(df['Class'].unique())
subjects = sorted(df['Subject'].unique())

selected_class = st.selectbox("Select Class", classes)
selected_subject = st.selectbox("Select Subject", subjects)

filtered_df = df[(df['Class']==selected_class) & (df['Subject']==selected_subject)]

difficulty = st.selectbox("Difficulty", ["Auto","Easy","Medium","Hard"])

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
    paper = {
        "MCQ": smart_select(filtered_df[filtered_df['Question_Type']=="MCQ"], 5),
        "SHORT": smart_select(filtered_df[filtered_df['Question_Type']=="SHORT"], 2),
        "3MARK": smart_select(filtered_df[filtered_df['Question_Type']=="3MARK"], 2),
        "CASE": smart_select(filtered_df[filtered_df['Question_Type']=="CASE"], 1),
        "LONG": smart_select(filtered_df[filtered_df['Question_Type']=="LONG"], 1)
    }
    return paper

def create_pdf(paper, include_solution=False):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # HEADER
    story.append(Paragraph("<b>GYANIN ACADEMY</b>", styles['Title']))
    story.append(Paragraph("8/2 Mandeville Garden, Kolkata - 700006", styles['Normal']))
    story.append(Paragraph("Ph: 8334006669", styles['Normal']))
    story.append(Spacer(1,10))

    story.append(Paragraph(f"<b>Class {selected_class} - {selected_subject}</b>", styles['Heading2']))

    sections = ["MCQ","SHORT","3MARK","CASE","LONG"]

    for sec in sections:
        story.append(Spacer(1,10))
        story.append(Paragraph(f"<b>{sec}</b>", styles['Heading3']))

        for i, row in enumerate(paper[sec].itertuples(),1):
            story.append(Paragraph(f"Q{i}. {row.Question_Text}", styles['Normal']))

            if sec == "MCQ":
                story.append(Paragraph(f"A. {row.Option_A}", styles['Normal']))
                story.append(Paragraph(f"B. {row.Option_B}", styles['Normal']))
                story.append(Paragraph(f"C. {row.Option_C}", styles['Normal']))
                story.append(Paragraph(f"D. {row.Option_D}", styles['Normal']))

            if include_solution:
                story.append(Paragraph(f"Answer: {row.Correct_Answer}", styles['Normal']))
                story.append(Paragraph(f"Solution: {row.Solution}", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

# BUTTON
if st.button("Generate Full Paper"):

    paper = generate_paper()

    st.success("Paper Generated!")

    # DISPLAY QUESTIONS
    for sec in paper:
        st.subheader(sec)
        for _, row in paper[sec].iterrows():
            st.write(row['Question_Text'])

    # PDF DOWNLOAD
    pdf = create_pdf(paper, include_solution=False)
    st.download_button("Download Question Paper", pdf, "Gyanin_Paper.pdf")

    pdf_sol = create_pdf(paper, include_solution=True)
    st.download_button("Download With Solutions", pdf_sol, "Gyanin_Paper_Solutions.pdf")
