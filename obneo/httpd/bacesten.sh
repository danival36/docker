# Backup bd Esten
# s'executa de dilluns a divendres a les 22:00h.
# Aprofitem i fem neteja dels usuaris demo i les cookies

dia=`date +%a`
sqlfile="/usr/iula/backup/Esten_$dia.sql"
logfile="/usr/iula/backup/Esten_$dia.log"

# Netejem bd Esten d'usuaris demo i esborra tots els directoris creats per aquest usuaris
# ---------------------------------------------------------------

demo_ids=`mysql -u esten_usr -pg5b4r3l2r1 Esten \
          -e 'select id from Usuario where Mail="demo@demo";' | grep -v "id"`

# esborrem els directoris creats per aquests usuaris a /var/www/esten/Usuarios
[ "$demo_ids" != "" ] && for id in $demo_ids
do
  [ "$id" != "" ] &&  rm -r /var/www/esten/Usuarios/$id
done

# esborrem de tota la resta de taules els registres amb id d'usuaris demo
# i finalment esborrem de la taula Usuario tots els usuaris demo:
mysql -u esten_usr -pg5b4r3l2r1 Esten <<!
DELETE Corpus FROM Corpus INNER JOIN Usuario ON Usuario.id=Usuario_id where Mail='demo@demo';
DELETE Documento FROM Documento INNER JOIN Usuario ON Usuario.id=Usuario_id where Mail='demo@demo';
DELETE Usuario FROM Usuario WHERE Mail='demo@demo';
!

# netegem cookies antigues de /usr/lib/cgi-bin/esten/Cookies
find /usr/lib/cgi-bin/esten/Cookies -type f -mtime +5 -exec rm {} \;

# Despres de fer la neteja fem la copia de la bd. 

echo "Inici de la copia: `date`" > $logfile

mysqldump -uesten_usr -pg5b4r3l2r1 Esten > $sqlfile
gzip -f $sqlfile

echo "Final de la copia: `date`" >> $logfile
