import streamlit as st
import pandas as pd


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Automatic Dashboard",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# PROFESSIONAL DASHBOARD STYLE
# =========================================================

st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 17px;
    color: #9ca3af;
    margin-bottom: 25px;
}

.section-title {
    font-size: 28px;
    font-weight: 650;
    margin-top: 20px;
}

.kpi-card {
    background: linear-gradient(135deg, #111827, #1f2937);
    border: 1px solid #374151;
    border-radius: 14px;
    padding: 20px;
    min-height: 105px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.18);
    margin-bottom: 10px;
}

.kpi-label {
    color: #9ca3af;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 7px;
}

.kpi-value {
    color: #f9fafb;
    font-size: 28px;
    font-weight: 700;
    line-height: 1.2;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# TITLE
# =========================================================

st.markdown(
    '<div class="main-title">🤖 Automatic Dashboard Generator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Upload your data and let AI automatically analyze, visualize, and generate business insights.</div>',
    unsafe_allow_html=True
)


# =========================================================
# FILE UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "📁 Upload your Excel or CSV file",
    type=["xlsx", "csv"]
)

if uploaded_file is None:
    st.info(
        "👆 Please upload an Excel or CSV file to generate your dashboard."
    )
    st.stop()


# =========================================================
# READ FILE
# =========================================================

try:

    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

except Exception as e:

    st.error(f"❌ Could not read the file: {e}")
    st.stop()


# =========================================================
# CHECK DATA
# =========================================================

if df.empty:

    st.warning("⚠️ The uploaded file contains no data.")
    st.stop()


# =========================================================
# DATA CLEANING
# =========================================================

# Clean Region
if "Region" in df.columns:

    df["Region"] = (
        df["Region"]
        .astype(str)
        .str.strip()
        .str.title()
    )


# Clean Category
if "Category" in df.columns:

    df["Category"] = (
        df["Category"]
        .astype(str)
        .str.strip()
        .str.title()
    )


# Clean Product
if "Product" in df.columns:

    df["Product"] = (
        df["Product"]
        .astype(str)
        .str.strip()
    )


# Remove invalid quantities
invalid_quantity_count = 0

if "Quantity" in df.columns:

    # Make sure Quantity is numeric
    df["Quantity"] = pd.to_numeric(
        df["Quantity"],
        errors="coerce"
    )

    invalid_quantity_count = int(
        (df["Quantity"] < 0).sum()
    )

    df = df[
        (df["Quantity"] >= 0) |
        (df["Quantity"].isna())
    ].copy()


# =========================================================
# COLUMN INTELLIGENCE
# =========================================================

date_columns = []
category_columns = []
measure_columns = []
id_columns = []


for column in df.columns:

    # DATE
    if pd.api.types.is_datetime64_any_dtype(df[column]):

        date_columns.append(column)

    # Try to detect date columns stored as text
    elif "date" in column.lower():

        converted_dates = pd.to_datetime(
            df[column],
            errors="coerce"
        )

        if converted_dates.notna().sum() > 0:

            date_columns.append(column)

        else:

            category_columns.append(column)

    # NUMERIC
    elif pd.api.types.is_numeric_dtype(df[column]):

        # ID detection
        if (
            "id" in column.lower()
            and df[column].nunique() == len(df)
        ):

            id_columns.append(column)

        else:

            measure_columns.append(column)

    # TEXT / CATEGORY
    else:

        category_columns.append(column)


# =========================================================
# INTERACTIVE FILTERS
# =========================================================

st.sidebar.header("🔎 Dashboard Filters")

filtered_df = df.copy()


# ---------------------------------------------------------
# REGION FILTER
# ---------------------------------------------------------

