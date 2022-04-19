# !/usr/bin/python3

import csv
import subprocess
import os
import argparse

result_dir = "./result"







def benchbase_config(cpu_list='0',
                     page_size='4k',
                     num_iter=1,
                     url="http://localhost:"):
    return {
        "cpu_list": cpu_list,
        "page_size": page_size,
        "num_iter": num_iter,
        "url": url
    }


def memcached_config(cpu_list='0',
                     page_size='4k',
                     num_iter=1,
                     url="http://localhost:11211"):
    return {
        "cpu_list": cpu_list,
        "page_size": page_size,
        "num_iter": num_iter,
        "url": url
    }


def redis_config(cpu_list='0',
                 page_size='4k',
                 num_iter=1,
                 url="http://localhost:6379"):
    return {
        "cpu_list": cpu_list,
        "page_size": page_size,
        "num_iter": num_iter,
        "url": url
    }


def save_meminfo(cpu_list='0',
                 page_size='4k',
                 num_iter=1,
                 benchmark=""):
    save_path = os.path.join(result_dir, to_string(cpu_list, page_size, num_iter, benchmark))
    os.system("cp /proc/meminfo " + save_path)
    print("Saving /proc/meminfo to {}".format(save_path))


def to_string(cpu_list='0',
              page_size='4k',
              num_iter=1,
              benchmark=""):
    return "{}_{}_{}_{}".format(cpu_list, page_size, num_iter, benchmark)


def execute(cpu_list='0',
            page_size='4k',
            num_iter=1,
            benchmark="",
            cmd=""):
    cmd = 'taskset -c ' + str(cpu_list) + ' ' + cmd
    process = subprocess.run(cmd.split(' '), check=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.stdout
    return output


def save(savefile, content):
    # create result directory
    if not os.path.exists("./result"):
        os.mkdir("./result")

    with open(os.path.join("./result", savefile), 'w+') as f:
        writer = csv.writer(f)
        writer.writerow(EXPORT_ALL_HEADERS)
        for line in content:
            writer.writerow(line)
