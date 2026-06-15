import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

st.title("Customer Segmentation")

# Load data
df = pd.read_csv("bank-additional-full.csv", sep=";")

# Remove target for segmentation
seg_df = df.drop("y", axis=1)

# Encode categorical variables
for col in seg_df.select_dtypes(include='object').columns:
    seg_df[col] = LabelEncoder().fit_transform(seg_df[col])

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(seg_df)

# Elbow Method
wcss = []

for k in range(2,11):
    km = KMeans(n_clusters=k, random_state=42)
    km.fit(X_scaled)
    wcss.append(km.inertia_)


# Fit final model
kmeans = KMeans(n_clusters=4, random_state=42)
clusters = kmeans.fit_predict(X_scaled)

df["Customer_Segment"] = clusters

profile_rows = []

categorical_cols = [
    "loan",
    "default",
    "housing",
    "poutcome",
    "marital"
]

numeric_cols = [
    "age",
    "duration",
    "previous",
    "pdays"
]

for segment in sorted(df["Customer_Segment"].unique()):

    temp = df[df["Customer_Segment"] == segment]

    row = {}

    row["Customers"] = len(temp)

    # Conversion Rate
    row["Conversion_Rate_%"] = round(
        (temp["y"] == "yes").mean() * 100,
        2
    )

    # Numerical Aggregates
    for col in numeric_cols:
        row[f"{col}_mean"] = round(temp[col].mean(), 2)
        
    # Categorical Percentage Distributions
    for col in categorical_cols:

        pct_dist = (
            temp[col]
            .value_counts(normalize=True)
            .mul(100)
            .round(2)
        )

        for category in sorted(df[col].unique()):
            row[f"{col}_{category}_pct"] = pct_dist.get(
                category,
                0
            )

    profile_rows.append(row)

cluster_profile = pd.DataFrame(profile_rows)
cluster_profile['Segment'] = ['A', 'B', 'C', 'D']


print(df["Customer_Segment"].value_counts())


h1, h2 =st.columns([3,2])
with h1.popover(label='Interactive 3D Segment Visualisation', width='stretch'):
    c1, c2, c3 = st.columns(3)
    f1 = c1.selectbox("X-axis", options=cluster_profile.columns.to_list(), index=1)
    f2 = c2.selectbox("Y-axis", options=cluster_profile.columns.to_list(), index=2)
    f3 = c3.selectbox("Z-axis", options=cluster_profile.columns.to_list(), index=3)

    fig = px.scatter_3d(
        cluster_profile,
        x=f1,
        y=f2,
        z=f3,
        color="Segment",           # color by cluster
        text="Segment",            # permanent label
    )

    fig.update_traces(
        marker=dict(size=8),
        textposition="top center"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with h2.popover(label='Segment-wise Aggregated Data', width='stretch'):
    st.dataframe(cluster_profile.set_index("Segment").T)

st.divider()
c1, temp1, c2, temp2,  c3, temp3, c4 = st.columns([1, 0.04, 1, 0.04, 1, 0.08, 1])

with c1:
    st.subheader('Segment A')
    st.write('***The Dormant Mass Market***')
    st.write('(13,341 clients, 5.8% conversion)')
    
    with st.container(border=True, height=300):
        st.markdown("""
                 
#### Interpretation
This is the bank's largest pool of "unknown" customers. They have not meaningfully interacted with prior campaigns and exhibit limited engagement signals.

#### Business Impact
Represents a large volume opportunity but low immediate efficiency.Broad marketing to this segment is likely to generate high acquisition costs with limited conversion uplift.
Better suited for low-cost digital campaigns, awareness initiatives, and nurturing programs before direct sales outreach.
#### Recommendation
Reduce expensive outbound calling. Use digital-first engagement strategies to identify customers showing intent before deploying sales resources.
                 """)
        
with c2:
    st.subheader('Segment B')
    st.write('***Previously engaged prospects***')
    st.write('(12,702 clients, 18.6% conversion)')
    
    with st.container(border=True, height=300):
        st.markdown("""
                 
#### Interpretation
These customers have already entered the marketing funnel and have demonstrated willingness to engage, even if previous campaigns were unsuccessful.

#### Business Impact
1. Conversion rate is over 3x higher than Segment 1.
2. Prior interaction history appears to be a strong predictor of future conversion.
3. This segment contains "warm leads" rather than cold prospects.
                    
#### Recommendation 
Prioritize for targeted reactivation campaigns. Customers who previously engaged but did not convert represent one of the highest ROI marketing opportunities.
                 """)

with c3:
    st.subheader('Segment C')
    st.write('***Conservative non-responders***')
    st.write('(13,629 clients, 3.9% conversion)')
    
    with st.container(border=True, height=300):
        st.markdown("""
                 
#### Interpretation
This group resembles the dormant population but exhibits even weaker conversion behavior and lower responsiveness to marketing activity.

#### Business Impact
- Lowest conversion rate among the large customer segments.
- Represents substantial marketing spend risk if treated identically to other customers.
- Significant opportunity cost exists when sales teams prioritize this group over higher-performing segments.
                    
#### Recommendation 
Deprioritize for direct acquisition efforts. Focus only on highly targeted offers or automated campaigns with minimal acquisition costs.
                 """)
        
with c4:
    st.subheader('Segment D')
    st.markdown('***High-yield responders***')
    st.write('(1,516 clients, 63.8% conversion)')
    
    with st.container(border=True, height=300):
        st.markdown("""
                 
#### Interpretation
This segment consists almost entirely of customers who have already demonstrated a strong positive response to previous marketing efforts.

#### Business Impact
- Converts at **11x the rate of Segment 1**.
- Although only 4% of the customer base, this segment likely contributes a disproportionate share of total campaign conversions.
- Represents the highest-value audience for upselling, cross-selling, and premium product offerings.
#### Recommendation 
Allocate a disproportionate share of marketing resources here. These customers should be treated as a strategic revenue segment rather than a generic campaign audience.
                 """)

st.subheader('Additional insights')
st.markdown("""
1. The analysis reveals that **historical engagement is a far stronger predictor** of conversion than demographic characteristics. 
-   Customers contacted recently, multiple times and were previously successful
are much more likely to convert.
2. A campaign strategy that reallocates outreach capacity from Segments 1 and 3 toward Segments 2 and 4 could materially improve conversion efficiency while reducing customer acquisition costs. **Segment 4 alone delivers conversion rates** that are approximately **16 times higher** than the lowest-performing segment, indicating substantial potential for marketing ROI optimization.""")
