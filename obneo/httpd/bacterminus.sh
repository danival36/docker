# [10/01/2013] jci Backup bd i dades de Terminus2.0
# arxius modificats les darreres 24h al directori /var/www/terminus2.0/ (normalment estaran a resultados, corpus i validados)
# s'executa de dilluns a divendres a la 1:00h.
# guardem els backups al mateix directori que l'script

dia=`date +%a`
#data=`date +%Y.%m.%d`

DATADIR="/var/www/terminus/terminus2.0"
logfile="/usr/iula/backup/Terminus_$dia.log"
sqlfile="/usr/iula/backup/Terminus_$dia.sql"
dadesfile="/usr/iula/backup/Terminus_$dia.tgz"


echo "Inici de la copia: `date`" > $logfile

/usr/bin/mysqldump -u rog -pfenixiula terminalB > $sqlfile
gzip -f $sqlfile


# mirem espai lliure en Kb al disc on es fan els backups
#espai_lliure=`df -P | grep /dev/mapper/vmbasic-root | awk '{print $2}'`
# calculem espai ocupat pels arxius modificats (dividim per 1024 perque el resultat es en bytes)
#espai_dades=`find $DATADIR -type f -mtime -1 -exec ls -l {} \; | awk 'BEGIN{total=0;} {total += $5;} END{print total}'`
#espai_dades=`expr $espai_dades / 1024`

# nomes copiem les dades si com a minim  queden 2 Gb lliures despres de la copia (sense comprimir)
#if [ $espai_lliure -gt `expr $espai_data + 2000000` ]
#then find $DATADIR -type f -mtime 1 -print | tar cvzf $dadesfile -T -
#else echo "Espacio de disco insuficiente. NO se copian archivos" >> $logfile 
#fi

echo "Inici copia arxius nous: `date`" > $logfile
find $DATADIR -type f -mtime 1 -print | tar cvzf $dadesfile -T -

# Un cop feta la copia esborrem els arxius d'analisi que tenen mes de 90 dies
echo "Esborrem arxius de resultats antics: `date`" > $logfile
echo "Arxius esborrats:" >> $logfile
find $DATADIR/resultados/ -type f -mtime +90 -regex '.*/[0-9]*$' -print  -exec rm {} \; | tee -a $logfile | awk -F"/" '{print "DELETE from Analisis WHERE Id="$NF";"}' | mysql -u rog -pfenixiula terminalB

# Fem neteja dels usuaris demo amb mes de 90 dies
echo "Inici neteja directoris usuaris demo: `date`" > $logfile
demo_ids=`mysql -u rog -pfenixiula terminalB \
-e 'select id from Usuario where DATE_ADD(fecha, INTERVAL 90 DAY) < CURDATE() AND status=-634;' | grep -v "id"`

# esborrem els directoris creats per aquests usuaris a /var/www/esten/Usuarios
echo "Directoris esborrats: " >> $logfile
[ "$demo_ids" != "" ] && for id in $demo_ids
do
        userdir="/var/www/terminus/terminus2.0/corpus/userID$id"
        [ "$id" != "" ] && [ -d $userdir ] && du -s $userdir >> $logfile && rm -r $userdir
        userdir="/var/www/terminus/terminus2.0/resultados/userID$id"
        [ "$id" != "" ] && [ -d $userdir ] && du -s $userdir >> $logfile && rm -r $userdir
done

# esborrem entrades de les taules Analisis, Documento, Usuario, Proyecto y Termino
# posem id a suprimir separts per coma
demo_ids_IN=`echo $demo_ids | tr " " ,`
echo "Inici neteja BD usuaris demo: `date`" > $logfile
echo " Netegem BD ids: $demo_ids_IN" >> $logfile
[ "$demo_ids_IN" != "" ] && mysql -u rog -pfenixiula terminalB << EOSQL >> $logfile 
DELETE FROM Analisis WHERE usuario IN ($demo_ids_IN);
DELETE FROM Documento WHERE usuario IN ($demo_ids_IN);
DELETE FROM Usuario WHERE id IN ($demo_ids_IN);
DELETE FROM Proyecto, Termino USING Proyecto, Termino WHERE Proyecto.id = Termino.proyecto AND (Proyecto.idautor)IN ($demo_ids_IN);
EOSQL

echo "\nFi de la copia: `date`" >> $logfile
