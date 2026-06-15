import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import LabelEncoder

# Load data
df = pd.read_csv("bank-additional-full.csv", sep=";")

st.title("Correlation Heatmap")

# Create a copy
corr_df = df.copy()

# Encode categorical columns
le = LabelEncoder()

for col in corr_df.select_dtypes(include=["object"]).columns:
    corr_df[col] = le.fit_transform(corr_df[col].astype(str))

# Correlation matrix
corr_matrix = corr_df.corr()

# Plotly heatmap
fig = px.imshow(
    corr_matrix,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1,
    aspect="auto"
)

fig.update_layout(
    height=800,
    width=1000,
    title="Correlation Matrix"
)

st.plotly_chart(fig, use_container_width=True)