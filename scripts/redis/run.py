# !/usr/bin/python3

"""
python3 run.py -n $NUM_ITER -d $DATASET -c $CPU_LIST -p $PAGE_SIZE
"""
import argparse
import os
import subprocess

result_dir = "./result"


def execute(cpu_list='0-7',
            page_size='4k',
            num_iter=1,
            benchmark="",
            cmd=""):
    taskset_cmd = 'taskset -c ' + str(cpu_list) + ' ' + cmd
    process = subprocess.run(taskset_cmd.split(' '), check=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.stdout
    return output


def to_string(cpu_list='0',
              page_size='4k',
              num_iter=1,
              benchmark=""):
    return "{}_{}_{}_{}".format(cpu_list, page_size, num_iter, benchmark)


def save_meminfo(cpu_list='0',
                 page_size='4k',
                 num_iter=1,
                 benchmark=""):
    save_path = os.path.join(result_dir, to_string(cpu_list, page_size, num_iter, benchmark))
    os.system("cp /proc/meminfo " + save_path)
    print("Saving /proc/meminfo to {}".format(save_path))


if __name__ == "__main__":
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=int, required=True, help='# of iteration')
    parser.add_argument('--c', type=str, required=False, help='cpu list')
    parser.add_argument('--p', type=str, required=False, help='page size')
    args = parser.parse_args()

    for i in range(args.n):
        cmd = "redis-benchmark >> benchmark-result_" + str(i) + ".log"
        out = execute(cpu_list=args.c, page_size=args.p, num_iter=args.n, benchmark="redis", cmd=cmd)
        save_meminfo(cpu_list=args.c, page_size=args.p, num_iter=args.n, benchmark="redis")
