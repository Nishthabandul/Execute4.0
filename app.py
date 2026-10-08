import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Subscription Tracker",
    layout="wide"
)

st.title("📅 Subscription Tracker & Data Analytics Dashboard")


# ============================================================
# 2. INITIALIZE SESSION STATE
# ============================================================

if "subscriptions" not in st.session_state:
    st.session_state.subscriptions = []


# ============================================================
# 3. DATA INGESTION
# ============================================================

st.sidebar.header("📂 Data Input / Output")

uploaded_file = st.sidebar.file_uploader(
    "Upload Subscription CSV",
    type=["csv"]
)

if uploaded_file is not None:

    # Read raw data
    raw_df = pd.read_csv(uploaded_file)

    st.success("CSV uploaded successfully!")

    # Store raw records
    st.session_state.subscriptions = raw_df.to_dict("records")


# ============================================================
# 4. ADD NEW RECORD
# ============================================================

with st.form("Add Subscription"):

    name = st.text_input("Subscription Name")

    cost = st.number_input(
        "Monthly Cost (₹)",
        min_value=0.0,
        format="%.2f"
    )

    next_date = st.date_input(
        "Next Payment Date",
        min_value=datetime.today()
    )

    submitted = st.form_submit_button("Add Subscription")


if submitted:

    st.session_state.subscriptions.append({
        "Name": name,
        "Cost": cost,
        "Next Payment Date": next_date.strftime("%Y-%m-%d")
    })

    st.success(f"Added subscription: {name}")


# ============================================================
# 5. DATA PIPELINE
# ============================================================

