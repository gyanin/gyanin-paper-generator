import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Gyanin Academy", layout="centered")

st.title("📄 Gyanin Academy Paper Generator")

# LOAD DATA
df = pd.read_csv("questionbank.csv")

# FILTER OPTIONS
classes = sorted(df['Class'].unique())
subjects = sorted(df['Subject'].unique())

selected_class = st.selectbox("Select Class", classes)
selected_subject = st.selectbox("Select Subject", subjects)

df = df[(df['Class']==selected_class) & (df['Subject']==selected_subject)]

# QUESTION TYPE SELECTION
qtype = st.selectbox("Select Section", df['Question_Type'].unique())

difficulty = st.selectbox("Difficulty", ["Auto","Easy","Medium","Hard"])

count = st.slider("Number of Questions", 1, 20, 5)

def smart_select(df, total):
    easy = int(total*0.4)
    med = int(total*0.4)
    hard = total - easy - med

    return pd.concat([
        df[df['Difficulty']=='Easy'].head(easy),
        df[df['Difficulty']=='Medium'].head(med),
        df[df['Difficulty']=='Hard'].head(hard)
    ])

if st.button("Generate Paper"):

    filtered = df[df['Question_Type']==qtype]

    if difficulty != "Auto":
        filtered = filtered[filtered['Difficulty']==difficulty]
        sample = filtered.sample(min(count,len(filtered)))
    else:
        sample = smart_select(filtered, count)

    st.subheader("Generated Questions")

    for i, row in sample.iterrows():
        st.write(f"Q: {row['Question_Text']}")

        if row['Question_Type']=="MCQ":
            st.write(f"A. {row['Option_A']}")
            st.write(f"B. {row['Option_B']}")
            st.write(f"C. {row['Option_C']}")
            st.write(f"D. {row['Option_D']}")
