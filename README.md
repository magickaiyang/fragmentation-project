# fragmentation-project

## HTTP server benchmark
Note that unless otherwise specified, scripts are generally run from the repo-level.

### Server Setup
Linux distribution (like Ubuntu) needed.

Run setup script once for nginx

```bash
$ sudo bash server/setup.sh
```

The directory `/var/www/html/index.html` will have the web pages to be served, and `/etc/nginx/sites-enabled/conf` the server configuration.

Go to [localhost:81](localhost:81) to see the server site.

### Starting and stopping nginx server
To re-start the nginx server:
```bash
$ bash server-restart.sh
```

To stop the nginx server:
```bash
$ bash server-stop.sh
```


### Client Setup
Linux distribution (like Ubuntu) needed.

Run setup script once for wrk

```bash
$ sudo bash client/setup.sh
```

### Testing server with wrk on client
To test sample wrk workloads from client and save stats to results/:
```bash
$ python client/test.py tests/test1.csv
```

Then to view an example plot, run
```bash
$ python client/plot.pt results/test1.csv
```

### Creating new tests
A test is a sequential list of wrk workload configurations.
Copy results/test1.csv and add rows for more tests, and change
row values to match the given headers. The arguments are passed to
wrk, but we cannot have comma-separated `cpu_list` values due to being in a CSV.

### Remote client and server
The nginx/wrk configs are set so the client and server are currently the same machine,
serving on `localhost:81`. These must be changed for remote testing.


