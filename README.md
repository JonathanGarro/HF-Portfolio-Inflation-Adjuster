# Grant Visualization Project

This project analyzes historical grant data and creates visualizations showing grant amounts by year and primary program category. It provides both nominal values and inflation-adjusted values to allow for meaningful comparisons across different time periods.

## Project Overview

The Grant Visualization project processes historical grant data from the Hewlett Foundation and creates:
1. Visualizations of grant amounts by year and program category
2. Summary data files with both nominal and inflation-adjusted values
3. A visualization of the Consumer Price Index (CPI) over time

## Data Sources

The project uses two main data sources:
- `grants_data.csv`: Contains historical grant data including request reference numbers, amounts, grant types, approval dates, and primary program categories
- `inflation_history.csv`: Contains yearly inflation rates from 1913 to 2024

## Inflation Calculation Methodology

The inflation adjustment is performed using the following methodology:

### 1. CPI Index Calculation

The script creates a Consumer Price Index (CPI) series starting with a base value of 100 for the earliest year in the dataset. For each subsequent year, it calculates the new index by applying that year's inflation rate to the previous year's index:

```
CPI_Index[year] = CPI_Index[year-1] * (1 + Inflation_Rate[year]/100)
```

This creates a continuous CPI index series that reflects the cumulative effect of inflation over time.

### 2. Inflation Multiplier Calculation

To convert dollar amounts from one year to another (e.g., from 1977 to 2024), the script calculates an inflation multiplier:

```
Inflation_Multiplier = CPI_Index[target_year] / CPI_Index[source_year]
```

This multiplier represents how many dollars in the target year have the same purchasing power as one dollar in the source year.

### 3. Adjustment Application

The script applies the inflation multiplier to each grant amount to convert it to 2024 dollars:

```
Adjusted_Amount = Original_Amount * Inflation_Multiplier
```

This adjustment allows for meaningful comparisons of grant amounts across different time periods by accounting for the changing value of money due to inflation.

## Outputs Generated

The script generates the following outputs in the `Outputs` directory:

### Visualizations
1. `grants_nominal.png`: Stacked bar chart showing grant amounts by year and primary program in nominal values
2. `grants_inflation_adjusted.png`: Stacked bar chart showing grant amounts by year and primary program in inflation-adjusted 2024 dollars
3. `cpi_index_chart.png`: Line chart showing the CPI index values over time

### Data Files
1. `grants_nominal_summary.csv`: Summary of total grant amounts by year in nominal values
2. `grants_inflation_adjusted_summary.csv`: Summary of grant amounts by year with the following columns:
   - Year
   - Total_Amount (nominal)
   - Inflation_Rate
   - CPI_Index
   - Inflation_Multiplier (used to convert to 2024 dollars)
   - Inflation_Adjusted_Amount (in 2024 dollars)

## How to Run the Script

### Prerequisites
- Python 3.6 or higher
- Required packages: pandas, matplotlib, seaborn, numpy

### Installation
1. Clone this repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

### Execution
Run the script from the command line:
```
python grant_visualization.py
```

The script will process the data, create the visualizations, and save all outputs to the `Outputs` directory.