if "Region" in df.columns:

    regions = sorted(
        df["Region"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_regions = st.sidebar.multiselect(
        "🌍 Region",
        options=regions,
        default=regions,
        key="region_filter"
    )

    filtered_df = filtered_df[
        filtered_df["Region"].isin(selected_regions)
    ]


# ---------------------------------------------------------
# CATEGORY FILTER
# ---------------------------------------------------------

if "Category" in df.columns:

    categories = sorted(
        df["Category"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_categories = st.sidebar.multiselect(
        "📊 Category",
        options=categories,
        default=categories,
        key="category_filter"
    )

    filtered_df = filtered_df[
        filtered_df["Category"].isin(selected_categories)
    ]


# ---------------------------------------------------------
# PRODUCT FILTER
# ---------------------------------------------------------

if "Product" in df.columns:

    products = sorted(
        df["Product"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_products = st.sidebar.multiselect(
        "📦 Product",
        options=products,
        default=products,
        key="product_filter"
    )

    filtered_df = filtered_df[
        filtered_df["Product"].isin(selected_products)
    ]


# =========================================================
# FILTERED DASHBOARD DATA
# =========================================================

dashboard_df = filtered_df.copy()


st.sidebar.divider()

st.sidebar.write(
    f"📌 **Showing {len(dashboard_df)} "
    f"of {len(df)} records**"
)


# Stop if filters produce no data
if dashboard_df.empty:

    st.warning(
        "⚠️ No records match the selected filters. "
        "Please select at least one filter value."
    )

    st.stop()


# =========================================================
# AUTOMATIC KPI ENGINE
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">📌 Key Performance Indicators</div>',
    unsafe_allow_html=True
)


def measure_priority(column):

    name = column.lower()

    important_words = [
        "sales",
        "revenue",
        "profit",
        "income",
        "amount",
        "value",
        "salary",
        "price"
    ]

    score = 0

    for word in important_words:

        if word in name:
            score += 2

    return score


sorted_measures = sorted(
    measure_columns,
    key=measure_priority,
    reverse=True
)


kpi_values = []


for column in sorted_measures[:4]:

    name = column.lower()

    # Additive measures
    if any(
        word in name
        for word in [
            "sales",
            "revenue",
            "profit",
            "income",
            "amount",
            "value",
            "quantity",
            "units",
            "count"
        ]
    ):

        value = dashboard_df[column].sum()

        label = f"Total {column}"

    # Non-additive measures
    else:

        value = dashboard_df[column].mean()

        label = f"Average {column}"

    kpi_values.append(
        {
            "label": label,
            "value": value
        }
    )


# Records
kpi_values.append(
    {
        "label": "Records",
        "value": len(dashboard_df)
    }
)


# Display maximum 4 KPI cards
display_kpis = kpi_values[:4]


if display_kpis:

    columns = st.columns(
        len(display_kpis)
    )

    for column, kpi in zip(
        columns,
        display_kpis
    ):

        with column:

            value = kpi["value"]

            if pd.isna(value):

                formatted_value = "N/A"

            elif isinstance(
                value,
                (int, float)
            ):

                if value >= 1000:

                    formatted_value = (
                        f"{value:,.0f}"
                    )

                else:

                    formatted_value = (
                        f"{value:,.2f}"
                    )

            else:

                formatted_value = str(value)

            st.markdown(
                f'''
                <div class="kpi-card">
                    <div class="kpi-label">{kpi["label"]}</div>
                    <div class="kpi-value">{formatted_value}</div>
                </div>
                ''',
                unsafe_allow_html=True
            )

else:

    st.info(
        "No numeric measures were detected."
    )


# =========================================================
# COLUMN INTELLIGENCE
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">🧠 Column Intelligence</div>',
    unsafe_allow_html=True
)


intelligence_data = []


for column in df.columns:

    if column in id_columns:

        detected_type = "ID"

    elif column in date_columns:

        detected_type = "DATE"

    elif column in measure_columns:

        detected_type = "MEASURE"

    elif column in category_columns:

        detected_type = "CATEGORY"

    else:

        detected_type = "UNKNOWN"

    intelligence_data.append(
        {
            "Column": column,
            "Detected Type": detected_type
        }
    )


intelligence_df = pd.DataFrame(
    intelligence_data
)


st.dataframe(
    intelligence_df,
    width="stretch",
    hide_index=True
)


# =========================================================
# CHART RECOMMENDER
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">🎯 Recommended Visualizations</div>',
    unsafe_allow_html=True
)


recommendations = []


def measure_score(column):

    name = column.lower()

    important_words = [
        "sales",
        "revenue",
        "profit",
        "income",
        "amount",
        "value"
    ]

    score = 0

    for word in important_words:

        if word in name:
            score += 2

    return score


# Find primary measure
if measure_columns:

    primary_measure = max(
        measure_columns,
        key=measure_score
    )

else:

    primary_measure = None


# ---------------------------------------------------------
# DATE + MEASURE
# ---------------------------------------------------------

if date_columns and primary_measure:

    recommendations.append(
        {
            "chart_type": "Line Chart",
            "title": f"{primary_measure} Trend",
            "dimension": date_columns[0],
            "measure": primary_measure,
            "reason": "A date column and measure were detected."
        }
    )


# ---------------------------------------------------------
# CATEGORY + MEASURE
# ---------------------------------------------------------

if primary_measure:

    for category in category_columns:

        unique_values = (
            dashboard_df[category]
            .nunique()
        )

        if unique_values <= 10:

            recommendations.append(
                {
                    "chart_type": "Bar Chart",
                    "title": (
                        f"{primary_measure} by "
                        f"{category}"
                    ),
                    "dimension": category,
                    "measure": primary_measure,
                    "reason": (
                        f"{category} has "
                        f"{unique_values} categories."
                    )
                }
            )

        else:

            recommendations.append(
                {
                    "chart_type": "Top-N Bar Chart",
                    "title": (
                        f"Top {category} by "
                        f"{primary_measure}"
                    ),
                    "dimension": category,
                    "measure": primary_measure,
                    "reason": (
                        f"{category} has "
                        f"{unique_values} unique values."
                    )
                }
            )


# Display recommendations
if recommendations:

    for number, recommendation in enumerate(
        recommendations,
        start=1
    ):

        st.write(
            f"**{number}. "
            f"{recommendation['chart_type']} — "
            f"{recommendation['title']}**"
        )

        st.caption(
            f"Reason: "
            f"{recommendation['reason']}"
        )

else:

    st.info(
        "No suitable visualizations were detected."
    )


# =========================================================
# AUTOMATIC CHART GENERATOR
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">📊 Automatically Generated Visualizations</div>',
    unsafe_allow_html=True
)


for recommendation in recommendations:

    chart_type = recommendation[
        "chart_type"
    ]

    title = recommendation[
        "title"
    ]

    dimension = recommendation[
        "dimension"
    ]

    measure = recommendation[
        "measure"
    ]


    st.write(
        f"### {title}"
    )


    # -----------------------------------------------------
    # LINE CHART
    # -----------------------------------------------------

    if chart_type == "Line Chart":

        chart_data = dashboard_df.copy()

        if dimension in chart_data.columns:

            chart_data[dimension] = pd.to_datetime(
                chart_data[dimension],
                errors="coerce"
            )

            chart_data = chart_data.dropna(
                subset=[dimension, measure]
            )

            chart_data = (
                chart_data
                .groupby(dimension)[measure]
                .sum()
                .reset_index()
                .sort_values(dimension)
            )

            if not chart_data.empty:

                st.line_chart(
                    chart_data,
                    x=dimension,
                    y=measure
                )


    # -----------------------------------------------------
    # BAR CHART
    # -----------------------------------------------------

    elif chart_type == "Bar Chart":

        chart_data = (
            dashboard_df
            .groupby(dimension)[measure]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        if not chart_data.empty:

            st.bar_chart(
                chart_data
            )


    # -----------------------------------------------------
    # TOP-N BAR CHART
    # -----------------------------------------------------

    elif chart_type == "Top-N Bar Chart":

        chart_data = (
            dashboard_df
            .groupby(dimension)[measure]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(10)
        )

        if not chart_data.empty:

            st.bar_chart(
                chart_data
            )

# =========================================================
# SALES VS PROFIT TREND
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">📈 Sales vs Profit Trend</div>',
    unsafe_allow_html=True
)

if (
    "Date" in dashboard_df.columns
    and "Sales" in dashboard_df.columns
    and "Profit" in dashboard_df.columns
):

    trend_df = dashboard_df.copy()

    # Convert Date column
    trend_df["Date"] = pd.to_datetime(
        trend_df["Date"],
        errors="coerce"
    )

    # Convert Sales and Profit to numeric
    trend_df["Sales"] = pd.to_numeric(
        trend_df["Sales"],
        errors="coerce"
    )

    trend_df["Profit"] = pd.to_numeric(
        trend_df["Profit"],
        errors="coerce"
    )

    # Remove invalid rows
    trend_df = trend_df.dropna(
        subset=["Date", "Sales", "Profit"]
    )

    if not trend_df.empty:

        # Group by date
        trend_df = (
            trend_df
            .groupby("Date", as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
            .sort_values("Date")
        )

        # Set Date as index for Streamlit chart
        trend_chart = trend_df.set_index("Date")

        st.line_chart(
            trend_chart[
                ["Sales", "Profit"]
            ],
            width="stretch"
        )

    else:

        st.info(
            "Not enough valid date, sales, and profit data "
            "to create this chart."
        )

else:

    st.info(
        "Date, Sales, and Profit columns are required "
        "for this analysis."
    )


# =========================================================
# TOP & BOTTOM PERFORMERS
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">🏆 Top & Bottom Performers</div>',
    unsafe_allow_html=True
)


if (
    "Product" in dashboard_df.columns
    and "Sales" in dashboard_df.columns
):

    product_performance = (
        dashboard_df
        .groupby("Product")["Sales"]
        .sum()
        .sort_values(
            ascending=False
        )
    )


    if not product_performance.empty:

        # TOP 5
        st.write(
            "### 🥇 Top 5 Products"
        )

        top_5 = product_performance.head(5)

        st.bar_chart(top_5)


        # BOTTOM 5
        st.write(
            "### 📉 Bottom 5 Products"
        )

        bottom_5 = (
            product_performance
            .tail(5)
            .sort_values()
        )

        st.bar_chart(bottom_5)

else:

    st.info(
        "Top & Bottom Performers could "
        "not be generated because Product "
        "or Sales columns were not detected."
    )


# =========================================================
# DATA QUALITY
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">🔍 Data Quality</div>',
    unsafe_allow_html=True
)


missing_values = (
    df.isna()
    .sum()
    .sum()
)


col1, col2 = st.columns(2)


with col1:

    if missing_values > 0:

        st.warning(
            f"⚠️ Dataset contains "
            f"{missing_values} "
            f"missing value(s)."
        )

    else:

        st.success(
            "✅ No missing values detected."
        )


with col2:

    if invalid_quantity_count > 0:

        st.success(
            f"✅ Removed "
            f"{invalid_quantity_count} "
            f"invalid quantity record(s)."
        )

    else:

        st.success(
            "✅ No invalid quantities found."
        )


# =========================================================
# AUTOMATIC INSIGHTS
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">🤖 Automatic Insights</div>',
    unsafe_allow_html=True
)


