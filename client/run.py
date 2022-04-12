#!/usr/bin/python3
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=int, required=True, help='# of iteration')
    args = parser.parse_args()

    for i in range(args.n):
        cmd = "redis-benchmark >> benchmark-result" + str(i) + ".log"
        os.system(cmd)

