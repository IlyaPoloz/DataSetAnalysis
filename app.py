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
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading data from {csv_path}: {e}")
        return None

# --- Configuration for Each Dataset ---
dataset_options = [
    "Global Video Game Sales",
    "Mikrouzņēmumu nodokļa maksātāji",
    "How Couples Meet and Stay Together",
    "Global EV Data Explorer"
]

titles_config = {
    "Global Video Game Sales": {
        "file": "vgsales.csv",
        "main_title": "Video Game Sales Dashboard",
        "metric_label": "Total Global Sales",
        "chart1_title": "Top Genres by Sales",
        "chart2_title": "Sales by Region",
        "chart3_title": "Games Released Over Time"
    },
    "Mikrouzņēmumu nodokļa maksātāji": {
        "file": "pdb_munmaksataji_odata.csv",
        "main_title": "Mikrouzņēmumu Nodokļa Maksātāju Dashboard",
        "metric_label": "Total Taxpayers",
        "chart1_title": "Distribution of Active vs Inactive Taxpayers",
        "chart2_title": "Registrations Over Time",
        "chart3_title": "Deregistrations Over Time"
    },
    "How Couples Meet and Stay Together": {
        "file": "HCMST_ver_3.04.csv",
        "main_title": "How Couples Meet and Stay Together Dashboard",
        "metric_label": "Total Couples",
        "chart1_title": "Distribution of Meeting Methods",
        "chart2_title": "Relationship Quality by Meeting Method",
        "chart3_title": "Relationship Duration Over Time"
    },
    "Global EV Data Explorer": {
        "file": "IEA-EV-dataEV salesHistoricalCars.csv",
        "main_title": "Global EV Data Explorer Dashboard",
        "metric_label": "Total EV Sales",
        "chart1_title": "EV Sales Over Time by Powertrain",
        "chart2_title": "EV Sales Share by Region",
        "chart3_title": "EV Stock Share Distribution"
    }
}

# --- Sidebar: Dataset Selection ---
selected_dataset = st.sidebar.selectbox("Select a dataset:", dataset_options)
config = titles_config[selected_dataset]
data = load_data(config["file"])

# --- Main Title ---
st.title(config["main_title"])

