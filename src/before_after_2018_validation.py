import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind, chi2_contingency

# Chinese format settings
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# Read file and clean data which include strange values
df = pd.read_csv('../csv/data_nie_cleaned_file.csv')
df_before_2018 = df[df['year'] < 2018]
df_after_2018 = df[df['year'] >= 2018]
df['period'] = df['year'].apply(lambda x: 'Before 2018' if x < 2018 else 'After 2018')

general_results = {}
general_indicators = ['年龄', '性别', '吸烟', '高血压', '糖尿病', '高血脂']

# Analyze 年龄 (continuous variable)
age_p_value = ttest_ind(df_before_2018['年龄'].dropna(), df_after_2018['年龄'].dropna())[1]
general_results['年龄'] = age_p_value

# Analyze 性别, 吸烟, 高血压, 糖尿病, 高血脂 (categorical variables)
categorical_variables = ['性别', '吸烟', '高血压', '糖尿病', '高血脂']
for var in categorical_variables:
    contingency_table = pd.crosstab(df['period'], df[var])
    _, p_value, _, _ = chi2_contingency(contingency_table)
    general_results[var] = p_value

# Convert results to DataFrame for better readability
results_df = pd.DataFrame.from_dict(general_results, orient='index', columns=['p_value'])
results_df.index.name = 'Indicator'

# Define significance level
alpha = 0.05

# Interpret results and add to DataFrame
results_df['Significant'] = results_df['p_value'].apply(lambda x: 'Yes' if x < alpha else 'No')

# Round p-values (safely handle NaN values)
results_df['p_value'] = results_df['p_value'].apply(lambda x: round(x, 3) if pd.notnull(x) else x)

# Print and save the results
print(results_df)
results_df.to_csv('../results/2. before_and_after_2018_general_data.csv', encoding='ansi')

# Print results with interpretation
for indicator, row in results_df.iterrows():
    if row['Significant'] == 'Yes':
        print(f"{indicator}的p值为{row['p_value']}，表明在 2018 年前后，{indicator}分布有显著差异")
    else:
        print(f"{indicator}的p值为{row['p_value']}，表明在 2018 年前后，{indicator}分布没有显著差异")
