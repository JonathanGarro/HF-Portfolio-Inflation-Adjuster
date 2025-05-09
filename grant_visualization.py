import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import matplotlib.ticker as mticker
import os

# create Outputs directory if it doesn't exist
os.makedirs('Outputs', exist_ok=True)

sns.set(style="whitegrid")
plt.rcParams.update({'font.size': 12})

custom_palette = [
    '#F4B000',  # Yellow-gold
    '#F5DE00',  # Bright yellow
    '#7B0085',  # Purple
    '#FA2D01',  # Red-orange
    '#42009E',  # Deep purple
    '#CB5F00',  # Orange-brown
    '#0039F4',  # Blue
    '#00EAFB',  # Cyan
    '#5D8E00',  # Olive green
    '#700027',  # Burgundy
    '#00410E'   # Dark green
]
sns.set_palette(custom_palette)

grants_df = pd.read_csv('grants_data.csv')
inflation_df = pd.read_csv('inflation_history.csv')

# convert award date to datetime and extract year
grants_df['President Approval/Award Date'] = pd.to_datetime(
    grants_df['President Approval/Award Date'],
    errors='coerce'
)
grants_df['Year'] = grants_df['President Approval/Award Date'].dt.year

# clean rows
grants_df = grants_df.dropna(subset=['Year', 'Amount'])
grants_df['Amount'] = pd.to_numeric(grants_df['Amount'], errors='coerce')
grants_df = grants_df.dropna(subset=['Amount'])


def bucket_primary_program(program):
    if pd.isna(program):
        return 'Other'

    # i bucketed some programs that are similar
    buckets = {
        'Culture, Race, & Equity': ['Culture, Race, & Equity'],
        'Cyber': ['Cyber', 'Cybersecurity'],
        'Economy and Society': ['Economy', 'Society', 'Economy and Society'],
        'Education': ['Education'],
        'Environment and Special Initiative on Climate': ['Environment', 'Climate', 'Special Initiative on Climate'],
        'Gender, Equity & Governance': ['Gender', 'Gender Equity & Governance', 'Governance'],
        'Initiatives and Special Projects': ['Initiatives', 'Special Projects', 'Initiative'],
        'Performing Arts': ['Performing Arts', 'Arts'],
        'Philanthropy': ['Philanthropy'],
        'Regional and SBAC': ['Regional', 'SBAC'],
        'U.S. Democracy': ['U.S. Democracy', 'Democracy', 'US Democracy']
    }

    # throw everything else into an Other bucket
    for bucket_name, keywords in buckets.items():
        if any(keyword in program for keyword in keywords):
            return bucket_name

    return 'Other'


grants_df['Bucketed_Program'] = grants_df['Top Level Primary Program'].apply(bucket_primary_program)

grouped_data = grants_df.groupby(['Year', 'Bucketed_Program'])['Amount'].sum().reset_index()

pivot_data = grouped_data.pivot_table(
    index='Year',
    columns='Bucketed_Program',
    values='Amount',
    aggfunc='sum',
    fill_value=0
)

# convert to billions
pivot_data = pivot_data / 1_000_000_000

# sort columns in reverse order to match legend order
pivot_data = pivot_data[pivot_data.columns[::-1]]

