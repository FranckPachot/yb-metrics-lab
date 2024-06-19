
Lab to run queries on YugabyteDB and display metrics, all from Grafana

- YugabyteDB master:  localhost:7000
- YugabyteDB tserver: localhost:9000
- Prometheus:         localhost:9090
- Grafana:            localhost:3000

Run with: `docker compose up -d`

You can start and get a psql shell with:
```
alias psql='docker compose up -d --no-recreate && docker compose run -it pgbench psql'
psql

```

## Example:

![image](https://github.com/FranckPachot/yb-metrics-lab/assets/33070466/f008e2a4-1d0f-4d78-9c2b-c3838cc3da6f)

There's also an experimental prometheus exporter for PostgreSQL auto_explain:
./config/auto_explain_exporter.py

## labs

### PgBench

You can run pgbench:
```
docker compose run --rm -it pgbench bash

# without connection pool
pgbench -c 20 -h yugabytedb -T 300 -P 1 -n
# with connection pool
pgbench -c 20 -h pgbouncer  -T 300 -P 1 -n
```

### COPY

Here is what I've used to test memory allocation with large files copy:
```
docker compose down 
docker compose up --scale pgbench=0 -d
docker compose exec -it yugabytedb ysqlsh -h yugabytedb

drop table if exists demo, demo_ref;
create table demo_ref ( id int primary key );
insert into demo_ref 
select distinct (100*random())::int from generate_series(1,1000);
create table demo ( id int generated always as identity, ref int default 100*random() references demo_ref, data text, primary key(id asc) );
-- begin transaction;
copy demo(data) from program 'base64 -w 100 /dev/urandom | head -c $(( 1024 * 1024 * 1024 ))';
-- commit;

\! yb-ts-cli -server_address yugabytedb flush_all_tablets
select pg_size_pretty(pg_table_size('demo'));
explain analyze select * from demo order by id;
\! yb-ts-cli -server_address yugabytedb compact_all_tablets
create table demo2 as select * from demo;

```
There are some interesting stats in the Memory dashboard

