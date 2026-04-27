import streamlit as st
import pandas as pd

st.title("Audience Sensitivity, Content Compliance & Format Preference Analysis of France Top 50 Playlist Dashboard")

# Load dataset
df = pd.read_excel("Atlantic_France.xlsx")

# --- KPI Section ---
st.subheader("Key Performance Indicators")

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

# Explicit Content Share
explicit_share = (df["is_explicit"].sum() / len(df)) * 100
col1.metric("Explicit Content Share", f"{explicit_share:.1f}%", "Audience sensitivity indicator")

# Clean Content Dominance Ratio
clean_ratio = ((len(df) - df["is_explicit"].sum()) / len(df)) * 100
col2.metric("Clean Content Dominance Ratio", f"{clean_ratio:.1f}%", "Compliance preference")

# Single vs Album Track Ratio
single_count = df[df["album_type"] == "single"].shape[0]
album_count = df[df["album_type"] == "album"].shape[0]
col3.metric("Single vs Album Track Ratio", f"{single_count}:{album_count}", "Format preference")

# Average Song Duration
avg_duration = df["duration_ms"].mean() / 60000  # convert ms to minutes
col4.metric("Average Song Duration", f"{avg_duration:.2f} min", "Structural norm")

# Album Size Impact Index
avg_tracks = df["total_tracks"].mean()
col5.metric("Album Size Impact Index", f"{avg_tracks:.1f}", "Catalog strategy insight")

# Content Acceptance Score
acceptance_score = df.loc[df["is_explicit"] == 0, "popularity"].mean()
col6.metric("Content Acceptance Score", f"{acceptance_score:.2f}", "Rank-aligned preference")


# --- Sidebar Filters ---
st.sidebar.header("Filters")

# Date range selector
min_date, max_date = df["date"].min(), df["date"].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])
if len(date_range) == 2:
    start_date, end_date = date_range
    df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]

# Rank tier filter (Top 10 / 25 / 50)
rank_tier = st.sidebar.selectbox("Select Rank Tier", ["Top 10", "Top 25", "Top 50"])
if rank_tier == "Top 10":
    df = df[df["position"] <= 10]
elif rank_tier == "Top 25":
    df = df[df["position"] <= 25]
else:
    df = df[df["position"] <= 50]

# Explicit content toggle
explicit_toggle = st.sidebar.radio("Explicit Content", ["All", "Explicit Only", "Clean Only"])
if explicit_toggle == "Explicit Only":
    df = df[df["is_explicit"] == 1]
elif explicit_toggle == "Clean Only":
    df = df[df["is_explicit"] == 0]

# Album type filter
album_types = df["album_type"].unique()
selected_album_type = st.sidebar.multiselect("Select Album Type", options=album_types, default=album_types)
df = df[df["album_type"].isin(selected_album_type)]


# --- Data Validation & Preparation ---

# 1. Ensure 50 entries per day
entries_per_day = df.groupby("date")["position"].count()
invalid_days = entries_per_day[entries_per_day != 50]
if not invalid_days.empty:
    st.warning(f"⚠️ Data quality issue: {len(invalid_days)} day(s) have fewer than 50 entries.")

# 2. Convert duration from milliseconds to minutes
df["duration_min"] = df["duration_ms"] / 60000

# 3. Standardize album type labels
df["album_type"] = df["album_type"].str.lower().str.strip()
df["album_type"] = df["album_type"].replace({
    "single": "single",
    "album": "album",
    "ep": "album"   # treat EPs as albums for consistency
})

# 4. Validate explicit flag consistency
if not df["is_explicit"].isin([0,1]).all():
    st.warning("⚠️ Data quality issue: 'is_explicit' column has invalid values.")


import matplotlib.pyplot as plt

st.markdown("### Explicit vs Clean Share")
labels = ["Clean", "Explicit"]
sizes = [df[df["is_explicit"] == 0].shape[0], df[df["is_explicit"] == 1].shape[0]]
colors = ["#4CAF50", "#E74C3C"]

fig1, ax1 = plt.subplots()
ax1.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
ax1.axis("equal")  # Equal aspect ratio ensures pie is circular
st.pyplot(fig1)

st.markdown("### Rank‑wise Explicit Content Distribution")
rank_data = df.groupby(["position", "is_explicit"]).size().unstack(fill_value=0)
st.bar_chart(rank_data)

