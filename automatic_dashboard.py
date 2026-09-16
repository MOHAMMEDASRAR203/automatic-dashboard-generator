import pandas as pd

# ==========================================python -m streamlit run app.py
# 1. LOAD DATA
# ==========================================

df = pd.read_excel("sales_data.xlsx")

print("✅ Excel file loaded successfully!")

print("\nOriginal rows:", len(df))


# ==========================================
# 2. STANDARDIZE TEXT
# ==========================================

df["Region"] = df["Region"].str.strip().str.title()
df["Category"] = df["Category"].str.strip().str.title()

print("\n✅ Region and Category standardized")


# ==========================================
# 3. REMOVE INVALID QUANTITIES
# ==========================================

invalid_quantity = df[df["Quantity"] < 0]

print("\n--- INVALID QUANTITY ---")
print("Invalid rows found:", len(invalid_quantity))

# Keep only valid quantities
df = df[df["Quantity"] >= 0].copy()

print("Rows after removing invalid quantities:", len(df))


# ==========================================
# 4. CHECK MISSING VALUES
# ==========================================

print("\n--- MISSING VALUES ---")

missing_values = df.isnull().sum()

for column in missing_values.index:
    if missing_values[column] > 0:
        print(f"⚠️ {column}: {missing_values[column]} missing value(s)")


# ==========================================
# 5. CHECK DUPLICATES
# ==========================================

duplicate_count = df.duplicated().sum()

print("\n--- DUPLICATES ---")

if duplicate_count > 0:
    print(f"⚠️ Found {duplicate_count} duplicate rows")
else:
    print("✅ No duplicate rows found")


# ==========================================
# 6. SHOW CLEAN DATA
# ==========================================

print("\n==========================================")
print("           CLEAN DATA")
print("==========================================")

print(df)

print("\nFinal rows:", len(df))
# ==========================================
# 7. COLUMN INTELLIGENCE
# ==========================================

print("\n==========================================")
print("       COLUMN INTELLIGENCE REPORT")
print("==========================================")

for column in df.columns:

    # Check if column contains dates
    if pd.api.types.is_datetime64_any_dtype(df[column]):
        column_type = "DATE"

    # Check if column is numeric
    elif pd.api.types.is_numeric_dtype(df[column]):

        # ID columns usually contain unique values
        if "id" in column.lower() and df[column].nunique() == len(df):
            column_type = "ID"
        else:
            column_type = "MEASURE"

    # Everything else is treated as categorical
    else:
        column_type = "CATEGORY"

    print(f"{column:12} → {column_type}")
    # ==========================================
# 8. AUTOMATIC KPI ENGINE
# ==========================================

print("\n==========================================")
print("          AUTOMATIC KPI REPORT")
print("==========================================")

# Find all measure columns
measure_columns = []

for column in df.columns:

    if pd.api.types.is_numeric_dtype(df[column]):

        # Don't treat ID columns as measures
        if "id" in column.lower() and df[column].nunique() == len(df):
            continue

        measure_columns.append(column)


# Generate KPIs automatically
for column in measure_columns:

    total = df[column].sum()
    average = df[column].mean()
    minimum = df[column].min()
    maximum = df[column].max()

    print(f"\n📊 {column}")
    print(f"   Total   : {total:,.2f}")
    print(f"   Average : {average:,.2f}")
    print(f"   Minimum : {minimum:,.2f}")
    print(f"   Maximum : {maximum:,.2f}")
    # ==========================================
# 9. AUTOMATIC CHART RECOMMENDER
# ==========================================

print("\n==========================================")
print("       CHART RECOMMENDATIONS")
print("==========================================")

# Store columns according to their detected type
date_columns = []
category_columns = []
measure_columns = []

for column in df.columns:

    # Detect DATE columns
    if pd.api.types.is_datetime64_any_dtype(df[column]):
        date_columns.append(column)

    # Detect NUMERIC columns
    elif pd.api.types.is_numeric_dtype(df[column]):

        # Ignore ID columns
        if "id" in column.lower() and df[column].nunique() == len(df):
            continue

        measure_columns.append(column)

    # Everything else is treated as CATEGORY
    else:
        category_columns.append(column)


# ------------------------------------------
# Find the most important measure
# ------------------------------------------

def measure_score(column):

    name = column.lower()

    score = 0

    important_words = [
        "sales",
        "revenue",
        "amount",
        "profit",
        "income",
        "value"
    ]

    for word in important_words:
        if word in name:
            score += 2

    return score


