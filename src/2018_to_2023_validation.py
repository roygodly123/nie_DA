import itertools
import pandas as pd
from scipy.stats import f_oneway, ttest_ind, chi2_contingency

def format_p_value(p_value):
    if p_value < 0.0001:
        return '<0.0001'
    elif p_value > 0.9999:
        return '>0.9999'
    else:
        return round(p_value, 4)

# Load the dataset
df = pd.read_csv('csv/data_nie_cleaned_file.csv')

# Filter the data for years starting from 2016
df_after_2016 = df[df['year'] >= 2016].copy()

# Drop specific columns from the dataframe
columns_to_drop = ['住院号', '姓名', 'treat']  # Columns not needed for analysis
df_after_2016 = df_after_2016.drop(columns=columns_to_drop)

# Define groups for the analysis
groups = df_after_2016['year'].unique()

# Initialize results dictionary for pairwise comparison
results_pairwise = {}

# Perform statistical analysis for each pair of years
for (year1, year2) in itertools.combinations(groups, 2):
    df_year1 = df_after_2016[df_after_2016['year'] == year1].copy()
    df_year2 = df_after_2016[df_after_2016['year'] == year2].copy()

    # Continuous Variables (t-test)
    for var in ['年龄']:
        data1 = df_year1[var].dropna()
        data2 = df_year2[var].dropna()
        if not data1.empty and not data2.empty:
            p_value = ttest_ind(data1, data2)[1]
            indicator_key = f'{year1} vs {year2}'
            results_pairwise.setdefault(indicator_key, {})[var] = format_p_value(p_value)

    # Categorical Variables (Chi-square Test)
    categorical_variables = ['性别', '吸烟', '高血压', '糖尿病', '高血脂']
    for var in categorical_variables:
        contingency_table = pd.crosstab(df_after_2016['year'], df_after_2016[var])
        _, p_value, _, _ = chi2_contingency(contingency_table)
        indicator_key = f'{year1} vs {year2}'
        results_pairwise.setdefault(indicator_key, {})[var] = format_p_value(p_value)

# Convert results to DataFrame for pairwise comparison
results_pairwise_df = pd.DataFrame.from_dict(results_pairwise, orient='index')

# Save results to CSV file
results_pairwise_df.to_csv('results/pairwise_comparison_results.csv', index=True, encoding='utf-8')

# Print the generated results table
print("\nPairwise Comparison Results:")
print(results_pairwise_df)
