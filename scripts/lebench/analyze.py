from json import load
import pandas as pd
import numpy as np
import sys
import seaborn as sns
import matplotlib.pyplot as plt

def load_results_of_one_config(config_name, repeat_runs):
    dataframes = []

    for i in range(repeat_runs):
        df_i = pd.read_csv('results/output.' + config_name + '-' + str(i) + '.csv',
            index_col=0, header=None, skiprows=2)
        df_i.drop(df_i.columns[[1]], axis=1, inplace=True)
        dataframes.append(df_i)

    df = pd.concat(dataframes, axis=0)
    df = df[~df.index.str.contains("average")]
    df['config_name'] = config_name
    return df

def main():
    pd.options.display.float_format = '{:.9f}'.format

    if len(sys.argv) != 2:
        print('Needs repeat runs')
        sys.exit(1)
    
    repeat_runs = int(sys.argv[1])

    dataframes = []

    for config_name in ['1gb', '2mb']:
        df_i = load_results_of_one_config(config_name, repeat_runs)
        dataframes.append(df_i)

    df = pd.concat(dataframes, axis=0)
    df.index.name = 'items'
    df.columns.values[0] = 'values'
    print(df)

    sns.boxplot(data=df, x=df.index, y='values', hue='config_name')
    plt.show()

main()
