# cat bacobneo
# Backup bd Observatori de Neologia
# s'executa de dilluns a divendres a les 21:00h.

dia=`date +%a`

# Bd de l'obneo i plataforma
sqlfile="/var/lib/mysql/backup/Obneo_$dia.sql"
logfile="/var/lib/mysql/backup/Obneo_$dia.log"

echo "Inici de la copia: `date`" > $logfile

/usr/bin/mysqldump -u obneonetPL_usr -pnaing2qu obneonetPL > $sqlfile

echo "Inici de la compresio: `date`" > $logfile
gzip -f $sqlfile

echo "Final de la copia: `date`" >> $logfile

# Bd del projecte APLE
# de moment no fem backup d'APLE
#sqlfile="ObneoAPLE_$dia.sql"
#logfile="ObneoAPLE_$dia.log"

#echo "Inici de la còpia: `date`" > $logfile

#/usr/bin/mysqldump -u obneonetGD_usr  -pnaing2qu obneonetGD > $sqlfile
#gzip -f $sqlfile

#echo "Final de la còpia: `date`" >> $logfile
