# fragmentation-project

## HTTP server benchmark

### Setup
Linux distribution (like Ubuntu)

Run setup script once for nginx and wrk

```bash
$ sudo bash setup.bash
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

### Testing server with wrk
To test a sample workload on nginx server:
```bash
$ bash test.sh
```