st.markdown("### Popularity Comparison: Explicit vs Clean Tracks")
fig2, ax2 = plt.subplots()
df.boxplot(column="popularity", by="is_explicit", ax=ax2)
ax2.set_xticklabels(["Clean", "Explicit"])
ax2.set_title("Popularity Comparison")
ax2.set_ylabel("Popularity Score")
st.pyplot(fig2)



import matplotlib.pyplot as plt

st.subheader("Release Format Preference Analysis")

# 1. Single vs Album Track Representation (Bar Chart)
st.markdown("### Single vs Album Track Representation")
format_counts = df["album_type"].value_counts()
st.bar_chart(format_counts)

# 2. Rank-based Format Comparison (Stacked Bar Chart)
st.markdown("### Rank-based Format Comparison")
rank_format = df.groupby(["position", "album_type"]).size().unstack(fill_value=0)

fig1, ax1 = plt.subplots(figsize=(8,4))
rank_format.plot(kind="bar", stacked=True, ax=ax1, color=["#1f77b4", "#ff7f0e"])
ax1.set_xlabel("Playlist Rank")
ax1.set_ylabel("Number of Songs")
ax1.set_title("Rank-based Format Comparison")
st.pyplot(fig1)

# 3. Popularity Differences by Album Type (Attractive Alternative)
st.markdown("### Popularity Differences by Album Type")

# Calculate average popularity per album type
avg_popularity = df.groupby("album_type")["popularity"].mean().reset_index()

fig2, ax2 = plt.subplots(figsize=(6,4))
bars = ax2.bar(avg_popularity["album_type"], avg_popularity["popularity"],
               color=["#1f77b4", "#ff7f0e"], alpha=0.8)

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, height,
             f"{height:.1f}", ha="center", va="bottom", fontsize=10, fontweight="bold")

ax2.set_ylabel("Average Popularity Score")
ax2.set_title("Average Popularity by Album Type")
st.pyplot(fig2)


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.subheader("Album Structure Impact Analysis")

# 1. Album Size Distribution (Horizontal Histogram with styling)
st.markdown("### Album Size Distribution")
fig1, ax1 = plt.subplots(figsize=(7,4))
ax1.hist(df["total_tracks"], bins=12, orientation="horizontal",
         color="#3498db", alpha=0.85, edgecolor="white")
ax1.set_ylabel("Number of Tracks per Album")
ax1.set_xlabel("Number of Albums")
ax1.set_title("Distribution of Album Sizes", fontsize=12, fontweight="bold")
ax1.grid(axis="x", linestyle="--", alpha=0.7)
st.pyplot(fig1)

# Replace Bubble Chart with Hexbin Plot
st.markdown("### Album Size vs Track Popularity (Hexbin Plot)")
fig4, ax4 = plt.subplots(figsize=(7,5))
hb2 = ax4.hexbin(df["total_tracks"], df["popularity"], gridsize=25, cmap="plasma", mincnt=1)
ax4.set_xlabel("Album Size (Total Tracks)")
ax4.set_ylabel("Track Popularity")
ax4.set_title("Album Size vs Track Popularity (Hexbin)", fontsize=12, fontweight="bold")
fig4.colorbar(hb2, ax=ax4, label="Number of Songs")
st.pyplot(fig4)

# 3. Album Dilution vs Concentration Effects (Radar Chart)
st.markdown("### Album Dilution vs Concentration Effects")
df["album_size_group"] = pd.cut(df["total_tracks"],
                                bins=[0,10,20,100],
                                labels=["Small (≤10)", "Medium (11-20)", "Large (>20)"])
avg_popularity = df.groupby("album_size_group")["popularity"].mean()

labels = avg_popularity.index.astype(str)
values = avg_popularity.values
angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
values = np.concatenate((values,[values[0]]))  # close the loop
angles += angles[:1]

fig3, ax3 = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
ax3.plot(angles, values, "o-", linewidth=2, color="red")
ax3.fill(angles, values, alpha=0.25, color="red")
ax3.set_xticks(angles[:-1])
ax3.set_xticklabels(labels)
ax3.set_title("Dilution vs Concentration Effects", fontsize=12, fontweight="bold")
st.pyplot(fig3)


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.subheader("Song Duration Preference Analysis")

# ✅ Step 1: Create duration_bucket column
df["duration_bucket"] = pd.cut(
    df["duration_ms"]/60000,   # convert ms → minutes
    bins=[0,3,5,10],
    labels=["Short (≤3 min)", "Medium (3-5 min)", "Long (>5 min)"]
)

