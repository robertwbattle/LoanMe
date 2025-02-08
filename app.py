import streamlit as st

def main():
    st.title('LoanMe')
    col1, _, col2 = st.columns([1, 0.2, 1])

    # left side column: create account
    with col1:
        # new acc login
        st.header('Create an Account')
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        if st.button('Sign Up'):
            st.success(f'Account created for {username}')

        # existing account login
        st.markdown('<h3 style="color: #999999; font-size: 20px;">Login to Existing Account</h3>', unsafe_allow_html=True)
        login_username = st.text_input('Login Username', key='login_username')
        login_password = st.text_input('Login Password', type='password', key='login_password')
        if st.button('Login', key='login_button'):
            st.success(f'Logged in as {login_username}')

    # right side column: stats
    with col2:
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
        .dimmed-input input {
            background-color: #f0f0f0;
            color: #666666;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="stat-box"><div class="stat-title">Average Loan</div><div class="stat-value">$10,000</div><div class="stat-description">The average loan amount provided to our customers.</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-box"><div class="stat-title">Average APY</div><div class="stat-value">5%</div><div class="stat-description">The average annual percentage yield on loans.</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-box"><div class="stat-title">Average Loan Length</div><div class="stat-value">36 months</div><div class="stat-description">The average duration of loans provided.</div></div>', unsafe_allow_html=True)

        # Apply dimmed-input class to login fields
        st.markdown('<style>.dimmed-input input { background-color: #f0f0f0; color: #666666; }</style>', unsafe_allow_html=True)
        st.markdown('<div class="dimmed-input"></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()