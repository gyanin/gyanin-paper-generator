def login():
    st.sidebar.title("Login")

    username = st.sidebar.text_input("Username").strip()
    password = st.sidebar.text_input("Password", type="password").strip()

    if st.sidebar.button("Login"):

        users_df['Username'] = users_df['Username'].astype(str).str.strip()
        users_df['Password'] = users_df['Password'].astype(str).str.strip()

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