if st.session_state.subscriptions:

    # --------------------------------------------------------
    # RAW DATA
    # --------------------------------------------------------

    raw_df = pd.DataFrame(st.session_state.subscriptions)

    st.subheader("🔵 Raw Data")

    st.dataframe(
        raw_df,
        use_container_width=True
    )


    # ========================================================
    # 6. DATA VALIDATION
    # ========================================================

    st.subheader("🔍 Data Quality Checks")

    df = raw_df.copy()

    quality_issues = []

    # Check required columns
    required_columns = [
        "Name",
        "Cost",
        "Next Payment Date"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:

        st.error(
            f"Missing required columns: {missing_columns}"
        )

        st.stop()


    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    missing_values = df[required_columns].isnull().sum()

    total_missing = missing_values.sum()


    # --------------------------------------------------------
    # Duplicate records
    # --------------------------------------------------------

    duplicate_count = df.duplicated().sum()


    # --------------------------------------------------------
    # Invalid cost values
    # --------------------------------------------------------

    df["Cost"] = pd.to_numeric(
        df["Cost"],
        errors="coerce"
    )

    invalid_costs = (
        df["Cost"].isnull().sum()
        +
        (df["Cost"] < 0).sum()
    )


    # --------------------------------------------------------
    # Invalid dates
    # --------------------------------------------------------

    df["Next Payment Date"] = pd.to_datetime(
        df["Next Payment Date"],
        errors="coerce"
    )

    invalid_dates = df["Next Payment Date"].isnull().sum()


    # Display quality metrics

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Missing Values",
        int(total_missing)
    )

    col2.metric(
        "Duplicate Rows",
        int(duplicate_count)
    )

    col3.metric(
        "Invalid Costs",
        int(invalid_costs)
    )

    col4.metric(
        "Invalid Dates",
        int(invalid_dates)
    )


    # ========================================================
    # 7. DATA CLEANING
    # ========================================================

    st.subheader("🧹 Cleaned Data")

    cleaned_df = df.copy()


    # Remove completely empty rows
    cleaned_df = cleaned_df.dropna(
        how="all"
    )


    # Remove duplicate rows
    cleaned_df = cleaned_df.drop_duplicates()


    # Clean subscription names
    cleaned_df["Name"] = (
        cleaned_df["Name"]
        .astype(str)
        .str.strip()
    )


    # Convert cost to numeric
    cleaned_df["Cost"] = pd.to_numeric(
        cleaned_df["Cost"],
        errors="coerce"
    )


    # Remove invalid costs
    cleaned_df = cleaned_df[
        cleaned_df["Cost"] >= 0
    ]


    # Convert dates
    cleaned_df["Next Payment Date"] = pd.to_datetime(
        cleaned_df["Next Payment Date"],
        errors="coerce"
    )


    # Remove rows with invalid dates
    cleaned_df = cleaned_df.dropna(
        subset=["Next Payment Date"]
    )


    # Remove rows without subscription name
    cleaned_df = cleaned_df[
        cleaned_df["Name"].str.len() > 0
    ]


    st.dataframe(
        cleaned_df,
        use_container_width=True
    )


    # ========================================================
    # 8. DATA TRANSFORMATION
    # ========================================================

    st.subheader("⚙️ Transformed Data")

    transformed_df = cleaned_df.copy()


    # --------------------------------------------------------
    # Extract useful date features
    # --------------------------------------------------------

    transformed_df["Payment Month"] = (
        transformed_df["Next Payment Date"]
        .dt.month_name()
    )

    transformed_df["Payment Month Number"] = (
        transformed_df["Next Payment Date"]
        .dt.month
    )


    # --------------------------------------------------------
    # Calculate percentage contribution
    # --------------------------------------------------------

    total_cost = transformed_df["Cost"].sum()

    if total_cost > 0:

        transformed_df["Spend %"] = (
            transformed_df["Cost"]
            / total_cost
            * 100
        )

    else:

        transformed_df["Spend %"] = 0


    # --------------------------------------------------------
    # Categorize subscriptions by cost
    # --------------------------------------------------------

    def categorize_cost(cost):

        if cost < 200:
            return "Low"

        elif cost < 1000:
            return "Medium"

        else:
            return "High"


    transformed_df["Cost Category"] = (
        transformed_df["Cost"]
        .apply(categorize_cost)
    )


    st.dataframe(
        transformed_df,
        use_container_width=True
    )


    # ========================================================
    # 9. DATA ANALYSIS
    # ========================================================

    st.subheader("📊 Data Analysis")


    total_subscriptions = len(
        transformed_df
    )

    total_monthly_cost = transformed_df[
        "Cost"
    ].sum()

    average_cost = transformed_df[
        "Cost"
    ].mean()

    highest_cost = transformed_df[
        "Cost"
    ].max()


    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Subscriptions",
        total_subscriptions
    )

    col2.metric(
        "Monthly Spending",
        f"₹{total_monthly_cost:,.2f}"
    )

    col3.metric(
        "Average Cost",
        f"₹{average_cost:,.2f}"
    )

    col4.metric(
        "Highest Cost",
        f"₹{highest_cost:,.2f}"
    )


    # ========================================================
    # 10. CATEGORY ANALYSIS
    # ========================================================

    category_summary = (
        transformed_df
        .groupby("Cost Category")["Cost"]
        .agg(
            ["count", "sum", "mean"]
        )
        .reset_index()
    )

    category_summary.columns = [
        "Category",
        "Number of Subscriptions",
        "Total Spending",
        "Average Spending"
    ]


    st.write("### Category-wise Analysis")

    st.dataframe(
        category_summary,
        use_container_width=True
    )


    # ========================================================
    # 11. VISUALIZATION
    # ========================================================

    st.subheader("📈 Spending Visualizations")


    # Pie chart
    fig1, ax1 = plt.subplots()

    ax1.pie(
        transformed_df["Cost"],
        labels=transformed_df["Name"],
        autopct="%1.1f%%",
        startangle=90
    )

    ax1.axis("equal")

    st.pyplot(fig1)


    # Bar chart
    fig2, ax2 = plt.subplots()

    ax2.bar(
        category_summary["Category"],
        category_summary["Total Spending"]
    )

    ax2.set_xlabel("Cost Category")
    ax2.set_ylabel("Total Spending (₹)")
    ax2.set_title("Spending by Category")

    st.pyplot(fig2)


    # ========================================================
    # 12. UPCOMING PAYMENT ANALYSIS
    # ========================================================

    st.subheader("⏰ Upcoming Payments")

    today = pd.Timestamp.today()

    upcoming = transformed_df[
        transformed_df["Next Payment Date"]
        <= today + timedelta(days=7)
    ]

    upcoming = upcoming[
        upcoming["Next Payment Date"] >= today
    ]


    if not upcoming.empty:

        st.warning(
            "⚠️ Payments due within the next 7 days"
        )

        st.dataframe(
            upcoming,
            use_container_width=True
        )

    else:

        st.success(
            "No payments due within the next 7 days."
        )


    # ========================================================
    # 13. HIGH-COST SUBSCRIPTION ANALYSIS
    # ========================================================

    st.subheader("💸 High-Cost Subscriptions")

    high_cost = transformed_df[
        transformed_df["Spend %"] > 30
    ]


    if not high_cost.empty:

        st.error(
            "Subscriptions contributing more than "
            "30% of total spending:"
        )

        st.dataframe(
            high_cost,
            use_container_width=True
        )

    else:

        st.success(
            "No subscription contributes more than "
            "30% of total spending."
        )


    # ========================================================
    # 14. DOWNLOAD CLEANED DATA
    # ========================================================

    st.sidebar.subheader("📥 Export")

    cleaned_csv = transformed_df.to_csv(
        index=False
    ).encode("utf-8")


    st.sidebar.download_button(
        "Download Processed Data",
        cleaned_csv,
        "processed_subscriptions.csv",
        "text/csv"
    )


else:

    st.info(
        "No subscriptions yet. "
        "Add one using the form or upload a CSV."
    )
