# About My Project

Student Name:  Jacob VonTersch
Student Email:  jvonters@syr.edu

### What it does

This project is an NCAA basketball analytics dashboard that analyzes game data from four major conferences (SEC, Big Ten, Big 12, and ACC). It provides comprehensive visualizations including team performance comparisons, player shooting analysis, shot charts, and conference standings.
The dashboard features interactive elements allowing users to select specific teams and conferences, view detailed player statistics, and analyze shooting patterns through various charts and visualizations.

### How you run my project

Ensure you have the required packages, they are all in my requirements.txt file.
Navigate to the final_dashboard.py file in the directory 
Make sure the data file 'PBP2324.csv' is in the cache directory
Run streamlit
The dashboard will open in your default web browser
Use the sidebar to select conferences and teams for analysis

### Other things you need to know

The project includes extensive testing which can be run using pytest. All visualizations are interactive and can be downloaded from the dashboard. The dashboard automatically handles data cleaning and processing.
Shot charts show both team-wide and individual player shooting patterns. Performance metrics include win percentages, shooting percentages, and player statistics.
The project structure separates core analysis functions (basketball_analysis.py) from the dashboard interface (final_dashboard.py) for better maintainability.


## Dataset
The dataset for this project is hosted on Google Drive. The code automatically handles downloading and loading the data.

To use the dataset:
1. Make sure you have pandas installed (`pip install pandas`)
2. Use the `load_dataset()` function from `data_loader.py`
3. The data will be automatically downloaded and loaded into a pandas DataFrame


The streamlit ran way smoother when I was reading my file from the cache folder, after changing it to the google drive it runs much slower.