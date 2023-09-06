import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

date_format = "%m/%d/%Y"

df = pd.read_csv(
    "eur_usd.csv",
    parse_dates=["Date"],
    dayfirst=True,
)

df.drop(["Open", "Vol.", "Change %"], axis=1, inplace=True)

df["Week"] = df["Date"].apply(
    lambda x: datetime.strptime(x, date_format).strftime("%Y-%W")
)
df["Day"] = df["Date"].apply(
    lambda x: datetime.strptime(x, date_format).strftime("%A")
)

week_max_price = df.groupby("Week")["High"].idxmax()
week_min_price = df.groupby("Week")["Low"].idxmin()

week_max_df = df.loc[week_max_price, ["Week", "High", "Day"]].reset_index(
    drop=True
)
week_min_df = df.loc[week_min_price, ["Week", "Low", "Day"]].reset_index(
    drop=True
)

max_day_counts = week_max_df["Day"].value_counts()
min_day_counts = week_min_df["Day"].value_counts()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# Plot max week price chart
max_day_counts.plot(kind="bar", color="skyblue", alpha=0.7, ax=ax1)
ax1.set_title("Max Week Price Formation Over Day of Week")
ax1.set_xlabel("Day of Week")
ax1.set_ylabel("Frequency")
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=0)

# Annotate the max_day_counts bars with their values
for i, v in enumerate(max_day_counts):
    ax1.text(i, v, str(v), ha="center", va="bottom")

# Plot min week price chart
min_day_counts.plot(kind="bar", color="salmon", alpha=0.7, ax=ax2)
ax2.set_title("Min Week Price Formation Over Day of Week")
ax2.set_xlabel("Day of Week")
ax2.set_ylabel("Frequency")
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=0)

# Annotate the min_day_counts bars with their values
for i, v in enumerate(min_day_counts):
    ax2.text(i, v, str(v), ha="center", va="bottom")

# Add a common title above both charts
plt.suptitle("EUR-USD. Date Range: 2018-Now")

plt.tight_layout()  # Ensure the subplots don't overlap
plt.savefig("week_price_day.png", dpi=200)
plt.show()
