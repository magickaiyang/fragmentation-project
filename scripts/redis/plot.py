# !/usr/bin/python3

import argparse
import csv

import matplotlib.pyplot as plt
import pandas as pd

WRK_CONFIG_HEADERS = [
    "cpu_list",
    "num_threads",
    "num_connections",
    "duration",
    "timeout",
    "url"
]

def parse_test_config(csvfile):
    retval = []
    with open(csvfile, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        rows = list(reader)
        header = rows[0]
        for row in rows[1:]:
            if (len(row) == len(WRK_CONFIG_HEADERS)):
                retval.append(dict(zip(header, row)))
            else:
                print("warning: csv has row with {} cols".format(len(row)))
    return retval

def main():
    parser = argparse.ArgumentParser(description = \
            'plot results from wrk')
    parser.add_argument('result', type=str, \
            help="CSV test result file to run")

    args = parser.parse_args()

    TEST_PATH = 'results/test1.csv' 

    df = pd.read_csv(TEST_PATH)

    df.plot.line("num_connections", "lat_avg")
    plt.show()

if __name__ == "__main__":
    main()