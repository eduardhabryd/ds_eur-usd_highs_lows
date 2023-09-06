from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
import pytz
import matplotlib.pyplot as plt

if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

timezone = pytz.timezone("Etc/UTC")
utc_from = datetime(2000, 1, 1, tzinfo=timezone)
utc_to = datetime(2023, 9, 5, hour=13, tzinfo=timezone)
rates = mt5.copy_rates_range("EURUSD", mt5.TIMEFRAME_D1, utc_from, utc_to)
mt5.shutdown()

rates_frame = pd.DataFrame(rates)
rates_frame["time"] = pd.to_datetime(rates_frame["time"], unit="s")
rates_frame.drop(
    ["open", "tick_volume", "spread", "real_volume", "close"],
    axis=1,
    inplace=True,
)

date_format = "%Y-%m/%d"

rates_frame["week"] = rates_frame["time"].apply(lambda x: x.strftime("%Y-%W"))
rates_frame["day"] = rates_frame["time"].apply(lambda x: x.strftime("%A"))

week_max_price = rates_frame.groupby("week")["high"].idxmax()
week_min_price = rates_frame.groupby("week")["low"].idxmin()

week_max_df = rates_frame.loc[
    week_max_price, ["week", "high", "day"]
].reset_index(drop=True)
week_min_df = rates_frame.loc[
    week_min_price, ["week", "low", "day"]
].reset_index(drop=True)

max_day_counts = week_max_df["day"].value_counts()
min_day_counts = week_min_df["day"].value_counts()

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
plt.suptitle(
    f"| EUR-USD | Date Range: {utc_from.strftime('%Y.%m.%d')} - {utc_to.strftime('%Y.%m.%d')} |"
)

plt.tight_layout()  # Ensure the subplots don't overlap
plt.savefig("week_price_day.png", dpi=200)