insights = []


# ---------------------------------------------------------
# TOP PRODUCT
# ---------------------------------------------------------

if (
    "Product" in dashboard_df.columns
    and "Sales" in dashboard_df.columns
):

    product_sales = (
        dashboard_df
        .groupby("Product")["Sales"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    if not product_sales.empty:

        top_product = product_sales.index[0]

        top_product_sales = product_sales.iloc[0]

        insights.append(
            f"🏆 **{top_product}** is the "
            f"top-selling product with sales "
            f"of ₹{top_product_sales:,.0f}."
        )


# ---------------------------------------------------------
# TOP REGION
# ---------------------------------------------------------

if (
    "Region" in dashboard_df.columns
    and "Sales" in dashboard_df.columns
):

    region_sales = (
        dashboard_df
        .groupby("Region")["Sales"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    if not region_sales.empty:

        top_region = region_sales.index[0]

        top_region_sales = region_sales.iloc[0]

        insights.append(
            f"🌍 **{top_region}** is the "
            f"strongest region with sales "
            f"of ₹{top_region_sales:,.0f}."
        )


# ---------------------------------------------------------
# TOP CATEGORY
# ---------------------------------------------------------

if (
    "Category" in dashboard_df.columns
    and "Sales" in dashboard_df.columns
):

    category_sales = (
        dashboard_df
        .groupby("Category")["Sales"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    if not category_sales.empty:

        top_category = category_sales.index[0]

        top_category_sales = category_sales.iloc[0]

        insights.append(
            f"📊 **{top_category}** is the "
            f"highest-performing category "
            f"with sales of "
            f"₹{top_category_sales:,.0f}."
        )


# ---------------------------------------------------------
# FILTERED DATA QUALITY
# ---------------------------------------------------------

filtered_missing_values = (
    dashboard_df.isna()
    .sum()
    .sum()
)


if filtered_missing_values > 0:

    insights.append(
        f"⚠️ The filtered data contains "
        f"**{filtered_missing_values} "
        f"missing value(s)** that should "
        f"be reviewed."
    )


# ---------------------------------------------------------
# DISPLAY INSIGHTS
# ---------------------------------------------------------

if insights:

    for insight in insights:

        st.info(insight)

else:

    st.info(
        "No automatic insights could be generated."
    )


# =========================================================
# ASK YOUR DATA
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">💬 Ask Your Data</div>',
    unsafe_allow_html=True
)

st.write(
    "Ask a question about the currently filtered data."
)


question = st.text_input(
    "Enter your question:",
    placeholder=(
        "Example: Which product has the highest sales?"
    ),
    key="ask_your_data"
)


if question:

    q = question.lower().strip()

    answered = False


    # -----------------------------------------------------
    # 1. HIGHEST SALES PRODUCT
    # -----------------------------------------------------

    if (
        "highest sales" in q
        and "product" in q
        and "profit" not in q
    ):

        if (
            "Product" in dashboard_df.columns
            and "Sales" in dashboard_df.columns
        ):

            result = (
                dashboard_df
                .groupby("Product")["Sales"]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            if not result.empty:

                product = result.index[0]
                sales = result.iloc[0]

                st.success(
                    f"🏆 **{product}** has the highest "
                    f"sales with **₹{sales:,.0f}**."
                )

                answered = True


    # -----------------------------------------------------
    # 2. LOWEST SALES PRODUCT
    # -----------------------------------------------------

    elif (
        "lowest sales" in q
        and "product" in q
        and "profit" not in q
    ):

        if (
            "Product" in dashboard_df.columns
            and "Sales" in dashboard_df.columns
        ):

            result = (
                dashboard_df
                .groupby("Product")["Sales"]
                .sum()
                .sort_values()
            )

            if not result.empty:

                product = result.index[0]
                sales = result.iloc[0]

                st.success(
                    f"📉 **{product}** has the lowest "
                    f"sales with **₹{sales:,.0f}**."
                )

                answered = True


    # -----------------------------------------------------
    # 3. HIGHEST SALES REGION
    # -----------------------------------------------------

    elif (
        "highest sales" in q
        and "region" in q
    ):

        if (
            "Region" in dashboard_df.columns
            and "Sales" in dashboard_df.columns
        ):

            result = (
                dashboard_df
                .groupby("Region")["Sales"]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            if not result.empty:

                region = result.index[0]
                sales = result.iloc[0]

                st.success(
                    f"🌍 **{region}** has the highest "
                    f"sales with **₹{sales:,.0f}**."
                )

                answered = True


    # -----------------------------------------------------
    # 4. HIGHEST SALES CATEGORY
    # -----------------------------------------------------

    elif (
        "highest sales" in q
        and "categor" in q
    ):

        if (
            "Category" in dashboard_df.columns
            and "Sales" in dashboard_df.columns
        ):

            result = (
                dashboard_df
                .groupby("Category")["Sales"]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            if not result.empty:

                category = result.index[0]
                sales = result.iloc[0]

                st.success(
                    f"📊 **{category}** has the highest "
                    f"sales with **₹{sales:,.0f}**."
                )

                answered = True


    # -----------------------------------------------------
    # 5. HIGHEST PROFIT PRODUCT
    # -----------------------------------------------------

    elif (
        "highest profit" in q
        and "product" in q
    ):

        if (
            "Product" in dashboard_df.columns
            and "Profit" in dashboard_df.columns
        ):

            result = (
                dashboard_df
                .groupby("Product")["Profit"]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            if not result.empty:

                product = result.index[0]
                profit = result.iloc[0]

                st.success(
                    f"💰 **{product}** has the highest "
                    f"profit with **₹{profit:,.0f}**."
                )

                answered = True


    # -----------------------------------------------------
    # 6. TOTAL SALES
    # -----------------------------------------------------

    elif (
        "total sales" in q
        or q == "sales"
    ):

        if "Sales" in dashboard_df.columns:

            total_sales = dashboard_df["Sales"].sum()

            st.success(
                f"💵 Total sales are "
                f"**₹{total_sales:,.0f}**."
            )

            answered = True


    # -----------------------------------------------------
    # 7. TOTAL PROFIT
    # -----------------------------------------------------

    elif "total profit" in q:

        if "Profit" in dashboard_df.columns:

            total_profit = dashboard_df["Profit"].sum()

            st.success(
                f"💰 Total profit is "
                f"**₹{total_profit:,.0f}**."
            )

            answered = True


    # -----------------------------------------------------
    # 8. TOTAL QUANTITY
    # -----------------------------------------------------

    elif (
        "total quantity" in q
        or "total units" in q
    ):

        if "Quantity" in dashboard_df.columns:

            total_quantity = (
                dashboard_df["Quantity"].sum()
            )

            st.success(
                f"📦 Total quantity sold is "
                f"**{total_quantity:,.0f}**."
            )

            answered = True


    # -----------------------------------------------------
    # 9. AVERAGE SALES
    # -----------------------------------------------------

    elif "average sales" in q:

        if "Sales" in dashboard_df.columns:

            average_sales = (
                dashboard_df["Sales"].mean()
            )

            st.success(
                f"📈 Average sales per record are "
                f"**₹{average_sales:,.2f}**."
            )

            answered = True


    # -----------------------------------------------------
    # 10. SALES CONTRIBUTION BY CATEGORY
    # -----------------------------------------------------

    elif (
        "percentage" in q
        and "sales" in q
        and "categor" in q
    ):

        if (
            "Category" in dashboard_df.columns
            and "Sales" in dashboard_df.columns
        ):

            contribution = (
                dashboard_df
                .groupby("Category")["Sales"]
                .sum()
                .reset_index()
            )

            total_sales = contribution["Sales"].sum()

            if total_sales > 0:

                contribution["Percentage"] = (
                    contribution["Sales"]
                    / total_sales
                    * 100
                )

                contribution = contribution.sort_values(
                    "Percentage",
                    ascending=False
                )

                st.write(
                    "### 📊 Sales Contribution by Category"
                )

                st.dataframe(
                    contribution,
                    width="stretch",
                    hide_index=True
                )

                answered = True


    # -----------------------------------------------------
    # 11. SALES CONTRIBUTION BY REGION
    # -----------------------------------------------------

    elif (
        "percentage" in q
        and "sales" in q
        and "region" in q
    ):

        if (
            "Region" in dashboard_df.columns
            and "Sales" in dashboard_df.columns
        ):

            contribution = (
                dashboard_df
                .groupby("Region")["Sales"]
                .sum()
                .reset_index()
            )

            total_sales = contribution["Sales"].sum()

            if total_sales > 0:

                contribution["Percentage"] = (
                    contribution["Sales"]
                    / total_sales
                    * 100
                )

                contribution = contribution.sort_values(
                    "Percentage",
                    ascending=False
                )

                st.write(
                    "### 🌍 Sales Contribution by Region"
                )

                st.dataframe(
                    contribution,
                    width="stretch",
                    hide_index=True
                )

                answered = True


    # -----------------------------------------------------
    # UNKNOWN QUESTION
    # -----------------------------------------------------

    if not answered:

        st.warning(
            "🤔 I don't understand that question yet."
        )

        st.write("Try questions such as:")

        st.write(
            "• Which product has the highest sales?"
        )

        st.write(
            "• Which product has the lowest sales?"
        )

        st.write(
            "• Which region has the highest sales?"
        )

        st.write(
            "• Which category has the highest sales?"
        )

        st.write(
            "• Which product has the highest profit?"
        )

        st.write(
            "• What is the total sales?"
        )

        st.write(
            "• What is the total profit?"
        )

        st.write(
            "• What is the total quantity?"
        )

        st.write(
            "• What is the average sales?"
        )

        st.write(
            "• What percentage of sales comes from each category?"
        )


# =========================================================
# PROFIT MARGIN ANALYSIS
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">💰 Profit Margin Analysis</div>',
    unsafe_allow_html=True
)


if (
    "Sales" in dashboard_df.columns
    and "Profit" in dashboard_df.columns
):

    total_sales = dashboard_df["Sales"].sum()

    total_profit = dashboard_df["Profit"].sum()


    if total_sales > 0:

        profit_margin = (
            total_profit
            / total_sales
            * 100
        )

    else:

        profit_margin = 0


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Total Sales",
            f"₹{total_sales:,.0f}"
        )


    with col2:

        st.metric(
            "Total Profit",
            f"₹{total_profit:,.0f}"
        )


    with col3:

        st.metric(
            "Profit Margin",
            f"{profit_margin:.2f}%"
        )

else:

    st.warning(
        "Sales and Profit columns are required "
        "for Profit Margin Analysis."
    )


# =========================================================
# PROFIT PERFORMANCE BY PRODUCT
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">🏆 Product Profit Performance</div>',
    unsafe_allow_html=True
)


if (
    "Product" in dashboard_df.columns
    and "Profit" in dashboard_df.columns
):

    product_profit = (
        dashboard_df
        .groupby("Product")["Profit"]
        .sum()
        .sort_values(
            ascending=False
        )
    )


    if len(product_profit) > 0:

        top_product = product_profit.index[0]
        top_profit = product_profit.iloc[0]

        bottom_product = product_profit.index[-1]
        bottom_profit = product_profit.iloc[-1]


        col1, col2 = st.columns(2)


        with col1:

            st.success(
                f"🏆 **{top_product}** is the most "
                f"profitable product with profit "
                f"of ₹{top_profit:,.0f}."
            )


        with col2:

            st.warning(
                f"⚠️ **{bottom_product}** has the "
                f"lowest profit with profit "
                f"of ₹{bottom_profit:,.0f}."
            )

else:

    st.info(
        "Product and Profit columns are required "
        "for this analysis."
    )


# =========================================================
# PROFIT MARGIN BY PRODUCT
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">📊 Profit Margin by Product</div>',
    unsafe_allow_html=True
)


if (
    "Product" in dashboard_df.columns
    and "Sales" in dashboard_df.columns
    and "Profit" in dashboard_df.columns
):

    product_analysis = (
        dashboard_df
        .groupby("Product")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
        .reset_index()
    )


    product_analysis["Profit Margin %"] = 0.0


    product_analysis.loc[
        product_analysis["Sales"] != 0,
        "Profit Margin %"
    ] = (
        product_analysis.loc[
            product_analysis["Sales"] != 0,
            "Profit"
        ]
        /
        product_analysis.loc[
            product_analysis["Sales"] != 0,
            "Sales"
        ]
        * 100
    )


    product_analysis = product_analysis.sort_values(
        "Profit Margin %",
        ascending=False
    )


    st.dataframe(
        product_analysis,
        width="stretch",
        hide_index=True
    )

else:

    st.info(
        "Product, Sales and Profit columns are required."
    )


# =========================================================
# SALES GROWTH ANALYSIS
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">📈 Sales Growth Analysis</div>',
    unsafe_allow_html=True
)


if (
    "Date" in dashboard_df.columns
    and "Sales" in dashboard_df.columns
):

    growth_data = dashboard_df.copy()


    growth_data["Date"] = pd.to_datetime(
        growth_data["Date"],
        errors="coerce"
    )


    growth_data = growth_data.dropna(
        subset=["Date", "Sales"]
    )


    if len(growth_data) >= 2:

        growth_data = growth_data.sort_values(
            "Date"
        )


        midpoint = len(growth_data) // 2


        previous_period = (
            growth_data.iloc[:midpoint]
        )

        current_period = (
            growth_data.iloc[midpoint:]
        )


        previous_sales = (
            previous_period["Sales"].sum()
        )

        current_sales = (
            current_period["Sales"].sum()
        )


        if previous_sales > 0:

            growth_percentage = (
                (
                    current_sales
                    - previous_sales
                )
                / previous_sales
            ) * 100


            col1, col2, col3 = st.columns(3)


            with col1:

                st.metric(
                    "Previous Period Sales",
                    f"₹{previous_sales:,.0f}"
                )


            with col2:

                st.metric(
                    "Current Period Sales",
                    f"₹{current_sales:,.0f}"
                )


            with col3:

                st.metric(
                    "Sales Growth",
                    f"{growth_percentage:.2f}%",
                    delta=f"{growth_percentage:.2f}%"
                )

        else:

            st.info(
                "Previous period sales are zero, "
                "so growth cannot be calculated."
            )

    else:

        st.info(
            "At least two valid dates are required "
            "for growth analysis."
        )

else:

    st.info(
        "Date and Sales columns are required "
        "for growth analysis."
    )


# =========================================================
# SMART ANOMALY DETECTION
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">🚨 Smart Anomaly Detection</div>',
    unsafe_allow_html=True
)


if "Sales" in dashboard_df.columns:

    sales_data = dashboard_df.copy()


    sales_data = sales_data.dropna(
        subset=["Sales"]
    )


    if len(sales_data) >= 4:

        Q1 = sales_data["Sales"].quantile(0.25)

        Q3 = sales_data["Sales"].quantile(0.75)


        IQR = Q3 - Q1


        lower_limit = Q1 - 1.5 * IQR

        upper_limit = Q3 + 1.5 * IQR


        anomalies = sales_data[
            (sales_data["Sales"] < lower_limit)
            |
            (sales_data["Sales"] > upper_limit)
        ].copy()


        if len(anomalies) > 0:

            st.warning(
                f"⚠️ {len(anomalies)} unusual "
                f"sales record(s) detected."
            )


            display_columns = []


            for column in [
                "Order_ID",
                "Date",
                "Product",
                "Category",
                "Region",
                "Sales",
                "Profit"
            ]:

                if column in anomalies.columns:

                    display_columns.append(
                        column
                    )


            if display_columns:

                st.dataframe(
                    anomalies[display_columns],
                    width="stretch",
                    hide_index=True
                )


            st.caption(
                f"Normal sales range: "
                f"₹{max(0, lower_limit):,.0f} "
                f"to ₹{upper_limit:,.0f}"
            )

        else:

            st.success(
                "✅ No unusual sales records "
                "were detected."
            )

    else:

        st.info(
            "At least 4 sales records are required "
            "for anomaly detection."
        )

else:

    st.info(
        "A Sales column is required "
        "for anomaly detection."
    )


# =========================================================
# CORRELATION ANALYSIS
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">🔗 Correlation Analysis</div>',
    unsafe_allow_html=True
)


correlation_columns = (
    dashboard_df
    .select_dtypes(include="number")
    .columns
    .tolist()
)


# Remove ID columns
correlation_columns = [
    column
    for column in correlation_columns
    if column not in id_columns
]


if len(correlation_columns) >= 2:

    correlation_matrix = (
        dashboard_df[
            correlation_columns
        ].corr()
    )


    st.write(
        "This analysis automatically identifies "
        "relationships between numeric measures."
    )


    st.dataframe(
        correlation_matrix.round(2),
        width="stretch"
    )


    # -----------------------------------------------------
    # FIND STRONGEST RELATIONSHIP
    # -----------------------------------------------------

    strongest_pair = None

    strongest_value = 0


    for i in range(
        len(correlation_columns)
    ):

        for j in range(
            i + 1,
            len(correlation_columns)
        ):

            column_1 = correlation_columns[i]

            column_2 = correlation_columns[j]


            value = correlation_matrix.loc[
                column_1,
                column_2
            ]


            if (
                pd.notna(value)
                and abs(value) > strongest_value
            ):

                strongest_value = abs(value)

                strongest_pair = (
                    column_1,
                    column_2,
                    value
                )


    if strongest_pair:

        column_1, column_2, value = (
            strongest_pair
        )


        if value >= 0.7:

            relationship = "strong positive"

        elif value >= 0.3:

            relationship = "moderate positive"

        elif value > -0.3:

            relationship = "weak"

        elif value > -0.7:

            relationship = "moderate negative"

        else:

            relationship = "strong negative"


        st.info(
            f"🔎 **Strongest relationship:** "
            f"{column_1} and {column_2} have a "
            f"**{relationship} correlation "
            f"({value:.2f})**."
        )

else:

    st.info(
        "Not enough numeric columns to perform "
        "correlation analysis."
    )
    # =========================================================
# SMART PERFORMANCE RANKING
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">🏅 Smart Performance Ranking</div>',
    unsafe_allow_html=True
)

if (
    "Product" in dashboard_df.columns
    and "Sales" in dashboard_df.columns
    and "Profit" in dashboard_df.columns
):

    performance = (
        dashboard_df
        .groupby("Product")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
        .reset_index()
    )

    # Calculate profit margin
    performance["Profit Margin %"] = 0.0

    performance.loc[
        performance["Sales"] != 0,
        "Profit Margin %"
    ] = (
        performance.loc[
            performance["Sales"] != 0,
            "Profit"
        ]
        /
        performance.loc[
            performance["Sales"] != 0,
            "Sales"
        ]
        * 100
    )

    # -----------------------------------------------------
    # NORMALIZE SALES
    # -----------------------------------------------------

    if performance["Sales"].max() > performance["Sales"].min():

        performance["Sales Score"] = (
            (
                performance["Sales"]
                - performance["Sales"].min()
            )
            /
            (
                performance["Sales"].max()
                - performance["Sales"].min()
            )
            * 100
        )

    else:

        performance["Sales Score"] = 100


    # -----------------------------------------------------
    # NORMALIZE PROFIT
    # -----------------------------------------------------

    if performance["Profit"].max() > performance["Profit"].min():

        performance["Profit Score"] = (
            (
                performance["Profit"]
                - performance["Profit"].min()
            )
            /
            (
                performance["Profit"].max()
                - performance["Profit"].min()
            )
            * 100
        )

    else:

        performance["Profit Score"] = 100


    # -----------------------------------------------------
    # NORMALIZE PROFIT MARGIN
    # -----------------------------------------------------

    if (
        performance["Profit Margin %"].max()
        >
        performance["Profit Margin %"].min()
    ):

        performance["Margin Score"] = (
            (
                performance["Profit Margin %"]
                - performance["Profit Margin %"].min()
            )
            /
            (
                performance["Profit Margin %"].max()
                - performance["Profit Margin %"].min()
            )
            * 100
        )

    else:

        performance["Margin Score"] = 100


    # -----------------------------------------------------
    # FINAL PERFORMANCE SCORE
    # -----------------------------------------------------

    performance["Performance Score"] = (
        performance["Sales Score"] * 0.4
        +
        performance["Profit Score"] * 0.4
        +
        performance["Margin Score"] * 0.2
    )


    # -----------------------------------------------------
    # PERFORMANCE CATEGORY
    # -----------------------------------------------------

    def performance_label(score):

        if score >= 75:

            return "Excellent"

        elif score >= 50:

            return "Good"

        elif score >= 25:

            return "Average"

        else:

            return "Needs Attention"


    performance["Performance"] = (
        performance["Performance Score"]
        .apply(performance_label)
    )


    # -----------------------------------------------------
    # RANK PRODUCTS
    # -----------------------------------------------------

    performance = performance.sort_values(
        "Performance Score",
        ascending=False
    ).reset_index(drop=True)


    performance.insert(
        0,
        "Rank",
        range(1, len(performance) + 1)
    )


    # -----------------------------------------------------
    # DISPLAY RESULT
    # -----------------------------------------------------

    display_performance = performance[
        [
            "Rank",
            "Product",
            "Sales",
            "Profit",
            "Profit Margin %",
            "Performance Score",
            "Performance"
        ]
    ].copy()


    display_performance["Profit Margin %"] = (
        display_performance["Profit Margin %"]
        .round(2)
    )

    display_performance["Performance Score"] = (
        display_performance["Performance Score"]
        .round(2)
    )


    st.write(
        "Products are ranked using Sales, Profit, "
        "and Profit Margin."
    )


    st.dataframe(
        display_performance,
        width="stretch",
        hide_index=True
    )


    # -----------------------------------------------------
    # BEST PERFORMER
    # -----------------------------------------------------

    best_product = performance.iloc[0]

    st.success(
        f"🏆 **Best Overall Performer:** "
        f"{best_product['Product']} "
        f"with a performance score of "
        f"**{best_product['Performance Score']:.2f}/100**."
    )


else:

    st.info(
        "Product, Sales and Profit columns are "
        "required for Smart Performance Ranking."
    )
    # =========================================================
# SALES FORECASTING
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">🔮 Sales Forecast</div>',
    unsafe_allow_html=True
)


