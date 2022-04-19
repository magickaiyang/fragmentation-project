# fragmentation-project

## Benchbase
Benchmark repository: https://github.com/cmu-db/benchbase
### Download and compile

Make sure JDK version is 17.
```
$ git clone --depth 1 https://github.com/cmu-db/benchbase.git

$ cd benchbase

$ ./mvnw clean package -P mysql
```

### Set up MySQL server
```
mysql -u root -p
```
In MySQL,
```
CREATE DATABASE benchbase;
```
### Change configure file
In `config/mysql/sample_tpcc_config.xml` and `config/mysql/sample_ycsb_config.xml`
<username>root</username>
<password>MySQL2022.</password>

### Run commands
```
$ ./mvnw clean package

$ cd target

$ tar xvzf benchbase-2021-SNAPSHOT.tgz

$ cd benchbase-2021-SNAPSHOT
```
Run tpcc:
```
$ java -jar benchbase.jar -b tpcc -c config/mysql/sample_tpcc_config.xml --create=true --load=true --execute=true
```
Run ycsb:
```
$ java -jar benchbase.jar -b ycsb -c config/mysql/sample_ycsb_config.xml --create=true --load=true --execute=true
```
### Possible errors:
1. java.sql.SQLException: Access denied for user 'admin'@'localhost' (using password: YES)
Set up username and password in xml file

2. java.sql.SQLSyntaxErrorException: Unknown database 'benchbase'
CREATE DATABASE benchbase;

3. Exception in thread "main" java.lang.RuntimeException: Failed to retrieve class for com.oltpbenchmark.benchmarks.tpcc.procedures.ReadRecord
Benchmark specified not fit for xml file

4. Need to rebuild whole package after changing xml file

5. [ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.10.0:compile (default-compile) on project benchbase: Fatal error compiling: error: invalid target release: 17 -> [Help 1]


## Redis

### Download and compile
http://download.redis.io/releases/redis-6.2.6.tar.gz

### Start server
```bash
redis-server
```

### 

## Memcached

https://github.com/RedisLabs/memtier_benchmark


