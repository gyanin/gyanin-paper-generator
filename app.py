import streamlit as st
import pandas as pd
import random
from datetime import datetime

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

st.title("🏫 Gyanin ERP - Student System")

# ================= FILTER =================
classes = sorted(df['Class'].astype(str).unique())
subjects = sorted(df['Subject'].unique())

c = st.selectbox("Class", classes)
s = st.selectbox("Subject", subjects)

filtered = df[(df['Class'].astype(str)==c) & (df['Subject']==s)]

# ================= STUDENT INFO =================
student_name = st.text_input("Enter Student Name")

# ================= TEST =================
st.header("🧑‍🎓 Practice Test")

mcq = filtered[filtered['Question_Type']=="MCQ"].sample(5)

score = 0
answers = []

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

    for correct, given in answers:
        if correct == given:
            score += 1

    st.success(f"Score: {score}/5")

    # SAVE RESULT (display only)
    new_row = {
        "StudentName": student_name,
        "Class": c,
        "Subject": s,
        "Score": score,
        "Total": 5,
        "Date": datetime.now().strftime("%Y-%m-%d")
    }

    st.write("Result Saved (copy to sheet):")
    st.code(f"{student_name}\t{c}\t{s}\t{score}\t5\t{new_row['Date']}")

# ================= ANALYTICS =================
st.header("📊 Student Analytics")

if not results.empty:

    st.subheader("All Results")
    st.dataframe(results)

    avg_score = results['Score'].mean()
    st.metric("Average Score", round(avg_score,2))

    st.subheader("Performance by Subject")
    st.write(results.groupby("Subject")["Score"].mean())

# ================= DIFFICULTY TRACK =================
st.header("🧠 Difficulty Tracking")

diff_stats = df.groupby("Difficulty").size()
st.bar_chart(diff_stats)
