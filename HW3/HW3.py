import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Bus Delay System", layout="wide")

st.title("Bus Delay Monitoring System")
st.markdown("System integration project: predicted bus arrivals and delay analysis.")

# Demo dataset
data = pd.DataFrame({
    "route": ["Route A", "Route A", "Route A", "Route A", "Route A",
              "Route B", "Route B", "Route B", "Route B", "Route B"],
    "stop_name": ["Stop 1", "Stop 2", "Stop 3", "Stop 4", "Stop 5",
                  "Stop 1", "Stop 2", "Stop 3", "Stop 4", "Stop 5"],
    "planned_time": ["08:00", "08:10", "08:20", "08:30", "08:40",
                     "09:00", "09:12", "09:24", "09:36", "09:48"],
    "predicted_time": ["08:05", "08:18", "08:32", "08:45", "08:55",
                       "09:03", "09:19", "09:31", "09:44", "09:58"],
    "delay_min": [5, 8, 12, 15, 15, 3, 7, 7, 8, 10],
    "reason": ["Traffic", "Traffic", "Road works", "Road works", "Weather",
               "Traffic", "Traffic", "Weather", "Weather", "Traffic"]
})

# Sidebar filters
st.sidebar.header("Filters")
selected_route = st.sidebar.selectbox("Select route", sorted(data["route"].unique()))
filtered = data[data["route"] == selected_route].copy()

# Metrics
max_delay = filtered["delay_min"].max()
avg_delay = round(filtered["delay_min"].mean(), 1)
total_stops = filtered["stop_name"].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("Route", selected_route)
col2.metric("Average delay", f"{avg_delay} min")
col3.metric("Maximum delay", f"{max_delay} min")

st.divider()

# Table + summary
left, right = st.columns([1.2, 1])

with left:
    st.subheader("Predicted Arrivals")
    st.dataframe(filtered, use_container_width=True)

with right:
    st.subheader("Delay Reasons")
    reason_counts = filtered["reason"].value_counts().reset_index()
    reason_counts.columns = ["reason", "count"]
    fig_reason = px.pie(reason_counts, names="reason", values="count", title="Main delay factors")
    st.plotly_chart(fig_reason, use_container_width=True)

st.divider()

# Delay bar chart
st.subheader("Delay at Each Stop")
fig_bar = px.bar(
    filtered,
    x="stop_name",
    y="delay_min",
    text="delay_min",
    title=f"Delay per Stop for {selected_route}"
)
fig_bar.update_traces(textposition="outside")
st.plotly_chart(fig_bar, use_container_width=True)

# Planned vs predicted
st.subheader("Planned vs Predicted Arrival Times")

plot_df = filtered.copy()
plot_df["planned_dt"] = pd.to_datetime(plot_df["planned_time"], format="%H:%M")
plot_df["predicted_dt"] = pd.to_datetime(plot_df["predicted_time"], format="%H:%M")

line_df = pd.DataFrame({
    "stop_name": list(plot_df["stop_name"]) + list(plot_df["stop_name"]),
    "time": list(plot_df["planned_dt"]) + list(plot_df["predicted_dt"]),
    "type": ["Planned"] * len(plot_df) + ["Predicted"] * len(plot_df)
})

fig_line = px.line(
    line_df,
    x="stop_name",
    y="time",
    color="type",
    markers=True,
    title=f"Planned vs Predicted Times for {selected_route}"
)
st.plotly_chart(fig_line, use_container_width=True)

st.divider()

st.subheader("Conclusion")
st.write(
    "This dashboard demonstrates how transportation delay data can be visualized "
    "in a cloud-deployed Streamlit application. For online deployment, demo data is used "
    "instead of a local MariaDB connection."
)
