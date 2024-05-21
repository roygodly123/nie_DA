import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind

# chinese format settings
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# read file and clean data which include strange values
df = pd.read_csv('csv/data_nie_v7.csv')
columns_to_clean = ['probnpmax', 'ctnimax']


def clean_data(value):
    if isinstance(value, str):
        try:
            # 替换逗号为小数点
            value = value.replace(',', '.').strip()
            print(f"替换小数点: {value}")

            # 删除无意义的字符
            value = value.replace('\\', '').replace('*', '').strip()
            print(f"删除无意义字符: {value}")

            # 处理大于符号
            if ">" in value:
                numeric_value = float(value.lstrip('>'))
                print(f"处理大于符号: {numeric_value}")
                return numeric_value

            # 处理小于符号
            if "<" in value:
                numeric_value = float(value.lstrip('<'))
                print(f"处理小于符号: {numeric_value}")
                return numeric_value

            # 尝试直接转换为浮点数
            numeric_value = float(value)
            print(f"直接转换为浮点数: {numeric_value}")
            return numeric_value
        except ValueError:
            if value == '':
                print(f"转换失败: {value}")
                return None
            else:
                value = float(value[1:])
                print(f"转换成功: {value}")
                return value
    return value

for column in columns_to_clean:
    df[column] = df[column].apply(clean_data)
for column in columns_to_clean:
    df[column] = pd.to_numeric(df[column], errors='coerce')

cleaned_file_path = 'csv/data_nie_cleaned_file.csv'
optional_cleaned_file_path = 'csv/(optional) data_nie_cleaned_file.csv'
df.to_csv(cleaned_file_path, index=False, encoding='utf-8-sig')
df.to_csv(optional_cleaned_file_path, index=False, encoding='ansi')
