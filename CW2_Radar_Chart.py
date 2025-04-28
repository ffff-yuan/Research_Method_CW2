import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import plotly.graph_objects as go
import plotly.express as px
import plotly.offline as pyo

# Load dataset
df = pd.read_csv('Results_21Mar2022.csv')

# Define the metrics and their display names
metrics = [
    'mean_ghgs', 'mean_land', 'mean_watscar', 'mean_eut',
    'mean_ghgs_ch4', 'mean_ghgs_n2o', 'mean_bio', 'mean_watuse', 'mean_acid'
]
metric_labels = [
    'GHG Emissions', 'Land Use', 'Water Scarcity', 'Eutrophication',
    'CH₄ Emissions', 'N₂O Emissions', 'Biodiversity Impact', 'Agricultural Water Use', 'Acidification'
]

metric_units = {
    'GHG Emissions':            'kg',
    'Land Use':                 'm²',
    'Water Scarcity':           '',
    'Eutrophication':           'g',
    'CH₄ Emissions':            'kg',
    'N₂O Emissions':            'kg',
    'Biodiversity Impact':      '',
    'Agricultural Water Use':   'm³',
    'Acidification':            ''
}

# summarize by grouping columns
def summarize_by(cols):
    return df.groupby(cols)[metrics].mean().reset_index()

# Create summary tables
df_sex      = summarize_by(['sex'])
df_age      = summarize_by(['age_group'])
df_diet     = summarize_by(['diet_group'])
df_sex_age  = summarize_by(['sex','age_group'])
df_sex_diet = summarize_by(['sex','diet_group'])
df_age_diet = summarize_by(['age_group','diet_group'])
df_all      = summarize_by(['diet_group','sex','age_group'])

# Combine all into a DataFrame
records = []
def add_records(subdf, cols):
    for _, row in subdf.iterrows():
        name = " | ".join(str(row[c]) for c in cols)
        rec = {'name': name}
        for m in metrics:
            rec[m] = row[m]
        records.append(rec)

add_records(df_sex, ['sex'])
add_records(df_age, ['age_group'])
add_records(df_diet, ['diet_group'])
add_records(df_sex_age, ['sex','age_group'])
add_records(df_sex_diet, ['sex','diet_group'])
add_records(df_age_diet, ['age_group','diet_group'])
add_records(df_all, ['diet_group','sex','age_group'])

records_pd = pd.DataFrame(records)

# Normalize metric values to [0, 1]
scaler = MinMaxScaler()
records_pd[metrics] = scaler.fit_transform(records_pd[metrics])

# Prepare radar chart
colors = px.colors.qualitative.Plotly
fig = go.Figure()

# Add one trace per group (initially hidden)
for i, row in records_pd.iterrows():
    vals = row[metrics].tolist()
    units = [metric_units[label] for label in metric_labels]
    fig.add_trace(go.Scatterpolar(
        r=vals,
        theta=metric_labels,
        fill='toself',
        name=row['name'],
        visible='legendonly',
        line_color=colors[i % len(colors)],
        opacity=0.3,
        mode='lines+markers',
        marker=dict(size=6),
        text=[row['name']]*len(vals),
        customdata=units,
        hovertemplate=(
            'Group: %{text}<br>'
            'Metric: %{theta}<br>'
            'Value: %{r:.2f} %{customdata}<extra></extra>'
        )
    ))

# Add "Clear All" button
n = len(records_pd)
fig.update_layout(
    updatemenus=[dict(
        type='buttons',
        direction='left',
        x=0, y=1.15,
        xanchor='left', yanchor='top',
        buttons=[dict(
            label='Clear All',
            method='update',
            args=[{'visible': ['legendonly']*n + [False]}, {}]
        )]
    )]
)

# Configure layout
fig.update_layout(
    title='Environmental Metrics Radar Chart',
    title_x=0.5,
    polar=dict(
        angularaxis=dict(
            tickmode='array',
            tickvals=metric_labels,
            ticktext=metric_labels,
            rotation=90,
            direction='clockwise',
            showline=True, showticklabels=True
        ),
        radialaxis=dict(visible=True, range=[0,1])
    ),
    legend=dict(
        orientation='v',
        x=0.78, y=1,
        xanchor='left',
        title='Groups'
    ),
    margin=dict(l=50, r=200, t=80, b=50)
)

# Render to HTML
pyo.plot(fig, filename='environmental_radar_chart.html')
