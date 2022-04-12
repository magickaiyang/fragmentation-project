# fragmentation-project

## Redis benchmark

### Download and Compile Redis
To compile Redis:
```bash
$ make install
```

After building Redis, to test it using: 
```bash
$ make tests
```

If you get an error message of
```
You need tcl 8.5 or newer in order to run the Redis test
```

Try to install tcl with:
```
$ apt install tcl
```

### Start Redis Server

```
./server/server-start.sh
```

### Run Redis benchmark
```
./client/run.py
```