if (
    "Date" in dashboard_df.columns
    and "Sales" in dashboard_df.columns
):

    forecast_data = dashboard_df.copy()

    # Convert Date to datetime
    forecast_data["Date"] = pd.to_datetime(
        forecast_data["Date"],
        errors="coerce"
    )

    # Remove invalid dates and missing sales
    forecast_data = forecast_data.dropna(
        subset=["Date", "Sales"]
    )

    if len(forecast_data) >= 4:

        # Group sales by date
        daily_sales = (
            forecast_data
            .groupby("Date")["Sales"]
            .sum()
            .reset_index()
            .sort_values("Date")
        )

        if len(daily_sales) >= 4:

            # Create numeric time index
            daily_sales["Time Index"] = range(
                len(daily_sales)
            )

            # Calculate linear trend
            slope, intercept = __import__(
                "numpy"
            ).polyfit(
                daily_sales["Time Index"],
                daily_sales["Sales"],
                1
            )

            # Number of future periods
            forecast_periods = 5

            future_index = range(
                len(daily_sales),
                len(daily_sales) + forecast_periods
            )

            future_sales = (
                slope * __import__("numpy").array(
                    list(future_index)
                )
                + intercept
            )

            # Make sure forecast doesn't become negative
            future_sales = __import__(
                "numpy"
            ).maximum(
                future_sales,
                0
            )

            # Create future dates
            last_date = daily_sales["Date"].max()

            future_dates = pd.date_range(
                start=last_date + pd.Timedelta(days=1),
                periods=forecast_periods,
                freq="D"
            )

            forecast_df = pd.DataFrame(
                {
                    "Date": future_dates,
                    "Forecast Sales": future_sales
                }
            )

            # -------------------------------------------------
            # HISTORICAL + FORECAST DATA
            # -------------------------------------------------

            historical_chart = daily_sales[
                ["Date", "Sales"]
            ].copy()

            historical_chart = (
                historical_chart
                .rename(
                    columns={
                        "Sales": "Historical Sales"
                    }
                )
            )

            historical_chart["Forecast Sales"] = float("nan")


            forecast_chart = forecast_df.copy()

            forecast_chart["Historical Sales"] = float("nan")


            combined_forecast = pd.concat(
                [
                    historical_chart[
                        [
                            "Date",
                            "Historical Sales",
                            "Forecast Sales"
                        ]
                    ],
                    forecast_chart[
                        [
                            "Date",
                            "Historical Sales",
                            "Forecast Sales"
                        ]
                    ]
                ],
                ignore_index=True
            )


            # -------------------------------------------------
            # FORECAST CHART
            # -------------------------------------------------

            st.line_chart(
                combined_forecast,
                x="Date",
                y=[
                    "Historical Sales",
                    "Forecast Sales"
                ]
            )


            # -------------------------------------------------
            # FORECAST TABLE
            # -------------------------------------------------

            st.write("### 📅 Forecasted Sales")

            forecast_display = forecast_df.copy()

            forecast_display["Forecast Sales"] = (
                forecast_display["Forecast Sales"]
                .round(2)
            )

            st.dataframe(
                forecast_display,
                width="stretch",
                hide_index=True
            )


            # -------------------------------------------------
            # FORECAST SUMMARY
            # -------------------------------------------------

            average_forecast = (
                forecast_df["Forecast Sales"].mean()
            )

            total_forecast = (
                forecast_df["Forecast Sales"].sum()
            )


            col1, col2 = st.columns(2)


            with col1:

                st.metric(
                    "Average Forecast Sales",
                    f"₹{average_forecast:,.0f}"
                )


            with col2:

                st.metric(
                    "Next 5 Days Forecast",
                    f"₹{total_forecast:,.0f}"
                )


            # -------------------------------------------------
            # TREND INTERPRETATION
            # -------------------------------------------------

            if slope > 0:

                st.success(
                    "📈 The historical sales trend is "
                    "increasing. Forecasted sales are "
                    "expected to continue increasing."
                )

            elif slope < 0:

                st.warning(
                    "📉 The historical sales trend is "
                    "decreasing. Forecasted sales are "
                    "expected to continue decreasing."
                )

            else:

                st.info(
                    "➡️ The historical sales trend is "
                    "relatively stable."
                )


        else:

            st.info(
                "At least 4 different dates are required "
                "for sales forecasting."
            )

    else:

        st.info(
            "At least 4 valid sales records are required "
            "for forecasting."
        )

else:

    st.info(
        "Date and Sales columns are required "
        "for sales forecasting."
    )