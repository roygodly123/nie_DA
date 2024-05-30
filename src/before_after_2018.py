import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind, chi2_contingency
import scipy.stats as stats

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

# Calculate p-values for continuous variables
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
        'variance_after_2018': round(after_var, 3),
        'chi2_statistic': np.nan,
        'chi2_p_value': np.nan
    }

# Function to compute confidence interval
def mean_confidence_interval(data, confidence=0.95):
    data = data.dropna()  # Drop missing values
    a = np.array(data)
    n = len(a)
    if n == 0:
        return np.nan, np.nan, np.nan
    m, se = np.mean(a), stats.sem(a)
    h = se * stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h

# Chi-Square Test for discrete variables
def chi_square_test(before, after, indicator):
    contingency_table = pd.crosstab(index=before[indicator], columns='Before 2018') \
                      .join(pd.crosstab(index=after[indicator], columns='After 2018'), how='outer').fillna(0)
    chi2, p_value, _, _ = chi2_contingency(contingency_table)
    return chi2, p_value

continuous_vars = ['住院天数', '住院费用', 'probnpmax', 'ctnimax', 'dtob', 'lvdd', 'lvef', '室间隔', '左室后壁']
discrete_vars = [indicator for indicator in indicators if indicator not in continuous_vars]

output_dir = 'before_after_2018_plots'
os.makedirs(output_dir, exist_ok=True)

for indicator in discrete_vars:
    # Calculate Chi-Square test
    chi2_stat, p_value = chi_square_test(df_before_2018, df_after_2018, indicator)

    # Handle extreme p-values
    if p_value < 1e-3:
        p_value_str = "< 0.001"
    elif p_value > 0.999:
        p_value_str = "> 0.999"
    else:
        p_value_str = round(p_value, 3)
    
    # Compute mean and confidence interval for before 2018
    mean_before, ci_low_before, ci_high_before = mean_confidence_interval(df_before_2018[indicator])
    # Compute mean and confidence interval for after 2018
    mean_after, ci_low_after, ci_high_after = mean_confidence_interval(df_after_2018[indicator])
    
    # Add chi-square results to the results dictionary
    results[indicator].update({
        'chi2_statistic': round(chi2_stat, 3),
        'chi2_p_value': p_value_str
    })
    
    # Create a DataFrame for visualization
    summary_df = pd.DataFrame({
        'Period': ['Before 2018', 'After 2018'],
        'Mean': [mean_before, mean_after],
        'CI Lower': [ci_low_before, ci_low_after],
        'CI Upper': [ci_high_before, ci_high_after]
    })
    
    # Plotting Bar Plot
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Period', y='Mean', data=summary_df, ci=None, palette='muted')
    plt.errorbar(x=[0, 1], y=summary_df['Mean'], yerr=[summary_df['Mean'] - summary_df['CI Lower'], summary_df['CI Upper'] - summary_df['Mean']],
                 fmt='none', c='black', capsize=5)
    plt.title(f'Mean and Confidence Interval of {indicator} Before and After 2018\nChi2: {round(chi2_stat, 3)}, p-value: {p_value_str}')
    plt.xlabel('Period')
    plt.ylabel(f'Mean {indicator} (Proportion)')
    plt.ylim(0, 1)
    plt.grid(True) 
    file_path = os.path.join(output_dir, f'{indicator}.png')
    plt.savefig(file_path, bbox_inches='tight')

    # Print results with interpretation
    if p_value < 0.05:
        print(f"{indicator} 的卡方统计量为 {round(chi2_stat, 3)}，p值为 {p_value_str}，在显著性水平 0.05 下，两组数据之间存在显著差异。")
    else:
        print(f"{indicator} 的卡方统计量为 {round(chi2_stat, 3)}，p值为 {p_value_str}，在显著性水平 0.05 下，两组数据之间没有显著差异。")

for indicator in continuous_vars:
    plt.figure(figsize=(10, 6))
    sns.violinplot(x='Indicator Period', y=indicator, data=pd.concat([df_before_2018[[indicator]].assign(**{'Indicator Period': 'Before 2018'}),
                                                                      df_after_2018[[indicator]].assign(**{'Indicator Period': 'After 2018'})]))
    plt.title(f'Comparison of {indicator} Before and After 2018')
    plt.xlabel('Indicator Period')
    plt.ylabel(indicator)
    file_path = os.path.join(output_dir, f'{indicator}.png')
    plt.savefig(file_path, bbox_inches='tight')

# Convert results to DataFrame for better readability
results_df = pd.DataFrame(results).T

# Display results
print(results_df)

# Save results to CSV file
results_df.to_csv('results/1. before_and_after_2018.csv', encoding='utf-8-sig')
results_df.to_csv('results/(optional) 1. before_and_after_2018.csv', encoding='ansi')
