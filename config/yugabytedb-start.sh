if [ -f /tmp/.yb.$(hostname -i):5433/.s.PGSQL.5433.lock ] 
then
 rm /tmp/.yb.$(hostname -i):5433/.s.PGSQL.5433.lock
fi
yugabyted start --tserver_flags='flagfile=/etc/yugabyte/tserver.flags' --master_flags='flagfile=/etc/yugabyte/master.flags'
until postgres/bin/pg_isready -h $(hostname) ; do sleep 1 ; done
pip install prometheus_client
# this is experimental:
(
while true
do
python /etc/yugabyte/auto_explain_exporter.py $( ysqlsh -h $(hostname) -tAc "select pg_current_logfile()" )
done
) &
# show the logs
yugabyted status
cd /root/var/logs
tail -F yugabyted.log master.err tserver.err tserver/postgresql-*.log
