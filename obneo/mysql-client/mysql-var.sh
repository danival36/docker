touch mysql.log
echo "s'executa" >> mysql.log
mysql -u root -pthevolumepaper -h db_obneodevel obneonetPL < script.sql
