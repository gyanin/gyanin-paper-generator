import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gyanin ERP", layout="centered")

# ================= GOOGLE SHEET =================
sheet_id = "1Qy6io_C1oO9iqyGyhxvFywoskc_vIEXvb1s5z5hjcic"

q_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=QuestionBank"
r_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=StudentResults"

@st.cache_data
def load_data():
    df = pd.read_csv(q_url)
    try:
        results = pd.read_csv(r_url)
    except:
        results = pd.DataFrame(columns=["StudentName","Class","Subject","Score","Total","Date"])
    return df, results

df, results = load_data()

st.title("🏫 Gyanin ERP System")

# ================= FILTER =================
classes = sorted(df['Class'].astype(str).unique())
subjects = sorted(df['Subject'].unique())

c = st.selectbox("Select Class", classes)
s = st.selectbox("Select Subject", subjects)

filtered = df[(df['Class'].astype(str)==c) & (df['Subject']==s)]

# ================= SAFE SAMPLE FUNCTION =================
def safe_sample(data, n):
    if len(data) == 0:
        return pd.DataFrame()
    return data.sample(min(len(data), n))

# ================= STUDENT INFO =================
st.header("🧑‍🎓 Student Test")

student_name = st.text_input("Enter Student Name")

# ================= MCQ TEST =================
mcq_data = filtered[filtered['Question_Type']=="MCQ"]
mcq = safe_sample(mcq_data, 5)

score = 0
answers = []

if mcq.empty:
    st.warning("No MCQ questions available for this selection")
else:
    for i,row in enumerate(mcq.itertuples(),1):
        st.write(f"Q{i}. {row.Question_Text}")

        ans = st.radio(
            f"Choose answer for Q{i}",
            [row.Option_A,row.Option_B,row.Option_C,row.Option_D],
            key=i
        )

        answers.append((row.Correct_Answer, ans))

# ================= SUBMIT =================
if st.button("Submit Test"):

    if not student_name:
        st.error("Please enter student name")
    elif mcq.empty:
        st.error("No questions available")
    else:
        score = sum(1 for correct, given in answers if correct == given)

        st.success(f"Score: {score}/{len(mcq)}")

        # Show row to copy
        date = datetime.now().strftime("%Y-%m-%d")

        st.info("Copy this and paste into StudentResults sheet")
        st.code(f"{student_name}\t{c}\t{s}\t{score}\t{len(mcq)}\t{date}")

# ================= ANALYTICS =================
st.header("📊 Analytics")

if results.empty:
    st.warning("No results data available yet")
else:
    st.subheader("All Results")
    st.dataframe(results)

    # Average score
    avg = results['Score'].mean()
    st.metric("Average Score", round(avg,2))

    # Subject-wise
    st.subheader("Subject Performance")
    st.write(results.groupby("Subject")["Score"].mean())

    # Class-wise
    st.subheader("Class Performance")
    st.write(results.groupby("Class")["Score"].mean())

# ================= DIFFICULTY =================
st.header("🧠 Difficulty Distribution")

if 'Difficulty' in df.columns:
    st.bar_chart(df['Difficulty'].value_counts())
else:
    st.warning("No difficulty column found")
