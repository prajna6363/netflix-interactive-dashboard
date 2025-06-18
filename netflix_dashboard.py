# netflix_dashboard.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Streamlit config
st.set_page_config(page_title="Netflix Explorer", layout="wide")
sns.set(style="whitegrid")

# Title
st.title("🎬 Netflix Content Explorer")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("netflix_titles.csv")
    df['date_added'] = pd.to_datetime(df['date_added'].str.strip(), errors='coerce')
    df['year_added'] = df['date_added'].dt.year
    df['month_added'] = df['date_added'].dt.month
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filter Options")
type_filter = st.sidebar.selectbox("Select Type", ["All", "Movie", "TV Show"])
country_filter = st.sidebar.text_input("Enter Country (optional)")
year_filter = st.sidebar.selectbox("Select Year Added", ["All"] + sorted(df['year_added'].dropna().unique().astype(int).tolist(), reverse=True))
genre_filter = st.sidebar.text_input("Enter Genre Keyword (optional)")

# Apply filters
filtered_df = df.copy()

if type_filter != "All":
    filtered_df = filtered_df[filtered_df['type'] == type_filter]

if country_filter:
    filtered_df = filtered_df[filtered_df['country'].fillna('').str.contains(country_filter, case=False)]

if year_filter != "All":
    filtered_df = filtered_df[filtered_df['year_added'] == int(year_filter)]

if genre_filter:
    filtered_df = filtered_df[filtered_df['listed_in'].fillna('').str.lower().str.contains(genre_filter.lower())]

# Show filtered data
st.subheader(f"📋 Filtered Data ({len(filtered_df)} results)")
st.dataframe(filtered_df[['title', 'type', 'country', 'year_added', 'listed_in']].reset_index(drop=True), use_container_width=True)

# Download button
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("💾 Download CSV", data=csv, file_name='filtered_netflix_data.csv', mime='text/csv')

# 📊 Plots
st.markdown("---")
st.subheader("📈 Visual Analysis")

# 1. Type count
st.markdown("### 1️⃣ Movies vs TV Shows")
fig1, ax1 = plt.subplots()
sns.countplot(data=filtered_df, x='type', palette='coolwarm', ax=ax1)
ax1.set_title("Movies vs TV Shows")
st.pyplot(fig1)

# 2. Yearly additions
st.markdown("### 2️⃣ Content Added by Year")
fig2, ax2 = plt.subplots(figsize=(10, 4))
filtered_df['year_added'].value_counts().sort_index().plot(kind='bar', color='skyblue', ax=ax2)
ax2.set_title("Titles Added Per Year")
ax2.set_xlabel("Year")
ax2.set_ylabel("Number of Titles")
st.pyplot(fig2)

# 3. Top genres
st.markdown("### 3️⃣ Top Genres")
genres = []
filtered_df['listed_in'].dropna().apply(lambda x: genres.extend([i.strip() for i in x.split(',')]))
top_genres = pd.DataFrame(Counter(genres).most_common(10), columns=['Genre', 'Count'])

fig3, ax3 = plt.subplots()
sns.barplot(x='Count', y='Genre', data=top_genres, palette='magma', ax=ax3)
ax3.set_title("Top 10 Genres")
st.pyplot(fig3)

# 4. Top countries
st.markdown("### 4️⃣ Top Countries by Titles")
top_countries = filtered_df['country'].value_counts().head(10)

fig4, ax4 = plt.subplots()
top_countries.plot(kind='barh', color='green', ax=ax4)
ax4.set_title("Top Countries with Most Titles")
st.pyplot(fig4)

# 5. Ratings
st.markdown("### 5️⃣ Ratings Distribution")
fig5, ax5 = plt.subplots()
sns.countplot(data=filtered_df, y='rating', order=filtered_df['rating'].value_counts().index, palette='pastel', ax=ax5)
ax5.set_title("Content Ratings Distribution")
st.pyplot(fig5)
