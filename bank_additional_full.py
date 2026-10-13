
import pandas as pd

# 1. Fix and read the original dataset
with open("bank_additional_full.csv", encoding="utf-8") as file:
    lines = file.readlines()

clean_lines = []
for line in lines:
    line = line.strip()
    if line.startswith('"') and line.endswith('"'):
        line = line[1:-1]
    clean_lines.append(line.replace('""', '"'))

with open("bank_fixed.csv", "w", encoding="utf-8") as file:
    file.write("\n".join(clean_lines))

df = pd.read_csv("bank_fixed.csv", sep=";")

# 2. Clean and save the data
df = df.drop_duplicates()
df.to_csv("bank_marketing_cleaned.csv", index=False)

print("Rows:", len(df))
print("Missing values:", df.isnull().sum().sum())
print("Duplicates:", df.duplicated().sum())

# 3. Overall campaign performance
total = len(df)
yes = (df["y"] == "yes").sum()
no = (df["y"] == "no").sum()
rate = yes / total * 100

print("\nTotal customers:", total)
print("Subscribed:", yes)
print("Not subscribed:", no)
print("Conversion rate:", round(rate, 2), "%")

# 4. Create useful customer groups
df["age_group"] = pd.cut(
    df["age"], [0, 25, 35, 45, 55, 65, float("inf")],
    labels=["18-25", "26-35", "36-45", "46-55", "56-65", "66+"]
)
df["campaign_group"] = pd.cut(
    df["campaign"], [0, 1, 2, 3, 5, float("inf")],
    labels=["1", "2", "3", "4-5", "6+"]
)
df["previous_group"] = pd.cut(
    df["previous"], [-1, 0, 1, 2, 5, float("inf")],
    labels=["0", "1", "2", "3-5", "6+"]
)

# 5. Analyze conversion by different categories
columns = {
    "job": "job",
    "contact": "contact",
    "marital": "marital_status",
    "education": "education",
    "poutcome": "previous_campaign_outcome",
    "month": "month",
    "day_of_week": "day",
    "housing": "housing_loan",
    "loan": "personal_loan",
    "age_group": "age_group",
    "campaign_group": "campaign_contacts",
    "previous_group": "previous_contacts"
}

for column, filename in columns.items():
    result = pd.crosstab(df[column], df["y"])
    for outcome in ["yes", "no"]:
        if outcome not in result.columns:
            result[outcome] = 0
    result["Conversion_Rate"] = (
        result["yes"] / (result["yes"] + result["no"]) * 100
    )
    result = result.sort_values("Conversion_Rate", ascending=False)
    result.to_csv("conversion_by_" + filename + ".csv")
    print(f"\nConversion by {column}:")
    print(result.round(2))

# 6. Print key business insights
for column in ["job", "contact", "month"]:
    rates = df.groupby(column, observed=True)["y"].apply(
        lambda x: (x == "yes").mean() * 100
    )
    print(f"\nHighest conversion by {column}:",
          rates.idxmax(), "-", round(rates.max(), 2), "%")

# 7. Save the overall summary
pd.DataFrame({
    "Metric": ["Total Customers", "Subscribed", "Not Subscribed",
               "Conversion Rate (%)"],
    "Value": [total, yes, no, round(rate, 2)]
}).to_csv("campaign_summary.csv", index=False)

print("\nProject completed successfully!")