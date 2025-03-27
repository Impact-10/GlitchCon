import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load Data
df = pd.read_csv("fd_rates_20_years.csv")
df["Date"] = pd.to_datetime(df["Date"])
df["Year"] = df["Date"].dt.year

# Filter for selected banks & recent years
selected_banks = ["ICICI Bank", "HDFC Bank", "SBI", "Kotak Mahindra Bank"]
df_filtered = df[(df["Year"] >= 2019) & (df["Bank"].isin(selected_banks))]

df_pivot = df_filtered.pivot_table(index="Year", columns="Bank", values="FD Rate 1Y (%)", aggfunc='mean')

# Create Line Chart
fig_line = px.line(df_filtered, x="Year", y="FD Rate 1Y (%)", color="Bank",
                    markers=True, title="FD Rates Over Time")
fig_line.show()

# Create Heatmap
fig_heatmap = go.Figure(data=go.Heatmap(
    z=df_pivot.values,
    x=df_pivot.columns,
    y=df_pivot.index,
    colorscale="Viridis"
))
fig_heatmap.update_layout(title="FD Rate Heatmap")
fig_heatmap.show()

# Create Bar Chart
fig_bar = px.bar(df_filtered, x="Year", y="FD Rate 1Y (%)", color="Bank",
                  barmode="group", title="Year-wise FD Rates")
fig_bar.show()

# Export charts as HTML
fig_line.write_html("line_chart.html")
fig_heatmap.write_html("heatmap.html")
fig_bar.write_html("bar_chart.html")

print("Interactive charts generated successfully!")
