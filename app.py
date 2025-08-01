import streamlit as st
import base64
import numpy as np
import pandas as pd
import joblib

# Function to add background image
def add_bg_from_local(image_file):
    with open(image_file, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded_string}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

add_bg_from_local("app_background.png")

# Load trained pipeline model
model = joblib.load("model.pkl")

# Set Streamlit page config
st.set_page_config(page_title="Credit Card Churn Prediction", layout="wide")

# Add custom CSS for bigger text and center alignment
st.markdown("""
    <style>
    .stSlider label, .stRadio label {
        font-size: 24px !important;
        font-weight: bold !important;
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8) !important;
    }
    .stButton > button {
        font-size: 20px !important;
        font-weight: bold !important;
        padding: 10px 20px !important;
        width: 100% !important;
        max-width: none !important;
    }
    .main .block-container {
        text-align: center;
        max-width: 800px;
        margin: 0 auto;
    }
    h1 {
        text-align: center !important;
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8) !important;
    }
    .stMarkdown {
        text-align: center !important;
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8) !important;
    }
    .stMarkdown h3:not([style*="color"]) {
        color: #FFD700 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8) !important;
    }
    .sidebar .sidebar-content {
        background-color: rgba(0,0,0,0.8);
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📊 Churn Prediction"],
    index=0 if "navigation" not in st.session_state else ["🏠 Home", "📊 Churn Prediction"].index(st.session_state.navigation),
    key="navigation"
)

def home_page():
    st.title("💳 Credit Card Churn Prediction System")
    st.markdown("---")
    
    st.markdown("### 👥 Who It's Made For:")
    st.markdown("""
    - **Financial Institutions:** Banks and credit card companies looking to reduce customer churn
    - **Business Analysts:** Professional business managers who need to identify churn risk in customers
    """)
    
    st.markdown("### 🔑 Key Features:")
    st.markdown("""
    -  Analyzes credit data to determine likelihood of account closure with confidence scores.
    -  Classifies customers into Low, Average, High, or Critical risk categories
    -  Provides recommendations based on risk level
    """)
    
    st.markdown("### 🚀 How to Use:")
    st.markdown("Navigate to the **'Churn Prediction'** page using the sidebar, enter the customer's information, and get instant risk assessment with detailed recommendations.")
    

    


def prediction_page():
    st.title("💳 Churn Prediction")
    st.markdown("Enter the customer details below to get a churn prediction:")
    
    # Input form
    months_on_book = st.slider("📘 How long has the customer had the account (months)?", 0, 60, 36)

    total_relationship = st.radio(
        "👥 Total number of products with the bank (e.g., cards, loans, etc.):", 
        options=[1, 2, 3, 4, 5, 6], 
        index=3
    )

    months_inactive = st.slider("😴 Months inactive in last 12 months:", 0, 12, 3)

    contacts_count = st.radio("📞 Contacts with customer service in last 12 months:", 
                              options=[0, 1, 2, 3, 4, 5, 6], index=2)

    # Credit balance information
    col1, col2 = st.columns(2)
    with col1:
        credit_limit = st.slider("💳 Credit limit ($):", 1000, 50000, 10000, step=100)
    with col2:
        current_balance = st.slider("💰 Current balance ($):", 0, 50000, 4000, step=100)
    
    # Spending comparison
    col1, col2 = st.columns(2)
    with col1:
        spending_this_quarter = st.slider("📈 Spending this quarter ($):", 0, 10000, 2000, step=50)
    with col2:
        spending_last_quarter = st.slider("📉 Spending last quarter ($):", 0, 10000, 1500, step=50)
    
    # Transaction comparison
    col1, col2 = st.columns(2)
    with col1:
        transactions_this_quarter = st.slider("🔁 Transactions this quarter:", 0, 100, 25, step=1)
    with col2:
        transactions_last_quarter = st.slider("📊 Transactions last quarter:", 0, 100, 20, step=1)

    # Calculate ratios from the new inputs
    revolving_bal = current_balance
    amt_chng_q4_q1 = spending_this_quarter / spending_last_quarter if spending_last_quarter > 0 else 1.0
    total_trans_ct = transactions_this_quarter + transactions_last_quarter
    ct_chng_q4_q1 = transactions_this_quarter / transactions_last_quarter if transactions_last_quarter > 0 else 1.0
    avg_util_ratio = current_balance / credit_limit if credit_limit > 0 else 0.0
    
    # Collect inputs into dictionary for DataFrame
    input_data = {
        'Months_on_book': [months_on_book],
        'Total_Relationship_Count': [total_relationship],
        'Months_Inactive_12_mon': [months_inactive],
        'Contacts_Count_12_mon': [contacts_count],
        'Total_Revolving_Bal': [revolving_bal],
        'Total_Amt_Chng_Q4_Q1': [amt_chng_q4_q1],
        'Total_Trans_Ct': [total_trans_ct],
        'Total_Ct_Chng_Q4_Q1': [ct_chng_q4_q1],
        'Avg_Utilization_Ratio': [avg_util_ratio]
    }

    # Convert to DataFrame
    input_df = pd.DataFrame(input_data)

    # Predict
    if st.button("🔮 Predict Churn"):
        prediction = model.predict(input_df)[0]
        prob = model.predict_proba(input_df)[0][1]
        
        # Display prediction result
        if prediction == 1:
            st.error(f"❌ Churn Likely (Confidence: {prob:.2f})")
        else:
            st.success(f"✅ Customer Likely to Stay (Confidence: {1 - prob:.2f})")
        
        # Display risk category and explanation
        st.markdown("📊 Risk Assessment")
        
        if prob < 0.2:
            risk_category = "Low Risk"
            risk_color = "green"
            risk_description = "This customer has a very low probability of churning. They are likely to remain loyal to your services."
        elif prob < 0.4:
            risk_category = "Average Risk"
            risk_color = "orange"
            risk_description = "This customer has a moderate risk of churning. Consider implementing retention strategies to improve their satisfaction."
        elif prob < 0.6:
            risk_category = "High Risk"
            risk_color = "yellow"
            risk_description = "This customer has a high risk of churning. Immediate intervention is recommended to prevent customer loss."
        else:
            risk_category = "Critical Risk"
            risk_color = "red"
            risk_description = "This customer has a critical risk of churning. Urgent action is required to retain this customer."
        
        st.markdown(f"""
        <div style='background-color: rgba(0,0,0,0.7); padding: 20px; border-radius: 10px; border-left: 5px solid {risk_color};'>
            <h3 style='color: {risk_color}; margin-bottom: 10px;'>Risk Category: {risk_category}</h3>
            <p style='color: white; font-size: 16px; line-height: 1.5;'>{risk_description}</p>
            <p style='color: white; font-size: 14px; margin-top: 10px;'><strong>Churn Probability:</strong> {prob:.1%}</p>
        </div>
        """, unsafe_allow_html=True)

# Page routing
if page == "🏠 Home":
    home_page()
elif page == "📊 Churn Prediction":
    prediction_page()