# 1. Duration Distribution Across Playlist (Smooth Curve)
st.markdown("### Duration Distribution Across Playlist")
counts, bins = np.histogram(df["duration_ms"]/60000, bins=20)
fig1, ax1 = plt.subplots(figsize=(7,4))
ax1.plot(bins[:-1], counts, color="#3498db", linewidth=2, marker="o")
ax1.set_xlabel("Song Duration (minutes)")
ax1.set_ylabel("Number of Songs")
ax1.set_title("Duration Distribution Curve", fontsize=12, fontweight="bold")
ax1.grid(linestyle="--", alpha=0.7)
st.pyplot(fig1)

# 2. Duration Buckets (Lollipop Chart – avoids repetition)
st.markdown("### Duration Buckets (Short, Medium, Long)")
bucket_counts = df["duration_bucket"].value_counts().sort_index()

fig2, ax2 = plt.subplots(figsize=(7,4))
colors = ["#2ecc71","#f1c40f","#e74c3c"]

for i, (label, val) in enumerate(bucket_counts.items()):
    ax2.plot([i,i],[0,val], color=colors[i], linewidth=3)
    ax2.scatter(i, val, s=200, color=colors[i], edgecolor="black", zorder=3)
    ax2.text(i, val+0.5, f"{val}", ha="center", fontsize=10, fontweight="bold")

ax2.set_xticks(range(len(bucket_counts)))
ax2.set_xticklabels(bucket_counts.index)
ax2.set_ylabel("Number of Songs")
ax2.set_title("Song Duration Buckets (Lollipop Chart)", fontsize=12, fontweight="bold")
ax2.grid(axis="y", linestyle="--", alpha=0.7)
st.pyplot(fig2)

# 3. Duration vs Popularity and Rank Alignment (Hexbin Plot – avoids overlap)
st.markdown("### Duration vs Popularity and Rank Alignment")
fig3, ax3 = plt.subplots(figsize=(7,5))
hb = ax3.hexbin(df["duration_ms"]/60000, df["popularity"], gridsize=25, cmap="viridis", mincnt=1)
ax3.set_xlabel("Song Duration (minutes)")
ax3.set_ylabel("Popularity Score")
ax3.set_title("Duration vs Popularity (Hexbin)", fontsize=12, fontweight="bold")
fig3.colorbar(hb, ax=ax3, label="Number of Songs")
st.pyplot(fig3)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.subheader("Content Attribute Concentration Analysis")

# ✅ Step 1: Attribute Density Across Top 10, 25, 50 (Heatmap using is_explicit)
st.markdown("### Attribute Density Across Playlist Segments")

segments = {"Top 10": df[df["position"]<=10],
            "Top 25": df[df["position"]<=25],
            "Top 50": df[df["position"]<=50]}

density_data = {}
for seg, subset in segments.items():
    density_data[seg] = subset["is_explicit"].value_counts(normalize=True)

density_df = pd.DataFrame(density_data).fillna(0)

fig1, ax1 = plt.subplots(figsize=(6,4))
im = ax1.imshow(density_df.values, cmap="coolwarm")

ax1.set_xticks(np.arange(len(density_df.columns)))
ax1.set_xticklabels(density_df.columns)
ax1.set_yticks(np.arange(len(density_df.index)))
ax1.set_yticklabels(density_df.index)
plt.setp(ax1.get_xticklabels(), rotation=45, ha="right")

for i in range(len(density_df.index)):
    for j in range(len(density_df.columns)):
        ax1.text(j, i, f"{density_df.iloc[i,j]*100:.1f}%",
                 ha="center", va="center", color="white", fontsize=9)

ax1.set_title("Explicit vs Clean Density Across Segments", fontsize=12, fontweight="bold")
fig1.colorbar(im, ax=ax1)
st.pyplot(fig1)

# ✅ Step 2: Preferred Content Profiles (Donut Chart using album_type + is_explicit)
st.markdown("### Preferred Content Profiles (France Top 50)")

profile_counts = {
    "Singles": (df["album_type"]=="single").sum(),
    "Albums": (df["album_type"]!="single").sum(),
    "Explicit": df["is_explicit"].sum(),
    "Clean": (df["is_explicit"]==0).sum()
}

labels = list(profile_counts.keys())
sizes = list(profile_counts.values())
colors = ["#2ecc71","#3498db","#e74c3c","#f1c40f"]

