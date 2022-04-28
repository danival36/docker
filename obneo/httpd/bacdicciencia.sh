# [10/01/2013] mcg Backup bd i dades de dicCiencia
# arxius modificats les darreres 24h al directori /var/www/terminus2.0/ (normalment estaran a resultados, corpus i validados)
# s'executa de dilluns a divendres a la 1:00h.
# guardem els backups al mateix directori que l'script

dia=`date +%a`
#data=`date +%Y.%m.%d`

logfile="/usr/iula/backup/DicCiencia$dia.log"
sqlfile="/usr/iula/backup/DicCiencia$dia.sql"
dadesfile="/usr/iula/backup/DicCiencia$dia.tgz"


echo "Inici de la copia: `date`" > $logfile

/usr/bin/mysqldump -u club -p3Wsxcde4 dicCiencia > $sqlfile
gzip -f $sqlfile


# mirem espai lliure en Kb al disc on es fan els backups
#espai_lliure=`df -P | grep /dev/mapper/vmbasic-root | awk '{print $2}'`
# calculem espai ocupat pels arxius modificats (dividim per 1024 perque el resultat es en bytes)
#espai_dades=`find /var/www/terminus2.0/ -type f -mtime -1 -exec ls -l {} \; | awk 'BEGIN{total=0;} {total += $5;} END{print total}'`
#espai_dades=`expr $espai_dades / 1024`

# nomes copiem les dades si com a minim  queden 2 Gb lliures despres de la copia (sense comprimir)
#if [ $espai_lliure -gt `expr $espai_data + 2000000` ]
#then find /var/www/terminus2.0/ -type f -mtime 1 -print | tar cvzf $dadesfile -T -
#else echo "Espacio de disco insuficiente. NO se copian archivos" >> $logfile 
#fi

echo "Fi de la copia: `date`" >> $logfile
