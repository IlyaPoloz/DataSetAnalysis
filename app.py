import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Dynamic Multi-Dataset Dashboard",
    page_icon="📊",
    layout="wide"
)

hide_streamlit_style = """
    <style>
        /* Hide the app toolbar, main menu, and deploy button */
        .stAppToolbar, #MainMenu, .stAppDeployButton {
            display: none;
        }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- Data Loading Function ---
@st.cache_data
def load_data(csv_path):
    try:
        df = pd.read_csv(csv_path)
        # Strip extra whitespace from column names
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading data from {csv_path}: {e}")
        return None

# --- Configuration for Each Dataset ---
dataset_options = [
    "Global Cybersecurity Threats (2015-2024)",
    "Air Pollution in China",
    "Dating App User Behavior",
    "Global Video Game Sales"
]

titles_config = {
    "Global Cybersecurity Threats (2015-2024)": {
        "file": "Global_Cybersecurity_Threats_2015-2024.csv",
        "main_title": "Global Cybersecurity Threats (2015-2024) Dashboard",
        "metric_label": "Total Incidents",
        "chart1_title": "Attack Type Frequency",
        "chart2_title": "Distribution of Financial Loss",
        "chart3_title": "Incidents Over Time"
    },
    "Air Pollution in China": {
        "file": "air_pollution_china.csv",
        "main_title": "Air Pollution in China Dashboard",
        "metric_label": "Average AQI",
        "chart1_title": "Distribution of AQI",
        "chart2_title": "Pollutant Levels by Season",
        "chart3_title": "Temperature vs PM2.5"
    },
    "Dating App User Behavior": {
        "file": "dating_app_behavior_dataset.csv",
        "main_title": "Dating App Usage Behavior Dashboard",
        "metric_label": "Total Active Users",
        "chart1_title": "App Usage Distribution",
        "chart2_title": "Messages Sent by Orientation",
        "chart3_title": "Swipe-Right Ratios"
    },
    "Global Video Game Sales": {
        "file": "vgsales.csv",
        "main_title": "Video Game Sales Dashboard",
        "metric_label": "Total Global Sales",
        "chart1_title": "Top Genres by Sales",
        "chart2_title": "Sales by Region",
        "chart3_title": "Games Released Over Time"
    }
}

# --- Sidebar: Dataset Selection ---
selected_dataset = st.sidebar.selectbox("Select a dataset:", dataset_options)
config = titles_config[selected_dataset]
data = load_data(config["file"])

# --- Main Title ---
st.title(config["main_title"])

if data is not None:
    if selected_dataset == "Global Cybersecurity Threats (2015-2024)":
        data.columns = (
            data.columns.str.lower()
            .str.replace(' ', '_')
            .str.replace('(in_million_$)', 'millions', regex=False)
            .str.replace('(in_hours)', 'hours', regex=False)
        )
        
        if st.checkbox("Show Original Data Table", key="cyber_original"):
            st.dataframe(data)
        
        # --- Sidebar Filters ---
        st.sidebar.header("Filters")
        years = sorted(data['year'].unique())
        selected_years = st.sidebar.multiselect("Select Year(s):", options=years, default=years)
        if not selected_years:
            selected_years = years
        countries = sorted(data['country'].unique())
        selected_countries = st.sidebar.multiselect("Select Country(s):", options=countries, default=countries)
        if not selected_countries:
            selected_countries = countries
        attack_types = sorted(data['attack_type'].unique())
        selected_attack_types = st.sidebar.multiselect("Select Attack Type(s):", options=attack_types, default=attack_types)
        if not selected_attack_types:
            selected_attack_types = attack_types
        
        # --- Apply Filters ---
        df_filtered = data[
            (data['year'].isin(selected_years)) &
            (data['country'].isin(selected_countries)) &
            (data['attack_type'].isin(selected_attack_types))
        ]
        
        # --- Key Metrics ---
        st.header("Key Metrics (Filtered Data)")
        col1, col2, col3 = st.columns(3)
        total_incidents = df_filtered.shape[0]
        avg_loss = df_filtered['financial_loss_millions'].mean()
        avg_resolution = df_filtered['incident_resolution_time_hours'].mean()
        col1.metric("Total Incidents", f"{total_incidents:,}")
        col2.metric("Avg. Financial Loss (M$)", f"{avg_loss:.2f}")
        col3.metric("Avg. Resolution Time (Hours)", f"{avg_resolution:.1f}")
        st.markdown("---")
        
        # --- Visualizations ---
        sns.set_theme(style="whitegrid")
        col1_viz, col2_viz = st.columns(2)
        with col1_viz:
            st.subheader(config["chart1_title"])
            fig1, ax1 = plt.subplots(figsize=(8, 5))
            sns.countplot(
                y=df_filtered['attack_type'],
                order=df_filtered['attack_type'].value_counts().index,
                ax=ax1, palette='viridis'
            )
            ax1.set_xlabel('Number of Incidents')
            ax1.set_ylabel('Attack Type')
            plt.tight_layout()
            st.pyplot(fig1)
        with col2_viz:
            st.subheader(config["chart2_title"])
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            sns.histplot(
                df_filtered['financial_loss_millions'],
                kde=True, bins=15, ax=ax2, color='skyblue'
            )
            ax2.set_xlabel('Financial Loss (Million $)')
            ax2.set_ylabel('Frequency')
            plt.tight_layout()
            st.pyplot(fig2)
            
        col3_viz, col4_viz = st.columns(2)
        with col3_viz:
            st.subheader("Financial Loss by Attack Type")
            order = df_filtered.groupby('attack_type')['financial_loss_millions'].median().sort_values().index
            fig3, ax3 = plt.subplots(figsize=(8, 6))
            sns.boxplot(
                x='financial_loss_millions', y='attack_type',
                data=df_filtered, order=order, ax=ax3, palette='mako'
            )
            ax3.set_xlabel('Financial Loss (Million $)')
            ax3.set_ylabel('Attack Type')
            plt.tight_layout()
            st.pyplot(fig3)
        with col4_viz:
            st.subheader(config["chart3_title"])
            if len(selected_years) > 1:
                incident_counts = df_filtered['year'].value_counts().sort_index()
                fig4, ax4 = plt.subplots(figsize=(8, 5))
                sns.lineplot(
                    x=incident_counts.index,
                    y=incident_counts.values, marker='o', ax=ax4
                )
                ax4.set_xlabel('Year')
                ax4.set_ylabel('Number of Incidents')
                plt.tight_layout()
                st.pyplot(fig4)
            elif len(selected_years) == 1:
                st.write(f"Showing data only for {selected_years[0]}.")
                count = df_filtered['year'].value_counts().iloc[0]
                st.metric(f"Incidents in {selected_years[0]}", count)
            else:
                st.write("Select multiple years to see trend.")
    
    elif selected_dataset == "Air Pollution in China":
        if st.checkbox("Show Original Data Table", key="air_original"):
            st.dataframe(data)
        
        # --- Sidebar Filters ---
        st.sidebar.header("Filters")
        years = sorted(data['Year'].unique())
        selected_years = st.sidebar.multiselect("Select Year(s):", options=years, default=years)
        if not selected_years:
            selected_years = years
        cities = sorted(data['City'].unique())
        selected_cities = st.sidebar.multiselect("Select City(ies):", options=cities, default=cities)
        if not selected_cities:
            selected_cities = cities
        seasons = sorted(data['Season'].unique())
        selected_seasons = st.sidebar.multiselect("Select Season(s):", options=seasons, default=seasons)
        if not selected_seasons:
            selected_seasons = seasons
        
        # --- Apply Filters ---
        df_filtered = data[
            (data['Year'].isin(selected_years)) &
            (data['City'].isin(selected_cities)) &
            (data['Season'].isin(selected_seasons))
        ]
        
        # --- Key Metrics ---
        st.header("Key Metrics (Filtered Data)")
        col1, col2, col3 = st.columns(3)
        avg_aqi = df_filtered['AQI'].mean() if 'AQI' in df_filtered.columns else None
        avg_temp = df_filtered['Temperature (°C)'].mean() if 'Temperature (°C)' in df_filtered.columns else None
        avg_pm25 = df_filtered['PM2.5 (µg/m³)'].mean() if 'PM2.5 (µg/m³)' in df_filtered.columns else None
        col1.metric("Average AQI", f"{avg_aqi:.1f}" if avg_aqi else "N/A")
        col2.metric("Average Temperature (°C)", f"{avg_temp:.1f}" if avg_temp else "N/A")
        col3.metric("Average PM2.5", f"{avg_pm25:.1f}" if avg_pm25 else "N/A")
        st.markdown("---")
        
        # --- Visualizations ---
        sns.set_theme(style="whitegrid")
        col1_viz, col2_viz = st.columns(2)
        with col1_viz:
            st.subheader(config["chart1_title"])
            fig1, ax1 = plt.subplots(figsize=(8, 5))
            sns.histplot(df_filtered['AQI'], kde=True, bins=15, ax=ax1, color='salmon')
            ax1.set_xlabel('AQI')
            ax1.set_ylabel('Frequency')
            plt.tight_layout()
            st.pyplot(fig1)
        with col2_viz:
            st.subheader(config["chart2_title"])
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            sns.boxplot(x='Season', y='PM2.5 (µg/m³)', data=df_filtered, ax=ax2, palette='coolwarm')
            ax2.set_xlabel('Season')
            ax2.set_ylabel('PM2.5 (µg/m³)')
            plt.tight_layout()
            st.pyplot(fig2)
        
        st.subheader(config["chart3_title"])
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        sns.scatterplot(x='Temperature (°C)', y='PM2.5 (µg/m³)', data=df_filtered, ax=ax3, color='green')
        ax3.set_xlabel('Temperature (°C)')
        ax3.set_ylabel('PM2.5 (µg/m³)')
        plt.tight_layout()
        st.pyplot(fig3)

    
    elif selected_dataset == "Dating App User Behavior":
        if st.checkbox("Show Original Data Table", key="dating_original"):
            st.dataframe(data)
        
        # --- Sidebar Filters ---
        st.sidebar.header("Filters")
        orientations = sorted(data['sexual_orientation'].unique())
        selected_orientations = st.sidebar.multiselect("Select Sexual Orientation:", options=orientations, default=orientations)
        if not selected_orientations:
            selected_orientations = orientations
        locations = sorted(data['location_type'].unique())
        selected_locations = st.sidebar.multiselect("Select Location Type:", options=locations, default=locations)
        if not selected_locations:
            selected_locations = locations
        
        # --- Apply Filters ---
        df_filtered = data[
            (data['sexual_orientation'].isin(selected_orientations)) &
            (data['location_type'].isin(selected_locations))
        ]
        
        # --- Key Metrics ---
        st.header("Key Metrics (Filtered Data)")
        col1, col2, col3 = st.columns(3)
        total_users = df_filtered.shape[0]
        avg_usage = df_filtered['app_usage_time_min'].mean()
        avg_messages = df_filtered['message_sent_count'].mean()
        col1.metric("Total Active Users", f"{total_users}")
        col2.metric("Avg. App Usage Time (min)", f"{avg_usage:.1f}")
        col3.metric("Avg. Messages Sent", f"{avg_messages:.1f}")
        st.markdown("---")
        
        # --- Visualizations ---
        sns.set_theme(style="whitegrid")
        col1_viz, col2_viz = st.columns(2)
        with col1_viz:
            st.subheader(config["chart1_title"])
            fig1, ax1 = plt.subplots(figsize=(8, 5))
            sns.histplot(df_filtered['app_usage_time_min'], kde=True, bins=15, ax=ax1, color='purple')
            ax1.set_xlabel('App Usage Time (min)')
            ax1.set_ylabel('Frequency')
            plt.tight_layout()
            st.pyplot(fig1)
        with col2_viz:
            st.subheader(config["chart2_title"])
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            sns.boxplot(x='sexual_orientation', y='message_sent_count', data=df_filtered, ax=ax2, palette='Set2')
            ax2.set_xlabel('Sexual Orientation')
            ax2.set_ylabel('Messages Sent')
            plt.tight_layout()
            st.pyplot(fig2)
            
        st.subheader(config["chart3_title"])
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        sns.histplot(df_filtered['swipe_right_ratio'], kde=True, bins=15, ax=ax3, color='orange')
        ax3.set_xlabel('Swipe Right Ratio')
        ax3.set_ylabel('Frequency')
        plt.tight_layout()
        st.pyplot(fig3)

                # --- Additional Graphs for Dating App User Behavior ---

        # Graph: Distribution of Education Level
        st.subheader("User Distribution by Education Level")
        fig4, ax4 = plt.subplots(figsize=(8, 5))
        sns.countplot(
            data=df_filtered,
            x='education_level',
            order=df_filtered['education_level'].value_counts().index,
            palette='coolwarm',
            ax=ax4
        )
        ax4.set_xlabel('Education Level')
        ax4.set_ylabel('Number of Users')
        # Rotate x-axis labels to avoid overlapping
        ax4.set_xticklabels(ax4.get_xticklabels(), rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig4)

        # Graph: Income Bracket vs Likes Received
                # --- Revised Diagram: Income Bracket vs Likes Received (Mean with Error Bars) ---
        st.subheader("Income Bracket vs Likes Received (Mean Likes ± SD)")
        fig5, ax5 = plt.subplots(figsize=(8, 5))
        # Use Seaborn's barplot to compute and plot the mean likes_received for each income bracket.
        # Error bars display the standard deviation.
        sns.barplot(data=df_filtered, x='income_bracket', y='likes_received', ci='sd', ax=ax5)
        ax5.set_xlabel('Income Bracket')
        ax5.set_ylabel('Average Likes Received')
        ax5.set_title('Average Likes Received by Income Bracket')
        # Rotate x-axis labels to reduce overlapping text if necessary.
        ax5.set_xticklabels(ax5.get_xticklabels(), rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig5)
    
    elif selected_dataset == "Global Video Game Sales":
        if st.checkbox("Show Original Data Table", key="vgsales_original"):
            st.dataframe(data)
        
        # --- Sidebar Filters ---
        st.sidebar.header("Filters")
        years = sorted(data['Year'].dropna().unique().astype(int))
        selected_years = st.sidebar.multiselect("Select Year(s):", options=years, default=years)
        if not selected_years:
            selected_years = years
        genres = sorted(data['Genre'].unique())
        selected_genres = st.sidebar.multiselect("Select Genre(s):", options=genres, default=genres)
        if not selected_genres:
            selected_genres = genres
        platforms = sorted(data['Platform'].unique())
        selected_platforms = st.sidebar.multiselect("Select Platform(s):", options=platforms, default=platforms)
        if not selected_platforms:
            selected_platforms = platforms
        
        # --- Apply Filters ---
        df_filtered = data[
            (data['Year'].isin(selected_years)) &
            (data['Genre'].isin(selected_genres)) &
            (data['Platform'].isin(selected_platforms))
        ]
        
        # --- Key Metrics ---
        st.header("Key Metrics (Filtered Data)")
        col1, col2 = st.columns(2)
        total_sales = df_filtered['Global_Sales'].sum()
        avg_sales = df_filtered['Global_Sales'].mean()
        col1.metric("Total Global Sales (M)", f"{total_sales:.2f}")
        col2.metric("Avg. Sales per Game (M)", f"{avg_sales:.2f}")
        st.markdown("---")
        
        # --- Visualizations ---
        sns.set_theme(style="whitegrid")
        col1_viz, col2_viz = st.columns(2)
        with col1_viz:
            st.subheader(config["chart1_title"])
            genre_sales = df_filtered.groupby('Genre')['Global_Sales'].sum().sort_values(ascending=False)
            fig1, ax1 = plt.subplots(figsize=(8, 5))
            sns.barplot(x=genre_sales.values, y=genre_sales.index, ax=ax1, palette='viridis')
            ax1.set_xlabel('Total Global Sales (M)')
            ax1.set_ylabel('Genre')
            plt.tight_layout()
            st.pyplot(fig1)
        with col2_viz:
            st.subheader(config["chart2_title"])
            regions = ['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']
            regional_sales = df_filtered[regions].sum()
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            sns.barplot(x=regional_sales.index, y=regional_sales.values, ax=ax2, palette='pastel')
            ax2.set_xlabel('Region')
            ax2.set_ylabel('Sales (M)')
            plt.tight_layout()
            st.pyplot(fig2)
            
        st.subheader(config["chart3_title"])
        game_counts = df_filtered['Year'].value_counts().sort_index()
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        sns.lineplot(x=game_counts.index, y=game_counts.values, marker='o', ax=ax3)
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Number of Games')
        plt.tight_layout()
        st.pyplot(fig3)

        
else:
    st.error("Failed to load data.")
