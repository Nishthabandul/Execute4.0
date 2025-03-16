import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(page_title="Subscription Tracker", layout="wide")

# Title
st.title("📅 Subscription Tracker App")

# Initialize session state for subscriptions
if "subscriptions" not in st.session_state:
    st.session_state.subscriptions = []

# Sidebar - Upload CSV
st.sidebar.header("📂 Upload / Download")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
if uploaded_file is not None:
    df_upload = pd.read_csv(uploaded_file)
    st.session_state.subscriptions = df_upload.to_dict('records')
    st.success("CSV uploaded successfully!")

# Sidebar - Download CSV
if st.session_state.subscriptions:
    df_download = pd.DataFrame(st.session_state.subscriptions)
    csv = df_download.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("Download CSV", csv, "subscriptions.csv", "text/csv")

# Sidebar - Dark mode
dark_mode = st.sidebar.checkbox("🌙 Dark Mode")
if dark_mode:
    st.markdown("""
        <style>
        body {background-color: #1e1e1e; color: white;}
        .stButton>button {background-color: #4CAF50; color: white;}
        </style>
    """, unsafe_allow_html=True)

# Input Form
with st.form("Add Subscription"):
    name = st.text_input("Subscription Name")
    cost = st.number_input("Monthly Cost (in ₹)", min_value=0.0, format="%.2f")
    next_date = st.date_input("Next Payment Date", min_value=datetime.today())
    submitted = st.form_submit_button("Add Subscription")

if submitted:
    st.session_state.subscriptions.append({
        "Name": name,
        "Cost": cost,
        "Next Payment Date": next_date.strftime("%Y-%m-%d")
    })
    st.success(f"Added subscription: {name}")

# Display Subscriptions
if st.session_state.subscriptions:
    df = pd.DataFrame(st.session_state.subscriptions)
    df["Next Payment Date"] = pd.to_datetime(df["Next Payment Date"])
    st.subheader("📋 Your Subscriptions")
    st.dataframe(df, use_container_width=True)

    # Monthly Cost Visualization
    st.subheader("📊 Monthly Cost Breakdown")
    fig, ax = plt.subplots()
    ax.pie(df["Cost"], labels=df["Name"], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

    # Upcoming Payments Alert (within 7 days)
    today = datetime.today()
    upcoming = df[df["Next Payment Date"] <= today + timedelta(days=7)]
    if not upcoming.empty:
        st.warning("⚠️ Upcoming Payments (within 7 days):")
        st.dataframe(upcoming, use_container_width=True)

    # High-Cost Subscription Alert (>30% of total cost)
    total_cost = df["Cost"].sum()
    high_cost = df[df["Cost"] > 0.3 * total_cost]
    if not high_cost.empty:
        st.error("💸 High-Cost Subscriptions (>30% of total spend):")
        st.dataframe(high_cost, use_container_width=True)
else:
    st.info("No subscriptions yet. Add one using the form above.")
