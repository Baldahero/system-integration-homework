import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Bus Delay System (Demo)")

# DEMO DATA (вместо базы данных)
predicted_arrivals = pd.DataFrame({
    "stop_name": ["Stop 1", "Stop 2", "Stop 3", "Stop 4", "Stop 5"],
    "planned_time": ["08:00", "08:10", "08:20", "08:30", "08:40"],
    "predicted_time": ["08:05", "08:18", "08:32", "08:45", "08:55"],
    "delay_min": [5, 8, 12, 15, 15]
})

# Таблица
st.subheader("Predicted Arrivals")
st.dataframe(predicted_arrivals)

# График
fig = px.bar(
    predicted_arrivals,
    x="stop_name",
    y="delay_min",
    title="Delay at Each Stop"
)

st.plotly_chart(fig, use_container_width=True)
