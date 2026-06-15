import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.title('Economic Indicators affecting Conversion rate')

# Load data
df = pd.read_csv("bank-additional-full.csv", sep=";")

# Convert target to binary
df["y_binary"] = df["y"].map({"yes": 1, "no": 0})

# Correct month ordering
month_order = [
    "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct",
    "nov", "dec"
]

df["month"] = pd.Categorical(
    df["month"],
    categories=month_order,
    ordered=True
)

# Economic indicators available
economic_indicators = [
    "emp.var.rate",
    "cons.price.idx",
    "cons.conf.idx",
    "euribor3m",
    "nr.employed"
]

selected_indicator = st.selectbox(
    "Select Economic Indicator",
    economic_indicators
)

# Monthly aggregation
monthly_data = (
    df.groupby("month", observed=False)
      .agg(
          conversion_rate=("y_binary", "mean"),
          economic_value=(selected_indicator, "mean")
      )
      .reset_index()
)

monthly_data["conversion_rate"] *= 100

# Create dual-axis chart
fig = make_subplots(
    specs=[[{"secondary_y": True}]]
)

# Conversion rate
fig.add_trace(
    go.Scatter(
        x=monthly_data["month"],
        y=monthly_data["conversion_rate"],
        mode="lines",
        line_shape='spline',
        name="Conversion Rate (%)"
    ),
    secondary_y=False
)

# Economic indicator
fig.add_trace(
    go.Scatter(
        x=monthly_data["month"],
        y=monthly_data["economic_value"],
        mode="lines",
        line_shape='spline',
        name=selected_indicator
    ),
    secondary_y=True
)

# Layout
fig.update_layout(
    title=f"Monthly Conversion Rate vs {selected_indicator}",
    hovermode="x unified",
    height=600
)

fig.update_yaxes(
    title_text="Conversion Rate (%)",
    showgrid=False,
    secondary_y=False
)

fig.update_yaxes(
    title_text=selected_indicator,
    secondary_y=True,
    showgrid=False
)

st.plotly_chart(fig, use_container_width=True)