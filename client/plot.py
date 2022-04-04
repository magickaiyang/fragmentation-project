import argparse
import matplotlib.pyplot as plt
import pandas as pd

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