plt.figure(figsize=(15, 8))
pivot_data.plot(kind='bar', stacked=True, figsize=(15, 8))
plt.title('Grant Amounts by Year and Primary Program (Nominal Values)', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Amount ($Billions)', fontsize=14)

ax = plt.gca()
labels = [item.get_text().replace('.0', '') for item in ax.get_xticklabels()]
ax.set_xticklabels(labels)
plt.xticks(rotation=45)

plt.legend(title='Primary Program', bbox_to_anchor=(1.05, 1), loc='upper left', reverse=True)
plt.tight_layout()
plt.savefig(os.path.join('Outputs', 'grants_nominal.png'))
plt.close()

yearly_summary = grouped_data.groupby('Year')['Amount'].sum().reset_index()
yearly_summary.columns = ['Year', 'Total_Amount']
yearly_summary.to_csv(os.path.join('Outputs', 'grants_nominal_summary.csv'), index=False)

inflation_df['Year'] = pd.to_numeric(inflation_df['Year'], errors='coerce')
inflation_df['Inflation_Rate'] = pd.to_numeric(inflation_df['Inflation_Rate'], errors='coerce')

inflation_df = inflation_df.sort_values('Year')

base_year_value = 100.0
inflation_df['CPI_Index'] = 0.0

inflation_df.iloc[0, inflation_df.columns.get_loc('CPI_Index')] = base_year_value

# calculate CPI for each year based on the previous year
for i in range(1, len(inflation_df)):
    prev_index = inflation_df.iloc[i - 1]['CPI_Index']
    inflation_rate = inflation_df.iloc[i]['Inflation_Rate'] / 100
    inflation_df.iloc[i, inflation_df.columns.get_loc('CPI_Index')] = prev_index * (1 + inflation_rate)

cpi_lookup = inflation_df.set_index('Year')['CPI_Index'].to_dict()


def get_inflation_multiplier(year, target_year=2024):
    if year not in cpi_lookup or target_year not in cpi_lookup:
        return 1

    return cpi_lookup[target_year] / cpi_lookup[year]

grouped_data['Adjusted_Amount'] = grouped_data.apply(
    lambda row: row['Amount'] * get_inflation_multiplier(int(row['Year'])),
    axis=1
)

pivot_adjusted = grouped_data.pivot_table(
    index='Year',
    columns='Bucketed_Program',
    values='Adjusted_Amount',
    aggfunc='sum',
    fill_value=0
)

pivot_adjusted = pivot_adjusted / 1_000_000_000

pivot_adjusted = pivot_adjusted[pivot_adjusted.columns[::-1]]

plt.figure(figsize=(15, 8))
pivot_adjusted.plot(kind='bar', stacked=True, figsize=(15, 8))
plt.title('Grant Amounts by Year and Primary Program (Inflation-Adjusted to 2024 Dollars)', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Amount ($Billions Inflation Adjusted)', fontsize=14)

ax = plt.gca()
labels = [item.get_text().replace('.0', '') for item in ax.get_xticklabels()]
ax.set_xticklabels(labels)
plt.xticks(rotation=45)

plt.legend(title='Primary Program', bbox_to_anchor=(1.05, 1), loc='upper left', reverse=True)
plt.tight_layout()
plt.savefig(os.path.join('Outputs', 'grants_inflation_adjusted.png'))

yearly_inflation_summary = grouped_data.groupby('Year').agg({
    'Amount': 'sum',
    'Adjusted_Amount': 'sum'
}).reset_index()
yearly_inflation_summary.columns = ['Year', 'Total_Amount', 'Inflation_Adjusted_Amount']

# add inflation rate and CPI index columns
yearly_inflation_summary['Year'] = yearly_inflation_summary['Year'].astype(int)
yearly_inflation_summary = yearly_inflation_summary.merge(
    inflation_df[['Year', 'Inflation_Rate', 'CPI_Index']],
    on='Year',
    how='left'
)

yearly_inflation_summary['Inflation_Multiplier'] = yearly_inflation_summary['Year'].apply(
    lambda year: get_inflation_multiplier(year, 2024)
)

yearly_inflation_summary = yearly_inflation_summary[
    ['Year', 'Total_Amount', 'Inflation_Rate', 'CPI_Index', 'Inflation_Multiplier', 'Inflation_Adjusted_Amount']
]
yearly_inflation_summary.to_csv(os.path.join('Outputs', 'grants_inflation_adjusted_summary.csv'), index=False)

plt.figure(figsize=(12, 6))
plt.plot(inflation_df['Year'], inflation_df['CPI_Index'], marker='o')
plt.title('CPI Index Values Over Time (Base Year Index = 100)', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('CPI Index Value', fontsize=14)
plt.grid(True)
plt.savefig(os.path.join('Outputs', 'cpi_index_chart.png'))
plt.close()