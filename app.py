import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from io import BytesIO
from reportlab.platypus import *
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Gyanin ERP", layout="wide")

# ===== GOOGLE AUTH =====
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

sheet = client.open_by_key("1Qy6io_C1oO9iqyGyhxvFywoskc_vIEXvb1s5z5hjcic")

question_sheet = sheet.worksheet("QuestionBank")
users_sheet = sheet.worksheet("Users")

df = pd.DataFrame(question_sheet.get_all_records())
users_df = pd.DataFrame(users_sheet.get_all_records())

# ===== LOGIN =====
def login():
    st.sidebar.title("Login")

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

st.title("🏫 Gyanin ERP System")

# ===== ADMIN PANEL =====
if st.session_state['role'] == "admin":

    st.subheader("Admin Panel")

    with st.expander("Add Question"):
        data = [
            st.text_input("Question ID"),
            st.text_input("Class"),
            st.text_input("Subject"),
            st.text_input("Chapter"),
            st.selectbox("Type", ["MCQ","SHORT","3MARK","CASE","LONG"]),
            st.selectbox("Difficulty", ["Easy","Medium","Hard"]),
            st.text_area("Question"),
            st.text_input("Option A"),
            st.text_input("Option B"),
            st.text_input("Option C"),
            st.text_input("Option D"),
            st.text_input("Answer"),
            st.text_input("Marks"),
            st.text_area("Solution"),
            0,
            ""
        ]

        if st.button("Save Question"):
            question_sheet.append_row(data)
            st.success("Saved!")

    st.subheader("Edit/Delete Questions")
    st.dataframe(df)

# ===== TEACHER PANEL =====
st.subheader("Generate Paper")

classes = sorted(df['Class'].astype(str).unique())
subjects = sorted(df['Subject'].unique())

c = st.selectbox("Class", classes)
s = st.selectbox("Subject", subjects)

filtered = df[(df['Class'].astype(str)==c) & (df['Subject']==s)]

if st.button("Generate"):
    st.write(filtered.head(10))

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>GYANIN ACADEMY</b>", styles['Title']))

    for i,row in enumerate(filtered.head(10).itertuples(),1):
        story.append(Paragraph(f"Q{i}. {row.Question_Text}", styles['Normal']))

    doc.build(story)
    buffer.seek(0)

    st.download_button("Download PDF", buffer, "paper.pdf")

# ===== STUDENT PANEL =====
st.subheader("Student Practice")

mcq = df[df['Question_Type']=="MCQ"].sample(5)

score = 0

for i,row in enumerate(mcq.itertuples(),1):
    st.write(row.Question_Text)

    ans = st.radio(f"Q{i}", [row.Option_A,row.Option_B,row.Option_C,row.Option_D], key=i)

    if ans == row.Correct_Answer:
        score += 1

if st.button("Submit Test"):
    st.success(f"Score: {score}/5")
