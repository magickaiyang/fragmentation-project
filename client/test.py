import re
import csv
import subprocess
import os
import argparse

from config import EXPORT_CONFIG_HEADERS, wrk_config, parse_test_config


# adapted from https://github.com/MaartenSmeets/db_perftest/blob/master/test_scripts/wrk_parser.py

wrkcmd = 'wrk'

EXPORT_WRK_HEADERS = [
    'lat_avg',
    'lat_stdev',
    'lat_max',
    'req_avg',
    'req_stdev',
    'req_max',
    'tot_requests',
    'tot_duration',
    'read',
    'err_connect',
    'err_read', 
    'err_write' , 
    'err_timeout', 
    'req_sec_tot',
    'read_tot'
]

EXPORT_ALL_HEADERS = EXPORT_CONFIG_HEADERS + EXPORT_WRK_HEADERS

def wrk_data(wrk_output):
    return [str(wrk_output[h]) for h in EXPORT_WRK_HEADERS]


def get_bytes(size_str):
    x = re.search("^(\d+\.*\d*)(\w+)$", size_str)
    if x is not None:
        size = float(x.group(1))
        suffix = (x.group(2)).lower()
    else:
        return size_str

    if suffix == 'b':
        return size
    elif suffix == 'kb' or suffix == 'kib':
        return size * 1024
    elif suffix == 'mb' or suffix == 'mib':
        return size * 1024 ** 2
    elif suffix == 'gb' or suffix == 'gib':
        return size * 1024 ** 3
    elif suffix == 'tb' or suffix == 'tib':
        return size * 1024 ** 3
    elif suffix == 'pb' or suffix == 'pib':
        return size * 1024 ** 4

    return False


def get_number(number_str):
    x = re.search("^(\d+\.*\d*)(\w*)$", number_str)
    if x is not None:
        size = float(x.group(1))
        suffix = (x.group(2)).lower()
    else:
        return number_str

    if suffix == 'k':
        return size * 1000
    elif suffix == 'm':
        return size * 1000 ** 2
    elif suffix == 'g':
        return size * 1000 ** 3
    elif suffix == 't':
        return size * 1000 ** 4
    elif suffix == 'p':
        return size * 1000 ** 5
    else:
        return size

    return False


def get_ms(time_str):
    x = re.search("^(\d+\.*\d*)(\w*)$", time_str)
    if x is not None:
        size = float(x.group(1))
        suffix = (x.group(2)).lower()
    else:
        return time_str

    if suffix == 'us':
        return size / 1000
    elif suffix == 'ms':
        return size
    elif suffix == 's':
        return size * 1000
    elif suffix == 'm':
        return size * 1000 * 60
    elif suffix == 'h':
        return size * 1000 * 60 * 60
    else:
        return size

    return False


def parse_wrk_output(wrk_output):
    retval = {}
    for line in wrk_output.splitlines():
        x = re.search("^\s+Latency\s+(\d+\.\d+\w*)\s+(\d+\.\d+\w*)\s+(\d+\.\d+\w*).*$", line)
        if x is not None:
            retval['lat_avg'] = get_ms(x.group(1))
            retval['lat_stdev'] = get_ms(x.group(2))
            retval['lat_max'] = get_ms(x.group(3))
        x = re.search("^\s+Req/Sec\s+(\d+\.\d+\w*)\s+(\d+\.\d+\w*)\s+(\d+\.\d+\w*).*$", line)
        if x is not None:
            retval['req_avg'] = get_number(x.group(1))
            retval['req_stdev'] = get_number(x.group(2))
            retval['req_max'] = get_number(x.group(3))
        x = re.search("^\s+(\d+)\ requests in (\d+\.\d+\w*)\,\ (\d+\.\d+\w*)\ read.*$", line)
        if x is not None:
            retval['tot_requests'] = get_number(x.group(1))
            retval['tot_duration'] = get_ms(x.group(2))
            retval['read'] = get_bytes(x.group(3))
        x = re.search("^Requests\/sec\:\s+(\d+\.*\d*).*$", line)
        if x is not None:
            retval['req_sec_tot'] = get_number(x.group(1))
        x = re.search("^Transfer\/sec\:\s+(\d+\.*\d*\w+).*$", line)
        if x is not None:
            retval['read_tot'] = get_bytes(x.group(1))
        x = re.search(
            "^\s+Socket errors:\ connect (\d+\w*)\,\ read (\d+\w*)\,\ write\ (\d+\w*)\,\ timeout\ (\d+\w*).*$", line)
        if x is not None:
            retval['err_connect'] = get_number(x.group(1))
            retval['err_read'] = get_number(x.group(2))
            retval['err_write'] = get_number(x.group(3))
            retval['err_timeout'] = get_number(x.group(4))
    if 'err_connect' not in retval:
        retval['err_connect'] = 0
    if 'err_read' not in retval:
        retval['err_read'] = 0
    if 'err_write' not in retval:
        retval['err_write'] = 0
    if 'err_timeout' not in retval:
        retval['err_timeout'] = 0
    return retval


def execute_wrk(cpu_list, num_threads, num_connections, duration, timeout, url):
    cmd = 'taskset -c ' + str(cpu_list) + ' ' + wrkcmd + ' --timeout ' + \
            str(timeout) + ' -d' + str(duration) + 's -c' + \
            str(num_connections) + ' -t' + str(num_threads) + ' ' + url
    process = subprocess.run(cmd.split(' '), check=True, \
            stdout=subprocess.PIPE, universal_newlines=True)
    output = process.stdout
    return output


def main():
    
    parser = argparse.ArgumentParser(description = \
            'run and save http workload tests with wrk. Saves to results/')
    parser.add_argument('test_config', type=str, \
            help="CSV test config file to run")
    
    args = parser.parse_args()

    csv_lines = []

    test = parse_test_config(args.test_config)

    savefile = os.path.join('results/', os.path.basename(args.test_config))

    assert os.path.exists(os.path.dirname(savefile)), \
            "save file path does not exist:\n\t{}".format( \
            os.path.dirname(savefile))

    test = parse_test_config(args.test_config)

    
    for i, wrk_cfg in enumerate(test):
        print("running wrk ({}/{}):\n\t{}\n".format(i, len(test), wrk_cfg))

        wrk_output = execute_wrk(**wrk_cfg)

        # print(str(wrk_output) + "\n\n")
        # print("****wrk output dict: \n\n")
        wrk_output_dict = parse_wrk_output(wrk_output)
        # print(str(wrk_output_dict) + "\n\n")

        # print("****wrk output csv line: \n\n")
        wrk_output_csv = wrk_data(wrk_output_dict)
        config_csv = [str(wrk_cfg[h]) for h in EXPORT_CONFIG_HEADERS]
        csv_lines.append(config_csv + wrk_output_csv)

        # print(str(wrk_output_csv))

    print("saving to file...")

    with open(savefile, 'w+') as f:
        writer = csv.writer(f)
        writer.writerow(EXPORT_ALL_HEADERS)
        for line in csv_lines:
            writer.writerow(line)

    print("done")


if __name__ == '__main__':
    main()
