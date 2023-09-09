from datetime import datetime, timedelta
import MetaTrader5 as mt5
import pandas as pd
import pytz
import matplotlib.pyplot as plt

if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

timezone = pytz.timezone("Etc/UTC")

# Define the start and end years
start_year = 2015
end_year = 2023

# Retrieve data for the first and last years in the range
utc_from_start = datetime(start_year, 1, 1, tzinfo=timezone)
utc_to_start = datetime(start_year + 1, 12, 31, hour=13, tzinfo=timezone)

utc_from_end = datetime(end_year, 1, 1, tzinfo=timezone)
utc_to_end = datetime(end_year, 12, 31, hour=13, tzinfo=timezone)

# Get the rates data for the entire date range once
rates = mt5.copy_rates_range(
    "EURUSD", mt5.TIMEFRAME_D1, utc_from_start, utc_to_end
)
mt5.shutdown()

rates_frame = pd.DataFrame(rates)
rates_frame["time"] = pd.to_datetime(
    rates_frame["time"], unit="s", utc=True
)  # Ensure timezone awareness
rates_frame.drop(
    ["open", "tick_volume", "spread", "real_volume", "close"],
    axis=1,
    inplace=True,
)

date_format = "%Y-%m/%d"

rates_frame["week"] = rates_frame["time"].apply(lambda x: x.strftime("%Y-%W"))
rates_frame["day"] = rates_frame["time"].apply(lambda x: x.strftime("%A"))

# Create a list of years to loop through
years = list(range(start_year, end_year + 1))

# Create subplots for the charts
fig, axs = plt.subplots(3, 6, figsize=(24, 12))

for row in axs:
    for i in range(0, len(row) - 1, 2):
        ax1 = row[i]
        ax2 = row[i + 1]

        # Get the current year in the loop
        year = years.pop(0)  # Remove the first year in the list

        # Filter the data for the current year
        year_data = rates_frame[
            (rates_frame["time"] >= datetime(year, 1, 1, tzinfo=timezone))
            & (rates_frame["time"] < datetime(year + 1, 1, 1, tzinfo=timezone))
        ]

        week_max_price = year_data.groupby("week")["high"].idxmax()
        week_min_price = year_data.groupby("week")["low"].idxmin()

        week_max_df = year_data.loc[
            week_max_price, ["week", "high", "day"]
        ].reset_index(drop=True)
        week_min_df = year_data.loc[
            week_min_price, ["week", "low", "day"]
        ].reset_index(drop=True)

        max_day_counts = week_max_df["day"].value_counts()
        min_day_counts = week_min_df["day"].value_counts()

        # Plot max week price chart
        max_day_counts.plot(kind="bar", color="skyblue", alpha=0.7, ax=ax1)
        ax1.set_title(f"Max Week Price Formation {year}")
        ax1.set_xlabel("")
        ax1.set_ylabel("Frequency")
        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45)

        # Annotate the max_day_counts bars with their values
        for i, v in enumerate(max_day_counts):
            ax1.text(i, v, str(v), ha="center", va="bottom")

        # Plot min week price chart
        min_day_counts.plot(kind="bar", color="salmon", alpha=0.7, ax=ax2)
        ax2.set_title(f"Min Week Price Formation {year}")
        ax2.set_xlabel("")
        ax2.set_ylabel("Frequency")
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45)

        # Annotate the min_day_counts bars with their values
        for i, v in enumerate(min_day_counts):
            ax2.text(i, v, str(v), ha="center", va="bottom")

        plt.suptitle(f"Year: {year}")

# Add a common title above all the charts
plt.suptitle(
    f"| EUR-USD | Date Range: {utc_from_start.strftime('%Y.%m.%d')} - {utc_to_end.strftime('%Y.%m.%d')} |"
)

plt.tight_layout()  # Ensure the subplots don't overlap
plt.savefig("yearly_week_price_day.png", dpi=250)