fig2, ax2 = plt.subplots(figsize=(6,6))
wedges, texts, autotexts = ax2.pie(sizes, labels=labels, autopct="%1.1f%%",
                                   startangle=90, colors=colors, pctdistance=0.85)
centre_circle = plt.Circle((0,0),0.70,fc="white")
fig2.gca().add_artist(centre_circle)
ax2.set_title("Preferred Content Profiles – France", fontsize=12, fontweight="bold")
st.pyplot(fig2)

# ✅ Step 3: Attribute Concentration Treemap (using artist)
st.markdown("### Top Artist Concentration Treemap")

artist_counts = df["artist"].value_counts().head(10)

fig3, ax3 = plt.subplots(figsize=(8,6))
total = sum(artist_counts)
x, y = 0, 0
width = 1
height = 1

for i, (label, val) in enumerate(artist_counts.items()):
    rect_width = width * (val/total)
    ax3.add_patch(plt.Rectangle((x,y), rect_width, height, facecolor=plt.cm.tab20(i)))
    # ✅ Smaller font size + vertical rotation
    ax3.text(x+rect_width/2, y+height/2, f"{label}\n{val}",
             ha="center", va="center", fontsize=8, rotation=90, color="white")
    x += rect_width

ax3.set_xlim(0,1)
ax3.set_ylim(0,1)
ax3.axis("off")
ax3.set_title("Top Artist Concentration Treemap", fontsize=12, fontweight="bold")
st.pyplot(fig3)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.subheader("Trend Analysis")

# ✅ Explicit vs Clean Trend (Stacked Area Chart)
st.markdown("### Explicit vs Clean Songs Over Time")
trend_data = df.groupby(["date","is_explicit"]).size().unstack(fill_value=0)

fig1, ax1 = plt.subplots(figsize=(8,4))
ax1.stackplot(trend_data.index,
              trend_data[False],  # clean songs
              trend_data[True],   # explicit songs
              labels=["Clean","Explicit"],
              colors=["#2ecc71","#e74c3c"],
              alpha=0.7)
ax1.set_xlabel("Date")
ax1.set_ylabel("Number of Songs")
ax1.set_title("Explicit vs Clean Content Trend", fontsize=12, fontweight="bold")
ax1.legend(loc="upper left")
ax1.grid(linestyle="--", alpha=0.6)
st.pyplot(fig1)

# ✅ Average Duration Trend (Rolling Smooth Line)
st.markdown("### Average Song Duration Over Time")
duration_trend = df.groupby("date")["duration_ms"].mean()/60000
rolling_duration = duration_trend.rolling(window=5).mean()

fig2, ax2 = plt.subplots(figsize=(8,4))
ax2.plot(duration_trend.index, duration_trend.values,
         color="#95a5a6", alpha=0.5, linewidth=1, label="Daily Avg")
ax2.plot(rolling_duration.index, rolling_duration.values,
         color="#3498db", linewidth=2, label="5-Day Rolling Avg")
ax2.set_xlabel("Date")
ax2.set_ylabel("Avg Duration (minutes)")
ax2.set_title("Average Song Duration Trend", fontsize=12, fontweight="bold")
ax2.legend()
ax2.grid(linestyle="--", alpha=0.6)
st.pyplot(fig2)

# ✅ Popularity Trend (Scatter + Regression Line)
st.markdown("### Average Popularity Trend Over Time")
popularity_trend = df.groupby("date")["popularity"].mean()

fig3, ax3 = plt.subplots(figsize=(8,4))
ax3.scatter(popularity_trend.index, popularity_trend.values,
            color="#f39c12", s=30, alpha=0.7, label="Daily Avg")

# regression line
z = np.polyfit(range(len(popularity_trend)), popularity_trend.values, 1)
p = np.poly1d(z)
ax3.plot(popularity_trend.index, p(range(len(popularity_trend))),
         color="#e74c3c", linewidth=2, label="Trendline")

ax3.set_xlabel("Date")
ax3.set_ylabel("Avg Popularity Score")
ax3.set_title("Average Popularity Trend", fontsize=12, fontweight="bold")
ax3.legend()
ax3.grid(linestyle="--", alpha=0.6)
st.pyplot(fig3)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.subheader("Correlation Analysis")

# ✅ Select numeric columns relevant for analysis
numeric_cols = ["popularity", "duration_ms", "total_tracks", "position"]
corr_matrix = df[numeric_cols].corr()

# ✅ Heatmap with Matplotlib
fig, ax = plt.subplots(figsize=(6,5))
cax = ax.matshow(corr_matrix, cmap="coolwarm")

