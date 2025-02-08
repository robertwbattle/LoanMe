import streamlit as st

def home_page():
    # Set the title of the page
    st.set_page_config(page_title="Loan Me", layout="wide")

    # Custom CSS for enhanced aesthetic appeal
    st.markdown("""
        <style>
            body {
                background-color: #f4f4f9;
                font-family: 'Arial', sans-serif;
            }
            h1 {
                color: #2c3e50;
                font-size: 56px;
                text-align: center;
                margin-bottom: 40px;
                font-weight: bold;
            }
            .button-container {
                display: flex;
                justify-content: center;
                gap: 40px;
                margin-top: 20px;
            }
            .button-container button {
                background-color: #4a90e2;
                color: white;
                padding: 20px 40px;
                border: none;
                border-radius: 12px;
                font-size: 20px;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                transition: background-color 0.3s, transform 0.2s;
            }
            .button-container button:hover {
                background-color: #357ab7;
                transform: scale(1.05);
            }
            .sign-in-button {
                background-color: #27ae60;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s, transform 0.2s;
                float: right;
                margin: 10px;
            }
            .sign-in-button:hover {
                background-color: #1e8449;
                transform: scale(1.05);
            }
        </style>
    """, unsafe_allow_html=True)

    # Top navigation bar with sign-in button
    st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
    if st.button("Sign In", key='sign_in', help="Click to sign in"):
        st.switch_page("app.py")  # Navigate to sign-in page
    st.markdown("</div>", unsafe_allow_html=True)

    # Centered title
    st.markdown("""
        <h1>Loan Me</h1>
    """, unsafe_allow_html=True)

    # Centered buttons side-by-side with enhanced styling
    st.markdown("<div class='button-container'>", unsafe_allow_html=True)
    if st.button("Lend", key='lend', help="Click to lend funds"):
        st.switch_page("lend.py")  # Navigate to Lend page
    if st.button("Borrow", key='borrow', help="Click to borrow funds"):
        st.switch_page("borrow.py")  # Navigate to Borrow page
    st.markdown("</div>", unsafe_allow_html=True)

# Run the home page function
if __name__ == "__main__":
    home_page()