if measure_columns:

    primary_measure = max(
        measure_columns,
        key=measure_score
    )

else:
    primary_measure = None


# ------------------------------------------
# Create recommendations
# ------------------------------------------

recommendations = []


# 1. DATE + MEASURE
if date_columns and primary_measure:

    recommendations.append({
        "chart_type": "Line Chart",
        "title": f"{primary_measure} Trend",
        "dimension": date_columns[0],
        "measure": primary_measure,
        "reason": "Date + measure detected"
    })


# 2. CATEGORY + PRIMARY MEASURE
if primary_measure:

    for category in category_columns:

        unique_values = df[category].nunique()

        if unique_values <= 10:

            recommendations.append({
                "chart_type": "Bar Chart",
                "title": f"{primary_measure} by {category}",
                "dimension": category,
                "measure": primary_measure,
                "reason": f"{category} has {unique_values} categories"
            })

        else:

            recommendations.append({
                "chart_type": "Top-N Bar Chart",
                "title": f"Top {category} by {primary_measure}",
                "dimension": category,
                "measure": primary_measure,
                "reason": f"{category} has {unique_values} unique values"
            })


# 3. SECONDARY MEASURE
secondary_measures = [
    column for column in measure_columns
    if column != primary_measure
]


if secondary_measures and category_columns:

    secondary_measure = secondary_measures[0]

    # Use a low-cardinality category
    for category in category_columns:

        if df[category].nunique() <= 10:

            recommendations.append({
                "chart_type": "Bar Chart",
                "title": f"{secondary_measure} by {category}",
                "dimension": category,
                "measure": secondary_measure,
                "reason": "Secondary measure + category detected"
            })

            break


# ------------------------------------------
# Display recommendations
# ------------------------------------------

for number, recommendation in enumerate(
    recommendations,
    start=1
):

    print(f"\n{number}. {recommendation['chart_type']}")
    print(f"   Title  : {recommendation['title']}")
    print(f"   Using  : {recommendation['dimension']} + "
          f"{recommendation['measure']}")
    print(f"   Reason : {recommendation['reason']}")
    # ==========================================
# 10. AUTOMATIC CHART GENERATOR
# ==========================================

import matplotlib.pyplot as plt

print("\n==========================================")
print("          GENERATING CHARTS")
print("==========================================")

for recommendation in recommendations:

    chart_type = recommendation["chart_type"]
    title = recommendation["title"]
    dimension = recommendation["dimension"]
    measure = recommendation["measure"]

    print(f"\nCreating: {title}")

    # --------------------------------------
    # LINE CHART
    # --------------------------------------

    if chart_type == "Line Chart":

        chart_data = (
            df.groupby(dimension)[measure]
            .sum()
            .reset_index()
        )

        chart_data = chart_data.sort_values(dimension)

        plt.figure(figsize=(10, 5))

        plt.plot(
            chart_data[dimension],
            chart_data[measure],
            marker="o"
        )

        plt.title(title)
        plt.xlabel(dimension)
        plt.ylabel(measure)

        plt.xticks(rotation=45)

        plt.tight_layout()

        plt.show()


    # --------------------------------------
    # BAR CHART
    # --------------------------------------

    elif chart_type == "Bar Chart":

        chart_data = (
            df.groupby(dimension)[measure]
            .sum()
            .reset_index()
        )

        chart_data = chart_data.sort_values(
            measure,
            ascending=False
        )

        plt.figure(figsize=(8, 5))

        plt.bar(
            chart_data[dimension],
            chart_data[measure]
        )

        plt.title(title)
        plt.xlabel(dimension)
        plt.ylabel(measure)

        plt.xticks(rotation=45)

        plt.tight_layout()

        plt.show()


    # --------------------------------------
    # TOP-N BAR CHART
    # --------------------------------------

    elif chart_type == "Top-N Bar Chart":

        chart_data = (
            df.groupby(dimension)[measure]
            .sum()
            .reset_index()
        )

        chart_data = chart_data.sort_values(
            measure,
            ascending=False
        )

        # Keep top 10
        chart_data = chart_data.head(10)

        plt.figure(figsize=(10, 5))

        plt.bar(
            chart_data[dimension],
            chart_data[measure]
        )

        plt.title(title)
        plt.xlabel(dimension)
        plt.ylabel(measure)

        plt.xticks(rotation=45)

        plt.tight_layout()

        plt.show()
