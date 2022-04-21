# !/usr/bin/python3

import matplotlib.pyplot as plt
import pandas as pd
import glob

result_dir = "./redis_result"


def plot():
    for summary_file in sorted(glob.glob(result_dir + "/redis*.csv")):
        df = pd.read_csv(summary_file)
        print(df)
        col = df.columns[1:]
        legends = []
        for x in col:
            legends.append(x)
            plt.plot(df['config'], df[x])
        plt.show()


if __name__ == "__main__":
    plot()
