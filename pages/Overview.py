import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sklearn.linear_model import LogisticRegression

from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.title("Term Deposit Marketing Campaign Dashboard")
data = pd.read_csv("bank-additional-full.csv", delimiter=';')

def preprocessing():
    month_order = [ "mar", "apr", "may", "jun",
        "jul", "aug", "sep", "oct", "nov", "dec"
    ]

    data["month"] = pd.Categorical(
        data["month"].str.lower(),
        categories=month_order,
        ordered=True
    )
    st.markdown("""
    <style>
                
    /* Metric card */
    [data-testid="stMetric"] {
        text-align: center;
    }
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"] {
        justify-content: center;
        width: 100%;
    }

    /* Label */
    [data-testid="stMetricLabel"] {
        justify-content: center;
        width: 100%;
    }

    /* Value */
    [data-testid="stMetricValue"] {
        justify-content: center;
        width: 100%;
    }
    
    [data-testid="stMetricValue"] {
    font-weight: 500;
    }

    /* Delta */
    [data-testid="stMetricDelta"] {
        justify-content: center;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

preprocessing()

def kpi(data):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label = "Total Clients", value=data.shape[0],border=True, height=135, )
    with col2:
        st.metric(label = "Successes", value=data['y'].value_counts()[1],border=True, delta=f"{data['y'].value_counts()[1]/data.shape[0] * 100:.2f}" + "%", delta_arrow="off")
    with col3:
        st.metric(label="High-Intent Calls", value=f"{(data['duration'] >= 300).mean() * 100:.2f}%", border = True, delta="Calls > 300s", delta_arrow="off")
    with col4:
        st.metric(label="Calls per conversion", value=f"{len(data) / (data['y'] == 'yes').sum():.1f}", border = True, delta_arrow="off", height=135)



kpi(data)

#st.dataframe(data)
c1, p1, c2, p2, c3 = st.columns([1,0.1,1,0.1,1])
month_conv = data[["month", "y"]].groupby('month')['y'].apply(lambda x: (x == 'yes').mean() * 100)

#Monthwise Conversion
with c1:
    fig = px.line(data_frame=month_conv, height=250)
    fig.update_yaxes(showgrid=False, title='Successes')
    fig.update_layout(showlegend=False)
    fig.update_traces(
        line_shape='spline',
        fill="tozeroy",
        fillgradient=dict(
            type="vertical",
            colorscale=[
                [0.00, "rgba(59,130,246,0.00)"],  # bottom
                [0.25, "rgba(59,130,246,0.05)"],
                [0.50, "rgba(59,130,246,0.15)"],
                [0.75, "rgba(59,130,246,0.35)"],
                [1.00, "rgba(59,130,246,0.80)"]   # near line
            ]
        ),
        line=dict(color="rgb(59,130,246)", width=3)
    )
    annotations = [
        dict(x='jun', y=25, text="Least conversion rate", showarrow=False)
    ]

    fig.update_layout(annotations=annotations)
    fig.add_vline(
        x=1,
        annotation_text="April",
        annotation_position='top left',
        line_color='purple',
        opacity=0.2
    )
    fig.add_vline(
        x=5,
        annotation_text="August",
        line_color='purple',
        opacity=0.2
    )

    fig.update_layout(
    margin=dict(
        l=10,
        r=10,
        t=10,
        b=20
    )
)
    st.subheader(
    "Monthly conversions",
    help="April to August have the lowest conversion rates, coincides perfectly with economic uncertainty (refer to Economic Indicators in Additional Charts)"
)
    
    st.plotly_chart(fig, height=180)

#Previous Campaign
with c2:
    poutcome_conv = (
    data.groupby("poutcome")["y"]
        .apply(lambda x: (x == "yes").mean() * 100)
        .reset_index(name="conversion_rate")
    )

    fig = px.bar(
    poutcome_conv.sort_values("conversion_rate"),
    x="conversion_rate",
    y="poutcome",
    orientation="h",
    text="conversion_rate",
    )
    fig.update_layout(
    bargap=0.26,
    barcornerradius=4
    )

    fig.update_yaxes(title_text="Previous Outcome")
    fig.update_xaxes(title_text="Conversion Rate (%)")

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="inside",
        marker_color='#635BFF'
    )
    fig.update_layout(
    margin=dict(
        l=10,
        r=10,
        t=10,
        b=20
    )
    )

    st.subheader(
    "Prior campaign",
    help="Even if past campaigns have failed, they have a better conversion rate than first-time clients. 65% of people who have had succesful prior campiagns have converted again."
    )
    st.plotly_chart(fig, height=180)

#Duration Probability 
with c3:
    # X = duration
    X = data[["duration"]]

    # y = 1 if yes, 0 if no
    y = (data["y"] == "yes").astype(int)

    # Fit model
    model = LogisticRegression()
    model.fit(X, y)

    max_duration = data["duration"].quantile(0.9995)

    # Generate smooth range of durations
    x_range = np.linspace(
        data["duration"].min(),
        max_duration,
        250
    ).reshape(-1, 1)

    # Predict probabilities
    y_prob = model.predict_proba(x_range)[:, 1]

    # Plot
    fig = px.line(
        x=x_range.flatten()/60,  # convert to minutes
        y=y_prob * 100,
        labels={
            "x": "Call Duration (minutes)",
            "y": "Probability of Conversion (%)"
        },
        height=180
    )

    fig.update_yaxes(showgrid=False)
    fig.update_layout(
        showlegend=False,
        yaxis_range=[0, 100]
    )

    fig.add_hline(
        y=50,
        annotation_text="50% chance",
        opacity=0.3,
        line_color='red'
    )

    fig.add_vline(
        x=data["duration"].median()/60,
        line_dash="dash",
        annotation_text="Median",
        opacity=0.4
    )
    fig.update_traces(
        line_shape="spline",
        fill="tozeroy",
        fillgradient=dict(
            type="vertical",
            colorscale=[
                [0.00, "rgba(220,38,38,0.00)"],
                [0.30, "rgba(220,38,38,0.00)"],
                [0.60, "rgba(220,38,38,0.25)"],
                [1.00, "rgba(220,38,38,0.95)"]
            ]
        ),
        line=dict(
            color="#DC2626",
            width=3
        )
    )
    fig.update_layout(
    margin=dict(
        l=10,
        r=10,
        t=10,
        b=20
    )
)
    st.subheader("Time on call",
    help="An average call lasts for 2 mins, but it needs to be at least 15 minutes to get a 50-50 chance of converting"
)

    st.plotly_chart(fig, height=180)

c4, c5, c6 = st.columns([0.5,2,3])

#Button
with c4:
    order = st.pills("", options=['Best', "Worst"], default="Best")

    ascending = {
        "Best": False,
        "Worst": True
    }[order]

#Jobwise conversion
with c5:
    job_conversion = (
    data.groupby("job")["y"]
      .value_counts(normalize=True)
      .unstack(fill_value=0)
      .reset_index()
    )   

    job_conversion["conversion_rate"] = job_conversion["yes"] * 100

    job_conversion = job_conversion.sort_values(
        "conversion_rate",
        ascending=ascending
    ).reset_index()

    mean_row = pd.DataFrame({
    "job": ["Average"],
    "conversion_rate": [job_conversion["conversion_rate"].mean()]
    })

    job_conversion = pd.concat(
        [job_conversion, mean_row],
        ignore_index=True
    )



    fig = px.bar(
        job_conversion.iloc[[0, 1, 2, 3, -1]],
        x="conversion_rate",
        y="job",
        orientation="h",
        text="conversion_rate",
        height=300
    )

    fig.update_layout(
    margin=dict(
        l=10,
        r=10,
        t=10,
        b=20
    )
)

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="inside"
    )

    fig.update_layout(
        xaxis_title="Conversion Rate (%)",
        yaxis_title="Job"
    )

    colors = ["#635BFF"] * (4) + ["#C53030"] 

    fig.update_traces(
        marker_color=colors
    )

    fig.update_layout(
    bargap=0.26,
    barcornerradius=4
    )
    
    st.subheader(
    "Jobwise conversion",
    help="Students are the job segment with the highest ROI, and blue-collar workers the lowest (Could be due to disposable income and/or needs)"
)
    st.plotly_chart(fig, height=180)

#Agewise conversion
with c6:
    bins = [18, 30, 40, 50, 60, 70, 100]
    labels = ["18-29", "30-39", "40-49", "50-59", "60-69", "70+"]

    data["age_group"] = pd.cut(
        data["age"],
        bins=bins,
        labels=labels,
        right=False
    )

    age_stats = (
        data.groupby("age_group", observed=True)
            .agg(
                total_conversions=("y", lambda x: (x == "yes").sum()),
                conversion_rate=("y", lambda x: (x == "yes").mean() * 100)
            )
            .reset_index()
    )

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Bars = total conversions
    fig.add_trace(
        go.Bar(
            x=age_stats["age_group"],
            y=age_stats["total_conversions"],
            name="Conversions",
            marker_color="#9ca3af",
            opacity=0.5
        ),
        secondary_y=False
    )

    # Line = conversion rate
    fig.add_trace(
        go.Scatter(
            x=age_stats["age_group"],
            y=age_stats["conversion_rate"],
            mode="lines+markers",
            line_shape='spline',
            name="Conversion Rate",
            line=dict(color="#df1b41", width=3)
        ),
        secondary_y=True
    )

    fig.update_yaxes(
        title_text="Conversions",
        showgrid=False,
        secondary_y=False
    )

    fig.update_yaxes(
        title_text="Conversion Rate (%)",
        showgrid=False,
        secondary_y=True
    )

    fig.update_layout(
        height=250,
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(
            orientation="h",
            y=1.05,
            x=1,
            xanchor="right"
        )
    )
    fig.update_layout(
    bargap=0.26,
    barcornerradius=4
    )

    annotations = [
        dict(x='30-39', y=1250, text="Low rate, yet most conversions", showarrow=True, )
    ]

    fig.update_layout(annotations=annotations)

    fig.update_layout(
    margin=dict(
        l=10,
        r=10,
        t=10,
        b=20
    )
)
    st.subheader(
    "Conversions by age",
    help="Although 30-39 is one of the bins with the least conversion rate, they still account for the largest total conversions. Focus on improving conversion rate for this category."
)


    st.plotly_chart(fig, height=180)
