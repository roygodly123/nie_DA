import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind, chi2_contingency

# Chinese format settings
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# Read file and clean data which includes strange values
df = pd.read_csv('csv/data_nie_cleaned_file.csv')

# Split data into two periods
df_before_2018 = df[df['year'] < 2018].copy()
df_after_2018 = df[df['year'] >= 2018].copy()

# Drop irrelevant variables and get a list of columns
columns_to_drop = ['住院号', '姓名', '年龄', '性别', '吸烟', 'year', 'treat', '高血压', '糖尿病', '高血脂']
df_clean = df.drop(columns=columns_to_drop).copy()
indicators = df_clean.columns.tolist()


# Calculate p-values
def compare_periods(before, after, indicator):
    t_stat, p_value = ttest_ind(before[indicator].dropna(), after[indicator].dropna())
    return t_stat, p_value


results = {}
for indicator in indicators:
    before_mean = df_before_2018[indicator].mean()
    before_var = df_before_2018[indicator].var()
    after_mean = df_after_2018[indicator].mean()
    after_var = df_after_2018[indicator].var()

    t_stat, p_value = compare_periods(df_before_2018, df_after_2018, indicator)

    # Handle extreme p-values
    if p_value < 1e-3:
        p_value_str = "< 0.001"
    elif p_value > 0.999:
        p_value_str = "> 0.999"
    else:
        p_value_str = round(p_value, 3)

    results[indicator] = {
        't_statistic': round(t_stat, 3),
        'p_value': p_value_str,
        'mean_before_2018': round(before_mean, 3),
        'variance_before_2018': round(before_var, 3),
        'mean_after_2018': round(after_mean, 3),
        'variance_after_2018': round(after_var, 3)
    }

# Convert results to DataFrame for better readability
results_df = pd.DataFrame(results).T

# Display results
print(results_df)

# Save results to CSV file
results_df.to_csv('results/1. before_and_after_2018.csv', encoding='utf-8-sig', index=False)
results_df.to_csv('results/(optional) 1. before_and_after_2018.csv', encoding='ansi', index=False)
# Define significance level
alpha = 0.05

# Print results with interpretation
for indicator, result in results.items():
    t_statistic, p_value = result['t_statistic'], result['p_value']
    if isinstance(p_value, str):
        p_value_float = 0 if p_value == "< 0.001" else 1
    else:
        p_value_float = p_value
    if p_value_float < alpha:
        print(
            f"{indicator} 的t统计量为 {t_statistic}，p值为 {p_value}，在显著性水平 {alpha} 下，两组数据之间存在显著差异。")
    else:
        print(
            f"{indicator} 的t统计量为 {t_statistic}，p值为 {p_value}，在显著性水平 {alpha} 下，两组数据之间没有显著差异。")


# Plotting box plots for each clinical indicator to compare distributions before and after 2018
# for indicator in indicators:
#     plt.figure(figsize=(10, 6))
#     sns.boxplot(x='Indicator Period', y=indicator, data=pd.concat([df_before_2018[[indicator]].assign(**{'Indicator Period': 'Before 2018'}),
#                                                                   df_after_2018[[indicator]].assign(**{'Indicator Period': 'After 2018'})]))
#     plt.title(f'Comparison of {indicator} Before and After 2018')
#     plt.xlabel('Indicator Period')
#     plt.ylabel(indicator)
#     plt.show()