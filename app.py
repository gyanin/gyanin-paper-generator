import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from reportlab.platypus import *
from reportlab.lib.pagesizes import A4

st.set_page_config(page_title="Gyanin ERP", layout="wide")

# ================= LOGIN =================
USERS = {
    "admin": {"password": "1234", "role": "admin"},
    "student1": {"password": "1234", "role": "student"}
}

def login():
    st.sidebar.title("Login")
    u = st.sidebar.text_input("Username")
    p = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if u in USERS and USERS[u]["password"] == p:
            st.session_state["logged_in"] = True
            st.session_state["user"] = u
            st.session_state["role"] = USERS[u]["role"]
        else:
            st.error("Invalid login")

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

# ================= LOAD QUESTION DATA =================
sheet_id = "1Qy6io_C1oO9iqyGyhxvFywoskc_vIEXvb1s5z5hjcic"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=QuestionBank"

@st.cache_data
def load_data():
    return pd.read_csv(url)

df = load_data()

# ================= SESSION STORAGE =================
if "results" not in st.session_state:
    st.session_state["results"] = pd.DataFrame(
        columns=["Student","Class","Subject","Score","Total","Date"]
    )

# ================= FILTER =================
st.title("🏫 Gyanin Academy ERP")

classes = sorted(df['Class'].astype(str).unique())
subjects = sorted(df['Subject'].unique())

c = st.selectbox("Class", classes)
s = st.selectbox("Subject", subjects)

filtered = df[(df['Class'].astype(str)==c) & (df['Subject']==s)]

# ================= SAFE SAMPLE =================
def safe_sample(data, n):
    return data.sample(min(len(data), n)) if len(data)>0 else pd.DataFrame()

# ================= STUDENT PANEL =================
if st.session_state["role"] == "student":

    st.header("🧑‍🎓 Student Test")

    mcq = safe_sample(filtered[filtered['Question_Type']=="MCQ"], 5)

    answers = []

    if mcq.empty:
        st.warning("No questions available")
    else:
        for i,row in enumerate(mcq.itertuples(),1):
            st.write(f"Q{i}. {row.Question_Text}")

            ans = st.radio(
                f"Answer Q{i}",
                [row.Option_A,row.Option_B,row.Option_C,row.Option_D],
                key=i
            )

            answers.append((row.Correct_Answer, ans))

    if st.button("Submit Test"):

        score = sum(1 for c,a in answers if c==a)

        st.success(f"Score: {score}/{len(mcq)}")

        new_row = {
            "Student": st.session_state["user"],
            "Class": c,
            "Subject": s,
            "Score": score,
            "Total": len(mcq),
            "Date": datetime.now().strftime("%Y-%m-%d")
        }

        st.session_state["results"] = pd.concat(
            [st.session_state["results"], pd.DataFrame([new_row])],
            ignore_index=True
        )

        st.success("Saved Successfully ✅")

# ================= ADMIN DASHBOARD =================
if st.session_state["role"] == "admin":

    st.header("📊 Admin Dashboard")

    results = st.session_state["results"]

    if results.empty:
        st.warning("No results yet")
    else:
        st.dataframe(results)

        st.metric("Total Students", results['Student'].nunique())
        st.metric("Average Score", round(results['Score'].mean(),2))

        st.subheader("Subject Performance")
        st.write(results.groupby("Subject")["Score"].mean())

        st.subheader("Class Performance")
        st.write(results.groupby("Class")["Score"].mean())

    # ================= DOWNLOAD =================
    st.header("⬇ Export Data")

    csv = results.to_csv(index=False).encode('utf-8')

    st.download_button(
        "Download Results CSV",
        csv,
        "results.csv",
        "text/csv"
    )

    # ================= REPORT CARD =================
    st.header("📄 Report Card")

    if not results.empty:
        student = st.selectbox("Select Student", results['Student'].unique())

        data = results[results['Student']==student]

        def create_pdf():
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []

            story.append(Paragraph("<b>GYANIN ACADEMY REPORT CARD</b>", getSampleStyleSheet()['Title']))
            story.append(Paragraph(f"Student: {student}", getSampleStyleSheet()['Normal']))

            for _,row in data.iterrows():
                story.append(Paragraph(
                    f"{row['Subject']} - {row['Score']}/{row['Total']}",
                    getSampleStyleSheet()['Normal']
                ))

            doc.build(story)
            buffer.seek(0)
            return buffer

        if st.button("Generate Report"):
            pdf = create_pdf()

            st.download_button(
                "Download Report Card",
                pdf,
                f"{student}_report.pdf"
            )
