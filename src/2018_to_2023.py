import os
import pandas as pd
import numpy as np
import xlsxwriter
from matplotlib import pyplot as plt
from scipy.stats import f_oneway
import seaborn as sns

# Chinese format settings
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# Read the cleaned data
df = pd.read_csv('csv/data_nie_cleaned_file.csv')

# Define the years of interest
years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]

# Filter the data for years 2016 and later
df_after_2016 = df[df['year'] >= 2016]

# Drop unnecessary columns and get clinical indicators
df_after_2016_list = df_after_2016.drop(columns=['住院号', '姓名', '年龄', '性别', '吸烟', 'treat', '高血压', '糖尿病', '高血脂', 'year'])
clinical_indicators = df_after_2016_list.columns.tolist()

# Initialize lists to store results
clinical_results = []
clinical_significance = []

# Loop through each clinical indicator to calculate mean, std, and perform significance tests
for var in clinical_indicators:
    clinical_results_var = {'indicator': var}

    # Calculate the mean and standard deviation for each year
    for year in years:
        mean_value = df_after_2016[df_after_2016['year'] == year][var].mean()
        std_value = df_after_2016[df_after_2016['year'] == year][var].std()
        clinical_results_var[f'{year}_mean'] = mean_value
        clinical_results_var[f'{year}_std'] = std_value

    clinical_results.append(clinical_results_var)

    # Perform ANOVA test across the years
    data_groups = [df_after_2016[df_after_2016['year'] == year][var].dropna() for year in years if not df_after_2016[df_after_2016['year'] == year][var].dropna().empty]
    if len(data_groups) > 1:  # Ensure there is more than one group with data
        anova_result = f_oneway(*data_groups)
        p_value = anova_result.pvalue
        significance = 'Yes' if p_value < 0.05 else 'No'
    else:
        p_value = None
        significance = 'N/A'

    clinical_significance.append({'indicator': var, 'p_value': p_value, 'significance': significance})

# Create an Excel workbook and worksheet using xlsxwriter
workbook = xlsxwriter.Workbook('results/3. clinical_results_and_significance_2016_2023.xlsx', {'nan_inf_to_errors': True})
worksheet = workbook.add_worksheet()

# Construct the header
header = [''] + [year for year in years for _ in range(2)] + ['p_value', 'significance']
sub_header = ['indicator'] + ['mean', 'std'] * len(years) + ['p_value', 'significance']

# Write the headers and merge cells for year labels
worksheet.write_row('A1', header)
worksheet.write_row('A2', sub_header)
cell_format = workbook.add_format({'align': 'center'})
col = 1
for year in years:
    worksheet.merge_range(0, col, 0, col + 1, year, cell_format)
    col += 2

# Write the data to the worksheet
row = 2
for result, significance in zip(clinical_results, clinical_significance):
    worksheet.write(row, 0, result['indicator'])
    col = 1
    for year in years:
        mean_value = result.get(f'{year}_mean', '')
        std_value = result.get(f'{year}_std', '')

        # Handle NaN values
        if pd.isna(mean_value):
            mean_value = ''
        if pd.isna(std_value):
            std_value = ''

        worksheet.write(row, col, mean_value, cell_format)
        worksheet.write(row, col + 1, std_value, cell_format)
        col += 2

    # Write p_value and significance
    worksheet.write(row, col, significance['p_value'])
    worksheet.write(row, col + 1, significance['significance'])
    row += 1

# Close the workbook
workbook.close()

# Create a directory to save the plots
output_dir = 'clinical_indicators_plots'
os.makedirs(output_dir, exist_ok=True)

# Plot each clinical indicator's trend over the years
for var in clinical_indicators:
    plt.figure(figsize=(12, 6))
    
    # 使用年平均值绘制折线图
    df_means = df_after_2016.groupby('year')[var].mean().reset_index()
    sns.lineplot(
        data=df_after_2016,
        x='year', y=var,
        marker='o',
        linestyle='-',
        markersize=8,
        linewidth=2,
        color='b',  # 颜色设置为蓝色
        errorbar=('ci', 95)
    )
    plt.title(f'{var} 年平均值变化趋势 (2016-2023)')
    plt.xlabel('年份')
    plt.ylabel(f'{var} 平均值')
    plt.xticks(years)
    plt.grid(True)
    file_path = os.path.join(output_dir, f'{var}_变化趋势_2016_2023.png')
    plt.savefig(file_path, bbox_inches='tight')
    plt.close()
