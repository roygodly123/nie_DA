import itertools
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind, chi2_contingency

def format_p_value(p_value):
    if p_value < 0.0001:
        return '<0.0001'
    elif p_value > 0.9999:
        return '>0.9999'
    else:
        return round(p_value, 4)

df = pd.read_csv('../csv/data_nie_cleaned_file.csv')
groups = [2018, 2019, 2020, 2021, 2022, 2023]
df_after_2018 = df[df['year'] >= 2018]
df_after_2018_general_data = df[df['year'] >= 2018]
df_after_2018 = df_after_2018.drop(columns='住院号').drop(columns='姓名').drop(columns='年龄').drop(columns='性别').drop(
    columns='吸烟').drop(columns='treat').drop(columns='高血压').drop(columns='糖尿病').drop(columns='高血脂')
indicators = df_after_2018.columns.tolist()
grouped_data = {}
for group in groups:
    filtered_data = df_after_2018[df_after_2018['year'] == group]
    grouped_data[group] = filtered_data

# general indicators significance test
# 对每对年份进行两两比较
combinations = list(itertools.combinations(groups, 2))

results = []
for (year1, year2) in combinations:
    print(f"\nAnalysis for {year1} vs {year2}:")

    df_year1 = df[df['year'] == year1].copy()
    df_year2 = df[df['year'] == year2].copy()

    # 添加标识列
    df_year1['year_group'] = f'{year1}'
    df_year2['year_group'] = f'{year2}'

    # 合并数据
    df_combined = pd.concat([df_year1, df_year2])

    # 对一般指标进行统计分析
    general_results_pair = {'year1': year1, 'year2': year2}

    # 分析年龄（连续变量）
    if not df_year1['年龄'].dropna().empty and not df_year2['年龄'].dropna().empty:
        age_p_value = ttest_ind(df_year1['年龄'].dropna(), df_year2['年龄'].dropna())[1]
        general_results_pair['年龄'] = format_p_value(age_p_value)
        print(f"P-value for 年龄 comparison between {year1} and {year2}: {general_results_pair['年龄']}")
    else:
        general_results_pair['年龄'] = None
        print(f"No data available for 年龄 comparison between {year1} and {year2}")

    # 分析性别、吸烟、高血压、糖尿病、高血脂（分类变量）
    categorical_variables = ['性别', '吸烟', '高血压', '糖尿病', '高血脂']
    for var in categorical_variables:
        contingency_table = pd.crosstab(df_combined['year_group'], df_combined[var])
        if contingency_table.size > 0:
            _, p_value, _, _ = chi2_contingency(contingency_table)
            general_results_pair[var] = format_p_value(p_value)
            print(f"P-value for {var} comparison between {year1} and {year2}: {general_results_pair[var]}")
        else:
            general_results_pair[var] = None
            print(f"No data available for {var} comparison between {year1} and {year2}")

    results.append(general_results_pair)

after_2018_general_indicator_results = pd.DataFrame(results)
after_2018_general_indicator_results.to_csv('../results/4. after_2018_general_data_validation.csv', index=False, encoding='ansi')
print("\nGenerated Results Table:")
print(after_2018_general_indicator_results)
