import config

__author__ = 'George Moura'

import smtplib
import datetime
import os
import subprocess
from email.message import Message


now = datetime.datetime.now()
directory = config.bkpbasedir+str(now.year)+'/'+str(now.month)+'/'+str(now.day)+'/'
filename = config.dbname+'-'+str(now.year)+str(now.month)+str(now.day)+'.bak'
disk = directory+filename
log = ''

#create bkp folders
if not os.path.exists(directory):
    os.makedirs(directory)
    log+="create folder "+directory+"- "

#create a file to run bkp
file = open(os.path.dirname(os.path.realpath(__file__))+"/sql/dbbkp.sql","w")
file.write("BACKUP DATABASE "+ config.dbname+" TO DISK='"+disk+"' \n")
file.write("BACKUP LOG "+ config.dbname+" WITH truncate_only\n")
file.write("DBCC Shrinkfile('Teste_Log',1)")
file.close()
#run bat to create a backup
print('Starting backup')
log+="Starting backup "+disk+"\n"

output = subprocess.call('sqlcmd -S '+ config.dbserver +' -U '+ config.u +' -P '+ config.p + ' -i "'+os.path.dirname(os.path.realpath(__file__))+'/sql/dbbkp.sql"')
log += "Backup file "+disk+" ended\n"

#compact the file
print('Compact the file '+disk)
log+="Compact the file "+disk+"\n"
output += subprocess.call(config.rarpath+' a '+disk.replace('.bak','.rar')+' '+disk)
#delete the file
print('Deleting '+disk)
log+="Deleting "+disk+"\n"
os.remove(disk)

print("Log: "+log)

#write log file
logfile = open(disk.replace('.bak','.log'),"w")
logfile.write(log)
logfile.close()

#send mail
msg = 'Backup da base '+ config.dbname+' no servidor '+ config.dbserver+' foi realizado.'
msg += 'Saida do programa: '+str(log)

try:
  msg1 = Message()
  msg1['Subject'] = config.subject
  msg1['From'] = config.fromaddr
  msg1['To'] = config.toaddrs
  msg1.set_payload(msg)
  print('Enviando Mensagem...\n')
  print(msg1)
  serv=smtplib.SMTP(config.smtpserver,config.smtpport)
  #serv.ehlo()
  #serv.starttls()
  serv.login(config.mailuser, config.mailpass)
  serv.sendmail(msg1['From'], msg1['To'], msg1.as_string())
  serv.quit()
except Exception as e:
  print("Erro " , e)
else:
  print("Enviado!")