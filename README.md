# Dynamic Multi-Dataset Dashboard

A dynamic, interactive dashboard built with Streamlit for visualizing and analyzing multiple datasets. This dashboard supports various data sources, including Global Video Game Sales, Micro-enterprise Tax Payers (Latvia), How Couples Meet and Stay Together, and Global EV Data Explorer.

## Overview

The **Dynamic Multi-Dataset Dashboard** offers an intuitive way to explore different datasets through interactive filtering and customizable visualizations. Users can easily switch between datasets and view key metrics and charts that provide valuable insights. Built with Python, Streamlit, Pandas, Matplotlib, and Seaborn, the dashboard is both flexible and extendable.

## Features

- **Multi-Dataset Support:** Choose among four datasets via a sidebar selection.
- **Interactive Filtering:** Customize filters for each dataset (e.g., year, genre, status, meeting method, region, and more) to refine the displayed data.
- **Dynamic Visualizations:** Automatically generated charts include bar plots, line charts, pie charts, histograms, and stacked bar charts to represent various metrics.
- **Key Metrics Display:** Overview of important statistics (e.g., total sales, average values, number of records) for each filtered dataset.
- **User-Friendly Interface:** Sidebar controls enable straightforward dataset selection and filter configuration.
- **Customizable Layout:** Organized into sections and columns for clear data presentation.

## Demo

### **Start page:**

![image](https://github.com/user-attachments/assets/867c9252-ef62-4c9c-9e42-05f22efb005e)

### **Filters that vary depending on the data source selected:**

![image](https://github.com/user-attachments/assets/b6e199fb-a171-4d9b-9f0f-5a10bc2b1b2e)

### **Various provided datasets:**

![image](https://github.com/user-attachments/assets/d3961475-bb13-43da-8596-91bc0d2df216)

### **Option to open data table from which visualizations were generated:**

![image](https://github.com/user-attachments/assets/135fb1bb-4056-4cad-b0cd-b4be8b70d668)

## Installation

1. **Clone the Repository:**

```bash
git clone https://github.com/your-username/dynamic-multi-dataset-dashboard.git
cd dynamic-multi-dataset-dashboard
```

2. **Create and Activate a Virtual Environment (Recommended):**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies:**

```bash
pip install -r requirements.txt
```

## Running the Application

1. **Prepare Your Datasets:**

Ensure these CSV files are in your working directory:
- `vgsales.csv`
- `pdb_munmaksataji_odata.csv`
- `HCMST_ver_3.04.csv`
- `IEA-EV-dataEV salesHistoricalCars.csv`

2. **Launch Streamlit:**

```bash
streamlit run app.py
```

## Usage

- **Dataset Selection:** Select datasets from the sidebar.
- **Filtering:** Adjust filters for specific insights.
- **Visual Exploration:** View detailed charts (bar, line, pie, histograms).
- **Key Metrics:** Quickly review summarized statistics.

## Directory Structure

```plaintext
dynamic-multi-dataset-dashboard/
├── app.py
├── vgsales.csv
├── pdb_munmaksataji_odata.csv
├── HCMST_ver_3.04.csv
├── IEA-EV-dataEV salesHistoricalCars.csv
├── requirements.txt
└── README.md
```

## Dependencies

- **Python 3.7+**
- **Streamlit**
- **Pandas**
- **Matplotlib**
- **Seaborn**

## Contact
Project Link: [https://github.com/IlyaPoloz/DataSetAnalysis](https://github.com/IlyaPoloz/DataSetAnalysis/)
