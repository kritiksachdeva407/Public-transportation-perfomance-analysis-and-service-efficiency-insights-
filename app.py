from pathlib import Path
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Public Transport Performance", page_icon="🚌", layout="wide")
st.title("🚌 Public Transportation Performance Analysis")
st.caption("Explore trip volume, punctuality, delays, route performance, and service patterns.")

ROOT = Path(__file__).resolve().parent
SAMPLE_PATH = ROOT / "data" / "sample_transit_data.csv"

REQUIRED = ["trip_id", "route_id", "scheduled_time", "actual_time"]
ALIASES = {
    "trip": "trip_id", "tripid": "trip_id", "route": "route_id",
    "routeid": "route_id", "scheduled": "scheduled_time",
    "scheduled_arrival": "scheduled_time", "actual": "actual_time",
    "actual_arrival": "actual_time", "passengers": "passenger_count",
    "cancelled_flag": "cancelled"
}

def normalize_columns(df):
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df.rename(columns={c: ALIASES[c] for c in df.columns if c in ALIASES})

def prepare_data(df):
    df = normalize_columns(df)
    missing = [c for c in ["route_id", "scheduled_time"] if c not in df.columns]
    if missing:
        raise ValueError("Missing required column(s): " + ", ".join(missing))
    if "trip_id" not in df:
        df["trip_id"] = [f"TRIP-{i+1}" for i in range(len(df))]
    if "actual_time" not in df:
        df["actual_time"] = pd.NaT
    if "cancelled" not in df:
        df["cancelled"] = False
    df["scheduled_time"] = pd.to_datetime(df["scheduled_time"], errors="coerce")
    df["actual_time"] = pd.to_datetime(df["actual_time"], errors="coerce")
    df["route_id"] = df["route_id"].astype("string").str.strip()
    df["cancelled"] = df["cancelled"].astype(str).str.strip().str.lower().isin(["true", "1", "yes", "y", "cancelled"])
    if "passenger_count" in df:
        df["passenger_count"] = pd.to_numeric(df["passenger_count"], errors="coerce")
    df = df.dropna(subset=["route_id", "scheduled_time"])
    df = df.drop_duplicates(subset=["trip_id", "route_id", "scheduled_time"])
    df["service_date"] = df["scheduled_time"].dt.date
    df["hour"] = df["scheduled_time"].dt.hour
    df["weekday"] = df["scheduled_time"].dt.day_name()
    df["delay_minutes"] = (df["actual_time"] - df["scheduled_time"]).dt.total_seconds() / 60
    df.loc[df["cancelled"], "delay_minutes"] = pd.NA
    return df

uploaded = st.sidebar.file_uploader("Upload transport CSV", type=["csv"])
use_sample = st.sidebar.checkbox("Use included demonstration dataset", value=uploaded is None)
st.sidebar.markdown("---")
on_time_threshold = st.sidebar.number_input("On-time threshold (minutes late)", min_value=0, max_value=60, value=5, step=1)
st.sidebar.caption("Sample data is synthetic and is included only to demonstrate the workflow.")

try:
    if uploaded is not None and not use_sample:
        raw = pd.read_csv(uploaded)
        source_label = uploaded.name
    else:
        raw = pd.read_csv(SAMPLE_PATH)
        source_label = "Included synthetic sample"
    df = prepare_data(raw)
except Exception as exc:
    st.error(f"Could not prepare this dataset: {exc}")
    st.info("See README.md for the expected CSV columns.")
    st.stop()

st.caption(f"Dataset: **{source_label}** · {len(raw):,} raw rows · {len(df):,} usable rows")
with st.expander("Data preview and quality checks"):
    st.write("Required fields: `route_id`, `scheduled_time`. For delay and punctuality, include `actual_time`.")
    st.dataframe(df.head(20), use_container_width=True)
    quality = pd.DataFrame({
        "Check": ["Raw rows", "Usable rows", "Duplicate records removed / invalid required rows", "Missing actual times", "Cancelled trips"],
        "Count": [len(raw), len(df), max(0, len(raw)-len(df)), int(df["actual_time"].isna().sum()), int(df["cancelled"].sum())]
    })
    st.dataframe(quality, hide_index=True, use_container_width=True)

