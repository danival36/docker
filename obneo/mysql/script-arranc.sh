/usr/sbin/cron &&
#mysqld --user=root &&
mysqld_safe &&
echo mysql engegat >> /var/log/cron.log
sleep 5 &&
/usr/iula/backup/script.sh
echo insertem variables mysql >> /var/log/cron.log
service mysql stop &&
echo parem mysql >> /var/log/cron.log
sleep 5 &&
echo engeguem mysql >> /var/log/cron.log
mysqld --user=root 
