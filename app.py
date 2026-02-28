import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Gyanin ERP", layout="centered")

# ================= LOGIN =================
USERS = {
    "student1": "1234",
    "student2": "1234",
    "admin": "admin123"
}

def login():
    st.sidebar.title("Login")

    user = st.sidebar.text_input("Username")
    pwd = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if user in USERS and USERS[user] == pwd:
            st.session_state["user"] = user
            st.session_state["logged_in"] = True
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

# ================= GOOGLE AUTH =================
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

sheet = client.open_by_key("1Qy6io_C1oO9iqyGyhxvFywoskc_vIEXvb1s5z5hjcic")

q_sheet = sheet.worksheet("QuestionBank")
r_sheet = sheet.worksheet("StudentResults")

df = pd.DataFrame(q_sheet.get_all_records())

# ================= FILTER =================
st.title("🏫 Gyanin ERP - Student Portal")

classes = sorted(df['Class'].astype(str).unique())
subjects = sorted(df['Subject'].unique())

c = st.selectbox("Class", classes)
s = st.selectbox("Subject", subjects)

filtered = df[(df['Class'].astype(str)==c) & (df['Subject']==s)]

# ================= SAFE SAMPLE =================
def safe_sample(data, n):
    if len(data) == 0:
        return pd.DataFrame()
    return data.sample(min(len(data), n))

# ================= TEST =================
st.header("🧑‍🎓 Test")

mcq = safe_sample(filtered[filtered['Question_Type']=="MCQ"], 5)

score = 0
answers = []

if mcq.empty:
    st.warning("No questions available")
else:
    for i,row in enumerate(mcq.itertuples(),1):
        st.write(f"Q{i}. {row.Question_Text}")

        ans = st.radio(
            f"Choose answer",
            [row.Option_A,row.Option_B,row.Option_C,row.Option_D],
            key=i
        )

        answers.append((row.Correct_Answer, ans))

# ================= SUBMIT =================
if st.button("Submit Test"):

    if mcq.empty:
        st.error("No questions available")
    else:
        score = sum(1 for c,a in answers if c==a)

        st.success(f"Score: {score}/{len(mcq)}")

        # AUTO SAVE TO SHEET
        r_sheet.append_row([
            st.session_state["user"],
            c,
            s,
            score,
            len(mcq),
            datetime.now().strftime("%Y-%m-%d")
        ])

        st.success("Result Saved Automatically ✅")