if data is not None:
    if selected_dataset == "Global Video Game Sales":
        data.columns = (
            data.columns.str.lower()
            .str.replace(' ', '_')
        )
        
        if st.checkbox("Show Original Data Table", key="vgsales_original"):
            st.dataframe(data)
        
        st.sidebar.header("Filters")
        
        years = sorted(data['year'].dropna().astype(int).unique())
        selected_years = st.sidebar.multiselect("Select Year(s):", options=years, default=years)
        if not selected_years:
            selected_years = years
        
        genres = sorted(data['genre'].dropna().unique())
        selected_genres = st.sidebar.multiselect("Select Genre(s):", options=genres, default=genres)
        if not selected_genres:
            selected_genres = genres
        
        top_publishers = data.groupby('publisher')['global_sales'].sum().nlargest(10).index.tolist()
        publishers = sorted(list(set(top_publishers + ['Others'])))
        data['publisher_filtered'] = data['publisher'].apply(lambda x: x if x in top_publishers else 'Others')
        selected_publishers = st.sidebar.multiselect("Select Publisher(s):", options=publishers, default=publishers)
        if not selected_publishers:
            selected_publishers = publishers
        
        # --- Apply Filters ---
        df_filtered = data[
            (data['year'].isin(selected_years)) &
            (data['genre'].isin(selected_genres)) &
            (data['publisher_filtered'].isin(selected_publishers))
        ]
        
        # --- Key Metrics ---
        st.header("Key Metrics (Filtered Data)")
        col1, col2, col3 = st.columns(3)
        total_sales = df_filtered['global_sales'].sum()
        avg_sales_per_game = df_filtered['global_sales'].mean()
        total_games = df_filtered.shape[0]
        col1.metric("Total Global Sales (M)", f"{total_sales:,.2f}")
        col2.metric("Avg. Sales per Game (M)", f"{avg_sales_per_game:.2f}")
        col3.metric("Total Games", f"{total_games:,}")
        st.markdown("---")
        
        # --- Visualizations ---
        sns.set_theme(style="whitegrid")
        
        # Chart 1: Top Genres by Sales (Bar Plot)
        col1_viz, col2_viz = st.columns(2)
        with col1_viz:
            st.subheader(config["chart1_title"])
            genre_sales = df_filtered.groupby('genre')['global_sales'].sum().sort_values(ascending=False)
            fig1, ax1 = plt.subplots(figsize=(8, 5))
            sns.barplot(
                x=genre_sales.values,
                y=genre_sales.index,
                ax=ax1, palette='viridis'
            )
            ax1.set_xlabel('Total Global Sales (Million $)')
            ax1.set_ylabel('Genre')
            plt.tight_layout()
            st.pyplot(fig1)
        
        # Chart 2: Sales by Region (Stacked Bar Plot)
        with col2_viz:
            st.subheader(config["chart2_title"])
            region_sales = df_filtered[['na_sales', 'eu_sales', 'jp_sales', 'other_sales']].sum()
            region_sales_df = pd.DataFrame({
                'Region': ['NA', 'EU', 'JP', 'Other'],
                'Sales': region_sales.values
            })
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            sns.barplot(
                x='Sales',
                y='Region',
                data=region_sales_df,
                ax=ax2, palette='mako'
            )
            ax2.set_xlabel('Total Sales (Million $)')
            ax2.set_ylabel('Region')
            plt.tight_layout()
            st.pyplot(fig2)
        
        # Chart 3: Games Released Over Time (Line Plot)
        col3_viz, col4_viz = st.columns(2)
        with col3_viz:
            st.subheader(config["chart3_title"])
            if len(selected_years) > 1:
                games_per_year = df_filtered['year'].value_counts().sort_index()
                fig3, ax3 = plt.subplots(figsize=(8, 5))
                sns.lineplot(
                    x=games_per_year.index,
                    y=games_per_year.values,
                    marker='o', ax=ax3
                )
                ax3.set_xlabel('Year')
                ax3.set_ylabel('Number of Games Released')
                plt.tight_layout()
                st.pyplot(fig3)
            elif len(selected_years) == 1:
                st.write(f"Showing data only for {selected_years[0]}.")
                count = df_filtered['year'].value_counts().iloc[0]
                st.metric(f"Games Released in {selected_years[0]}", count)
            else:
                st.write("Select multiple years to see trend.")
        
        # Chart 4: Top Publishers by Sales (Bar Plot)
        with col4_viz:
            st.subheader("Top Publishers by Sales")
            publisher_sales = df_filtered.groupby('publisher_filtered')['global_sales'].sum().sort_values(ascending=False)
            fig4, ax4 = plt.subplots(figsize=(8, 5))
            sns.barplot(
                x=publisher_sales.values,
                y=publisher_sales.index,
                ax=ax4, palette='rocket'
            )
            ax4.set_xlabel('Total Global Sales (Million $)')
            ax4.set_ylabel('Publisher')
            plt.tight_layout()
            st.pyplot(fig4)
    elif selected_dataset == "Mikrouzņēmumu nodokļa maksātāji":
        data.columns = (
            data.columns.str.lower()
            .str.replace(' ', '_')
        )
        
        data['registrets'] = data['registrets'].str.strip()
        data['izslegts'] = data['izslegts'].str.strip()
        data['registrets'] = pd.to_datetime(data['registrets'], format='%d.%m.%Y', errors='coerce')
        data['izslegts'] = pd.to_datetime(data['izslegts'], format='%d.%m.%Y', errors='coerce')
        
        data['registration_year'] = data['registrets'].dt.year
        data['deregistration_year'] = data['izslegts'].dt.year
        
        if st.checkbox("Show Original Data Table", key="mikro_original"):
            st.dataframe(data)
        
        st.sidebar.header("Filters")
        
        statuses = sorted(data['aktivs'].dropna().unique())
        selected_statuses = st.sidebar.multiselect("Select Status:", options=statuses, default=statuses)
        if not selected_statuses:
            selected_statuses = statuses
        
        reg_years = sorted(data['registration_year'].dropna().astype(int).unique())
        selected_reg_years = st.sidebar.multiselect("Select Registration Year(s):", options=reg_years, default=reg_years)
        if not selected_reg_years:
            selected_reg_years = reg_years
        
        dereg_years = sorted(data['deregistration_year'].dropna().astype(int).unique())
        selected_dereg_years = st.sidebar.multiselect("Select Deregistration Year(s):", options=dereg_years, default=dereg_years)
        if not selected_dereg_years:
            selected_dereg_years = dereg_years
        
        # --- Apply Filters ---
        df_filtered = data[
            (data['aktivs'].isin(selected_statuses)) &
            (data['registration_year'].isin(selected_reg_years))
        ]
        if 'nav' in selected_statuses:
            df_filtered = df_filtered[
                (df_filtered['aktivs'] == 'ir') |
                ((df_filtered['aktivs'] == 'nav') & (df_filtered['deregistration_year'].isin(selected_dereg_years)))
            ]
        
        # --- Key Metrics ---
        st.header("Key Metrics (Filtered Data)")
        col1, col2, col3 = st.columns(3)
        total_taxpayers = df_filtered.shape[0]
        active_taxpayers = df_filtered[df_filtered['aktivs'] == 'ir'].shape[0]
        inactive_taxpayers = df_filtered[df_filtered['aktivs'] == 'nav'].shape[0]
        col1.metric("Total Taxpayers", f"{total_taxpayers:,}")
        col2.metric("Active Taxpayers", f"{active_taxpayers:,}")
        col3.metric("Inactive Taxpayers", f"{inactive_taxpayers:,}")
        st.markdown("---")
        
        # --- Visualizations ---
        sns.set_theme(style="whitegrid")
        
        # Chart 1: Distribution of Active vs Inactive Taxpayers (Pie Chart)
        col1_viz, col2_viz = st.columns(2)
        with col1_viz:
            st.subheader(config["chart1_title"])
            status_counts = df_filtered['aktivs'].value_counts()
            fig1, ax1 = plt.subplots(figsize=(8, 5))
            ax1.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', colors=sns.color_palette('viridis', len(status_counts)))
            plt.tight_layout()
            st.pyplot(fig1)
        
        # Chart 2: Registrations Over Time (Line Plot)
        with col2_viz:
            st.subheader(config["chart2_title"])
            if len(selected_reg_years) > 1:
                reg_counts = df_filtered['registration_year'].value_counts().sort_index()
                fig2, ax2 = plt.subplots(figsize=(8, 5))
                sns.lineplot(
                    x=reg_counts.index,
                    y=reg_counts.values,
                    marker='o', ax=ax2
                )
                ax2.set_xlabel('Registration Year')
                ax2.set_ylabel('Number of Registrations')
                plt.tight_layout()
                st.pyplot(fig2)
            elif len(selected_reg_years) == 1:
                st.write(f"Showing data only for registration year {selected_reg_years[0]}.")
                reg_count = df_filtered['registration_year'].value_counts().iloc[0]
                st.metric(f"Registrations in {selected_reg_years[0]}", f"{reg_count:,}")
            else:
                st.write("Select multiple registration years to see trend.")
        
        # Chart 3: Deregistrations Over Time (Line Plot)
        col3_viz, col4_viz = st.columns(2)
        with col3_viz:
            st.subheader(config["chart3_title"])
            inactive_df = df_filtered[df_filtered['aktivs'] == 'nav']
            if len(selected_dereg_years) > 1 and not inactive_df.empty:
                dereg_counts = inactive_df['deregistration_year'].value_counts().sort_index()
                fig3, ax3 = plt.subplots(figsize=(8, 5))
                sns.lineplot(
                    x=dereg_counts.index,
                    y=dereg_counts.values,
                    marker='o', ax=ax3
                )
                ax3.set_xlabel('Deregistration Year')
                ax3.set_ylabel('Number of Deregistrations')
                plt.tight_layout()
                st.pyplot(fig3)
            elif len(selected_dereg_years) == 1 and not inactive_df.empty:
                st.write(f"Showing data only for deregistration year {selected_dereg_years[0]}.")
                dereg_count = inactive_df['deregistration_year'].value_counts().iloc[0]
                st.metric(f"Deregistrations in {selected_dereg_years[0]}", f"{dereg_count:,}")
            else:
                st.write("Select multiple deregistration years to see trend, or ensure inactive taxpayers are included.")
        
        # Chart 4: Duration of Activity (Histogram)
        with col4_viz:
            st.subheader("Duration of Activity (Inactive Taxpayers)")
            if not inactive_df.empty:
                inactive_df['activity_duration'] = (inactive_df['izslegts'] - inactive_df['registrets']).dt.days / 365.25  # Convert to years
                fig4, ax4 = plt.subplots(figsize=(8, 5))
                sns.histplot(
                    inactive_df['activity_duration'],
                    kde=True, bins=15, ax=ax4, color='skyblue'
                )
                ax4.set_xlabel('Duration of Activity (Years)')
                ax4.set_ylabel('Frequency')
                plt.tight_layout()
                st.pyplot(fig4)
            else:
                st.write("No inactive taxpayers in the filtered data to show duration.")
    elif selected_dataset == "How Couples Meet and Stay Together":
        if st.checkbox("Show Original Data Table", key="hcmst_original"):
            st.dataframe(data)
        data.columns = data.columns.str.strip()
        
        # --- Sidebar Filters ---
        st.sidebar.header("Filters")
        meeting_methods = data['q24_met_online'].dropna().unique().tolist()
        selected_methods = st.sidebar.multiselect("Select Meeting Method(s):", options=meeting_methods, default=meeting_methods)
        if not selected_methods:
            selected_methods = meeting_methods
        
        # --- Apply Filters ---
        df_filtered = data[data['q24_met_online'].isin(selected_methods)]
        
        # --- Key Metrics ---
        st.header("Key Metrics (Filtered Data)")
        col1, col2 = st.columns(2)
        total_couples = df_filtered.shape[0]
        avg_duration = df_filtered['how_long_relationship'].mean()
        col1.metric("Total Couples", f"{total_couples}")
        col2.metric("Avg. Relationship Duration (Years)", f"{avg_duration:.1f}")
        st.markdown("---")
        
        # --- Visualizations ---
        sns.set_theme(style="whitegrid")
        
        # Chart 1: Distribution of Meeting Methods
        st.subheader(config["chart1_title"])
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        sns.countplot(
            data=df_filtered,
            x='q24_met_online',
            order=df_filtered['q24_met_online'].value_counts().index,
            ax=ax1,
            palette="viridis"
        )
        ax1.set_xlabel("Meeting Method")
        ax1.set_ylabel("Count")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig1)
        
        # Chart 2: Relationship Quality by Meeting Method (as Percentages)
        st.subheader(config["chart2_title"])
        # Build a cross-tabulation normalized by meeting method (row-wise percentages)
        quality_pct = pd.crosstab(df_filtered['q24_met_online'], df_filtered['relationship_quality'], normalize='index') * 100
        quality_pct = quality_pct.reset_index().melt(id_vars='q24_met_online', var_name='relationship_quality', value_name='percentage')
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        sns.barplot(
            data=quality_pct,
            x='q24_met_online',
            y='percentage',
            hue='relationship_quality',
            ax=ax2,
            palette="magma"
        )
        ax2.set_xlabel("Meeting Method")
        ax2.set_ylabel("Percentage (%)")
        ax2.legend(title="Relationship Quality", bbox_to_anchor=(1, 1))
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig2)
        
        # Chart 3: Age Difference Distribution by Meeting Method (Histogram)
        st.subheader("Age Difference Distribution by Meeting Method")
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        for method in df_filtered['q24_met_online'].unique():
            subset = df_filtered[df_filtered['q24_met_online'] == method]
            sns.histplot(
                subset['age_difference'], kde=True, bins=20, ax=ax3, label=method, alpha=0.5
            )
        ax3.set_xlabel("Age Difference (Years)")
        ax3.set_ylabel("Frequency")
        ax3.legend(title="Meeting Method")
        plt.tight_layout()
        st.pyplot(fig3)

    elif selected_dataset == "Global EV Data Explorer":
        # Clean column names
        data.columns = (
            data.columns.str.lower()
            .str.replace(' ', '_')
        )
        
        # Show original data table if checked
        if st.checkbox("Show Original Data Table", key="ev_original"):
            st.dataframe(data)
        
        # --- Sidebar Filters ---
        st.sidebar.header("Filters")
        
        # Region Filter
        regions = sorted(data['region'].dropna().unique())
        selected_regions = st.sidebar.multiselect("Select Region(s):", options=regions, default=regions)
        if not selected_regions:
            selected_regions = regions
        
        # Year Filter
        years = sorted(data['year'].dropna().astype(int).unique())
        selected_years = st.sidebar.multiselect("Select Year(s):", options=years, default=years)
        if not selected_years:
            selected_years = years
        
        # Powertrain Filter
        powertrains = sorted(data['powertrain'].dropna().unique())
        selected_powertrains = st.sidebar.multiselect("Select Powertrain(s):", options=powertrains, default=powertrains)
        if not selected_powertrains:
            selected_powertrains = powertrains
        
        # Parameter Filter
        parameters = sorted(data['parameter'].dropna().unique())
        selected_parameters = st.sidebar.multiselect("Select Parameter(s):", options=parameters, default=parameters)
        if not selected_parameters:
            selected_parameters = parameters
        
        # --- Apply Filters ---
        df_filtered = data[
            (data['region'].isin(selected_regions)) &
            (data['year'].isin(selected_years)) &
            (data['powertrain'].isin(selected_powertrains)) &
            (data['parameter'].isin(selected_parameters))
        ]
        
        # --- Key Metrics ---
        st.header("Key Metrics (Filtered Data)")
        col1, col2, col3 = st.columns(3)
        total_sales = df_filtered[(df_filtered['parameter'] == 'EV sales') & (df_filtered['unit'] == 'Vehicles')]['value'].sum()
        avg_sales_share = df_filtered[(df_filtered['parameter'] == 'EV sales share') & (df_filtered['unit'] == 'percent')]['value'].mean()
        avg_stock_share = df_filtered[(df_filtered['parameter'] == 'EV stock share') & (df_filtered['unit'] == 'percent')]['value'].mean()
        col1.metric("Total EV Sales (Vehicles)", f"{total_sales:,.0f}")
        col2.metric("Avg. EV Sales Share (%)", f"{avg_sales_share:.2f}")
        col3.metric("Avg. EV Stock Share (%)", f"{avg_stock_share:.2f}")
        st.markdown("---")
        
        # --- Visualizations ---
        sns.set_theme(style="whitegrid")
        
        # Chart 1: EV Sales Over Time by Powertrain (Line Plot)
        col1_viz, col2_viz = st.columns(2)
        with col1_viz:
            st.subheader(config["chart1_title"])
            sales_data = df_filtered[(df_filtered['parameter'] == 'EV sales') & (df_filtered['unit'] == 'Vehicles')]
            if not sales_data.empty and len(selected_years) > 1:
                fig1, ax1 = plt.subplots(figsize=(8, 5))
                sns.lineplot(
                    data=sales_data,
                    x='year', y='value', hue='powertrain',
                    marker='o', ax=ax1, palette='viridis'
                )
                ax1.set_xlabel('Year')
                ax1.set_ylabel('EV Sales (Vehicles)')
                ax1.legend(title='Powertrain')
                plt.tight_layout()
                st.pyplot(fig1)
            elif len(selected_years) == 1:
                st.write(f"Showing data only for year {selected_years[0]}.")
                sales_year = sales_data[sales_data['year'] == selected_years[0]]['value'].sum()
                st.metric(f"EV Sales in {selected_years[0]}", f"{sales_year:,.0f}")
            else:
                st.write("Select multiple years to see trend.")
        
        # Chart 2: EV Sales Share by Region (Bar Plot) - Modified to show overall average across all years
        with col2_viz:
            st.subheader(config["chart2_title"])
            sales_share_data = df_filtered[(df_filtered['parameter'] == 'EV sales share') & (df_filtered['unit'] == 'percent')]
            if not sales_share_data.empty:
                # Calculate the average EV sales share across all selected years for each region
                sales_share_overall = sales_share_data.groupby('region')['value'].mean().reset_index()
                fig2, ax2 = plt.subplots(figsize=(8, 5))
                sns.barplot(
                    data=sales_share_overall,
                    x='value', y='region',
                    ax=ax2, palette='mako'
                )
                ax2.set_xlabel('Average EV Sales Share (%)')
                ax2.set_ylabel('Region')
                ax2.set_title('Overall EV Sales Share Across Selected Years')
                plt.tight_layout()
                st.pyplot(fig2)
            else:
                st.write("No EV sales share data available for the selected filters.")
        
        # Chart 3: EV Stock Share Distribution (Histogram)
        col3_viz, col4_viz = st.columns(2)
        with col3_viz:
            st.subheader(config["chart3_title"])
            stock_share_data = df_filtered[(df_filtered['parameter'] == 'EV stock share') & (df_filtered['unit'] == 'percent')]
            if not stock_share_data.empty:
                fig3, ax3 = plt.subplots(figsize=(8, 5))
                sns.histplot(
                    data=stock_share_data,
                    x='value', kde=True, bins=20,
                    ax=ax3, color='skyblue'
                )
                ax3.set_xlabel('EV Stock Share (%)')
                ax3.set_ylabel('Frequency')
                plt.tight_layout()
                st.pyplot(fig3)
            else:
                st.write("No EV stock share data available for the selected filters.")
        
        # Chart 4: EV Stock by Powertrain (Stacked Bar Plot)
        with col4_viz:
            st.subheader("EV Stock by Powertrain")
            stock_data = df_filtered[(df_filtered['parameter'] == 'EV stock') & (df_filtered['unit'] == 'Vehicles')]
            if not stock_data.empty and len(selected_years) > 1:
                stock_pivot = stock_data.pivot_table(index='year', columns='powertrain', values='value', aggfunc='sum', fill_value=0)
                fig4, ax4 = plt.subplots(figsize=(8, 5))
                stock_pivot.plot(kind='bar', stacked=True, ax=ax4, colormap='rocket')
                ax4.set_xlabel('Year')
                ax4.set_ylabel('EV Stock (Vehicles)')
                ax4.legend(title='Powertrain', bbox_to_anchor=(1, 1))
                plt.tight_layout()
                st.pyplot(fig4)
            elif len(selected_years) == 1:
                st.write(f"Showing data only for year {selected_years[0]}.")
                stock_year = stock_data[stock_data['year'] == selected_years[0]]['value'].sum()
                st.metric(f"EV Stock in {selected_years[0]}", f"{stock_year:,.0f}")
            else:
                st.write("Select multiple years to see trend.")
        
else:
    st.error("Failed to load data.")
