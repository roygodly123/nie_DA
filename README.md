# Data Analysis for Nie

## Description
包括一个关于心血管病的病人的数据集, 2017年9月至2018年12月，就当2018年吧，前面是筹划期，后面2019-2023是持续改进期

1. 这个数据主要想分析下2018年后（胸痛中心成立后）与2018年前（胸痛中心成立前）数据对比，比如心衰发生率、死亡率等指标到底有没有明显下降，住院费用有没有降低？等等，同时我也想看看2018年后，随着胸痛中心持续改进，2018-2019-2020-2021-2022这几年组间中心衰，死亡率等其他临床指标有没有明显下降？

2. 年龄，性别，吸烟，高血压，糖尿病等一般指标都要求统计分析一下，对照组和观察组一般都没有统计学差异
   
## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/roygodly123/nie_DA.git
   cd nie_DA.git
2. navigate to virtual env.
   ```sh
4. pip install -r requirements.txt
   
### Usage
1. The csv file directory includes original dataset and cleaned file.
2. The src file directory includes all source code for manipulating the data.
3. The results file directory includes pre-run results.(marked by 1,2,3,4, and a significance file is optional)
4. The csv results are saved by ANSI encoding, if it does not work for your computer, set encoding to UTF-8 and try.