completed = df[~df["cancelled"] & df["actual_time"].notna() & df["delay_minutes"].notna()].copy()
total_trips = len(df)
cancelled_count = int(df["cancelled"].sum())
if len(completed):
    on_time_rate = (completed["delay_minutes"] <= on_time_threshold).mean() * 100
    avg_delay = completed["delay_minutes"].mean()
else:
    on_time_rate, avg_delay = None, None

c1, c2, c3, c4 = st.columns(4)
c1.metric("Trips in dataset", f"{total_trips:,}")
c2.metric("On-time rate", f"{on_time_rate:.1f}%" if on_time_rate is not None else "N/A",
          help=f"On time means delay ≤ {on_time_threshold} minutes. Computed only for trips with actual times.")
c3.metric("Average delay", f"{avg_delay:.1f} min" if avg_delay is not None else "N/A",
          help="Computed for non-cancelled trips with valid actual and scheduled times.")
c4.metric("Cancellations", f"{cancelled_count:,}")

st.subheader("Performance overview")
left, right = st.columns(2)
with left:
    route_trips = df.groupby("route_id").size().sort_values(ascending=False).rename("trips")
    fig, ax = plt.subplots()
    route_trips.plot(kind="bar", ax=ax)
    ax.set_title("Trips by Route")
    ax.set_xlabel("Route")
    ax.set_ylabel("Trips")
    ax.tick_params(axis="x", rotation=0)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
with right:
    hourly = df.groupby("hour").size().reindex(range(24), fill_value=0)
    fig, ax = plt.subplots()
    hourly.plot(kind="line", marker="o", ax=ax)
    ax.set_title("Trip Volume by Scheduled Hour")
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Trips")
    ax.set_xticks(range(0,24,2))
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

st.subheader("Route-level performance")
if len(completed):
    route_perf = completed.groupby("route_id").agg(
        completed_trips=("trip_id", "count"),
        average_delay_minutes=("delay_minutes", "mean"),
        on_time_rate_percent=("delay_minutes", lambda x: (x <= on_time_threshold).mean()*100)
    ).round(2).reset_index()
    st.dataframe(route_perf, hide_index=True, use_container_width=True)
    fig, ax = plt.subplots()
    sns.barplot(data=route_perf, x="route_id", y="average_delay_minutes", ax=ax)
    ax.set_title("Average Delay by Route")
    ax.set_xlabel("Route")
    ax.set_ylabel("Average delay (minutes)")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
else:
    st.info("Route delay comparisons need valid actual arrival times for completed trips.")

st.subheader("Delay distribution")
if len(completed):
    fig, ax = plt.subplots()
    sns.histplot(completed["delay_minutes"].dropna(), bins=20, kde=True, ax=ax)
    ax.axvline(0, linestyle="--", linewidth=1)
    ax.set_title("Distribution of Arrival Delay")
    ax.set_xlabel("Delay in minutes (negative = early)")
    ax.set_ylabel("Number of trips")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    p50 = completed["delay_minutes"].quantile(.50)
    p90 = completed["delay_minutes"].quantile(.90)
    st.write(f"Median delay: **{p50:.1f} minutes** · 90th percentile: **{p90:.1f} minutes**")
else:
    st.info("No valid actual arrival times were found, so delay distribution is unavailable.")

if "passenger_count" in df.columns and df["passenger_count"].notna().any():
    st.subheader("Passenger usage")
    passenger_summary = df.groupby("route_id")["passenger_count"].agg(["count", "mean", "sum"]).round(2).reset_index()
    passenger_summary.columns = ["Route", "Trips with passenger data", "Average passengers", "Total passengers"]
    st.dataframe(passenger_summary, hide_index=True, use_container_width=True)
else:
    st.info("Passenger analysis is skipped because this dataset has no usable passenger_count field.")

st.subheader("Interpretation and limitations")
st.markdown("""
- Compare routes and time periods to identify where further investigation may be useful.
- A high delay or busy period is a signal for investigation, not proof of its cause.
- KPIs depend on the completeness and consistency of the uploaded records.
- Results from the included sample dataset are **synthetic demonstration results**, not real-world transport findings.
""")

st.download_button(
    "Download cleaned analysis data",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="cleaned_transport_data.csv",
    mime="text/csv"
)
