## Objective

This project investigates rice production trends in selected Asian countries from 1980 to 2023. I will analyze changes in yield and area harvested over time, and will experiment with visualization techniques to compare historical and recent values.

Data type: panel data (cross-sectional and time series data).

## Current progress

- Data loaded in and cleaned for relevant factors and quality
- EDA (Exploratory Data Analysis): Please view agri_data_expl.ipynb to see EDA visualizations and analyses
- Interactive Dash web application exploring annual agricultural, population and economic data for each country.
- Simple analysis
    - Began significance testing for difference in % employed by high/low Urban:Rural ratio. Began investigating significance testing for non-intervention time series data. Refer to LJ.

## Next steps

- Significance Tests
    - Q: Is there a significant difference in % employed in agriculture in countries with high Urban:Rural ratio vs low Urban:Rural ratio?
    - Q: Is there a significant difference in yields between countries with high area harvested prop vs low area harvested prop?
    - Will require personal research on conducting significance tests with time-series data.

### Format & Technologies

Jupyter Notebook, Python (pandas, seaborn, matplotlib, numpy), Dash, Render

Data Used (csv files):

- FAOSTAT production data, 1980-2023
- FAOSTAT-employment-data
- FAOSTAT-population-data
- FAOSTAT-macroecon-data
- Our World in Data https://ourworldindata.org/grapher/land-area-hectares