# Add colorbar
fig.colorbar(cax)

# Set ticks
ax.set_xticks(range(len(corr_matrix.columns)))
ax.set_yticks(range(len(corr_matrix.columns)))
ax.set_xticklabels(corr_matrix.columns, rotation=45, ha="left")
ax.set_yticklabels(corr_matrix.columns)

# Annotate correlation values
for i in range(len(corr_matrix.columns)):
    for j in range(len(corr_matrix.columns)):
        ax.text(j, i, f"{corr_matrix.iloc[i,j]:.2f}",
                ha="center", va="center", color="white", fontsize=9)

ax.set_title("Correlation Heatmap of Key Attributes", fontsize=12, fontweight="bold")
st.pyplot(fig)


st.markdown("### Song Duration Distribution")
fig, ax = plt.subplots(figsize=(8,4))
ax.hist(df["duration_ms"]/60000, bins=20, color="#3498db", alpha=0.7, edgecolor="black")
ax.set_xlabel("Song Duration (minutes)")
ax.set_ylabel("Number of Songs")
ax.set_title("Song Duration Histogram", fontsize=12, fontweight="bold")
st.pyplot(fig)


st.markdown("### Rank-Tier Attribute Comparison")

tiers = {"Top 10": df[df["position"]<=10],
         "Top 25": df[df["position"]<=25],
         "Top 50": df[df["position"]<=50]}

tier_summary = {tier: {"Avg Duration (min)": subset["duration_ms"].mean()/60000,
                       "Avg Popularity": subset["popularity"].mean()}
                for tier, subset in tiers.items()}

for tier, stats in tier_summary.items():
    st.markdown(f"- **{tier}** → Avg Duration: {stats['Avg Duration (min)']:.2f} min, Avg Popularity: {stats['Avg Popularity']:.1f}")



st.subheader("Forecasting Analysis")

# ✅ Forecasting Popularity with Moving Average + Regression
popularity_trend = df.groupby("date")["popularity"].mean()

# Moving average (7-day window)
moving_avg = popularity_trend.rolling(window=7).mean()

fig, ax = plt.subplots(figsize=(8,4))
ax.plot(popularity_trend.index, popularity_trend.values,
        color="#95a5a6", alpha=0.5, linewidth=1, label="Daily Avg")
ax.plot(moving_avg.index, moving_avg.values,
        color="#3498db", linewidth=2, label="7-Day Moving Avg")

# Regression forecast
z = np.polyfit(range(len(popularity_trend)), popularity_trend.values, 1)
p = np.poly1d(z)
ax.plot(popularity_trend.index, p(range(len(popularity_trend))),
        color="#e74c3c", linewidth=2, linestyle="--", label="Forecast Trendline")

ax.set_xlabel("Date")
ax.set_ylabel("Avg Popularity Score")
ax.set_title("Popularity Forecasting", fontsize=12, fontweight="bold")
ax.legend()
ax.grid(linestyle="--", alpha=0.6)
st.pyplot(fig)


st.subheader("Recommendations & Insights")

# Build recommendations dynamically from your data
explicit_share = df["is_explicit"].mean() * 100
avg_duration = (df["duration_ms"]/60000).mean()
single_share = (df["album_type"]=="single").mean() * 100

recommendations = []

# Explicit content preference
if explicit_share < 50:
    recommendations.append("Clean content dominates the France Top 50, suggesting that non-explicit songs are more likely to perform well.")

else:
    recommendations.append("Explicit content has a strong presence, indicating that edgy tracks are resonating with audiences.")

# Duration trend
if avg_duration < 3.5:
    recommendations.append("Shorter songs (under ~3.5 minutes) are trending higher, which aligns with global streaming behavior favoring quick, repeatable tracks.")
else:
    recommendations.append("Longer songs are still holding ground, but shorter tracks may gain more traction in future playlists.")

# Album type preference
if single_share > 60:
    recommendations.append("Singles dominate the Top 50, showing that standalone releases are more effective than full albums for chart success.")
else:
    recommendations.append("Albums contribute significantly, suggesting that bundled releases can still capture audience attention.")

# Popularity insight
avg_popularity = df["popularity"].mean()
recommendations.append(f"Average popularity score across the Top 50 is {avg_popularity:.1f}, indicating overall playlist strength and audience engagement.")

# Display recommendations
for rec in recommendations:
    st.markdown(f"- {rec}")
