import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from reportlab.platypus import *
from reportlab.lib.pagesizes import A4
from io import BytesIO

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

# ================= GOOGLE =================
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

sheet = client.open_by_key("1Qy6io_C1oO9iqyGyhxvFywoskc_vIEXvb1s5z5hjcic")
q_sheet = sheet.worksheet("QuestionBank")
r_sheet = sheet.worksheet("StudentResults")

df = pd.DataFrame(q_sheet.get_all_records())
results = pd.DataFrame(r_sheet.get_all_records())

st.title("🏫 Gyanin ERP System")

# ================= FILTER =================
classes = sorted(df['Class'].astype(str).unique())
subjects = sorted(df['Subject'].unique())

c = st.selectbox("Class", classes)
s = st.selectbox("Subject", subjects)

filtered = df[(df['Class'].astype(str)==c) & (df['Subject']==s)]

# ================= SAFE SAMPLE =================
def safe_sample(data, n):
    return data.sample(min(len(data), n)) if len(data)>0 else pd.DataFrame()

# ================= STUDENT TEST =================
if st.session_state["role"] == "student":

    st.header("🧑‍🎓 Test")

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

    if st.button("Submit"):
        score = sum(1 for c,a in answers if c==a)

        st.success(f"Score: {score}/{len(mcq)}")

        r_sheet.append_row([
            st.session_state["user"],
            c,
            s,
            score,
            len(mcq),
            datetime.now().strftime("%Y-%m-%d")
        ])

        st.success("Saved Successfully ✅")

# ================= ADMIN DASHBOARD =================
if st.session_state["role"] == "admin":

    st.header("📊 Admin Dashboard")

    if results.empty:
        st.warning("No results yet")
    else:
        st.dataframe(results)

        st.metric("Total Students", results['StudentName'].nunique())
        st.metric("Average Score", round(results['Score'].mean(),2))

        st.subheader("Subject Performance")
        st.write(results.groupby("Subject")["Score"].mean())

        st.subheader("Class Performance")
        st.write(results.groupby("Class")["Score"].mean())

    # ================= REPORT CARD =================
    st.header("📄 Generate Report Card")

    student_list = results['StudentName'].unique()
    selected_student = st.selectbox("Select Student", student_list)

    student_data = results[results['StudentName']==selected_student]

    def create_report():
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("<b>GYANIN ACADEMY REPORT CARD</b>", styles['Title']))
        story.append(Paragraph(f"Student: {selected_student}", styles['Normal']))
        story.append(Spacer(1,10))

        for _,row in student_data.iterrows():
            story.append(Paragraph(
                f"{row['Subject']} - Score: {row['Score']}/{row['Total']}",
                styles['Normal']
            ))

        doc.build(story)
        buffer.seek(0)
        return buffer

    if st.button("Generate Report Card"):
        pdf = create_report()

        st.download_button(
            "Download Report Card",
            pdf,
            f"{selected_student}_report.pdf"
        )
