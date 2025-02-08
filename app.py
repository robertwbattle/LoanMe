import streamlit as st

def main():
    # Sidebar navigation
    st.sidebar.title('Navigation')
    page = st.sidebar.selectbox('Select a page:', ['Home', 'Page 1', 'Page 2', 'Page 3', 'Page 4'])

    if page == 'Home':
        show_home()
    elif page == 'Page 1':
        show_page_1()
    elif page == 'Page 2':
        show_page_2()
    elif page == 'Page 3':
        show_page_3()
    elif page == 'Page 4':
        show_page_4()

def show_home():
    st.title('LoanMe')
    col1, _, col2 = st.columns([1, 0.2, 1])

    # left side column: create account
    with col1:
        st.header('Create an Account')
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        if st.button('Sign Up'):
            st.success(f'Account created for {username}')

        st.markdown('<h3 style="color: #999999; font-size: 20px;">Login to Existing Account</h3>', unsafe_allow_html=True)
        login_username = st.text_input('Login Username', key='login_username')
        login_password = st.text_input('Login Password', type='password', key='login_password')
        if st.button('Login', key='login_button'):
            st.success(f'Logged in as {login_username}')

    # right side column: stats
    with col2:
        st.header('Simple Statistics')
        st.markdown("""
        <style>
        .stat-box {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .stat-title {
            font-size: 24px;
            font-weight: bold;
            color: #333333;
        }
        .stat-value {
            font-size: 20px;
            font-weight: bold;
            color: #007BFF;
        }
        .stat-description {
            font-size: 16px;
            color: #666666;
            text-align: left;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="stat-box"><div class="stat-title">Average Loan</div><div class="stat-value">$10,000</div><div class="stat-description">The average loan amount provided to our customers.</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-box"><div class="stat-title">Average APY</div><div class="stat-value">5%</div><div class="stat-description">The average annual percentage yield on loans.</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-box"><div class="stat-title">Average Loan Length</div><div class="stat-value">36 months</div><div class="stat-description">The average duration of loans provided.</div></div>', unsafe_allow_html=True)

def show_page_1():
    st.title('Page 1')
    st.write('This is Page 1.')

def show_page_2():
    st.title('Page 2')
    st.write('This is Page 2.')

def show_page_3():
    st.title('Page 3')
    st.write('This is Page 3.')

def show_page_4():
    st.title('Page 4')
    st.write('This is Page 4.')

if __name__ == "__main__":
    main()