import csv

EXPORT_CONFIG_HEADERS = [
        "num_threads",
        "num_connections",
        "duration",
        "timeout"
]

WRK_CONFIG_HEADERS = [
    "cpu_list",
    "num_threads",
    "num_connections",
    "duration",
    "timeout",
    "url"
]


def wrk_config(cpu_list='0-7', 
        num_threads=8,
        num_connections=400,
        duration=30,
        timeout=40,
        url="http://localhost:81"):
    return {
        "cpu_list": cpu_list,
        "num_threads": num_threads,
        "num_connections": num_connections,
        "duration": duration,
        "timeout": timeout,
        "url": url
    }

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
