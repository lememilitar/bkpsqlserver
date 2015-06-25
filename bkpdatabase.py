import config

import smtplib
from datetime import datetime
import os
import subprocess
from email.message import Message
import zipfile
try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

directory = ''
log = ''
disk = ''

def backup_mmsql():
  now = datetime.now()
  global log
  global directory
  global disk
  for database,dataconfig in config.databases.items():
    log = ''
    directory = dataconfig['bkpbasedir']+str(now.year)+'/'+str(now.month)+'/'+str(now.day)+'/'
    filename = database+'-'+str(now.year)+str(now.month)+str(now.day)+'.bak'
    disk = directory+filename
    create_bkp_folders()
    create_file_to_run_bkp(database)
    run_command()
    compact_file()
    write_log_file()
    msg = 'Backup da base '+ database +' no servidor '+ config.dbserver+' foi realizado.'
    msg += 'Saida do programa: '+str(log)
    send_mail(dataconfig['subject'],msg)


def create_bkp_folders():
  global directory
  global log
  if not os.path.exists(directory):
      os.makedirs(directory)
      log+="create folder "+directory+"- "+get_hour_now()+"\n"

def create_file_to_run_bkp(dbname):
  global disk
  file = open(os.path.dirname(os.path.realpath(__file__))+"/sql/dbbkp.sql","w")
  file.write("use "+dbname+"\n")
  file.write("BACKUP DATABASE "+dbname+" TO DISK='"+disk+"' \n")
  file.write("BACKUP LOG "+dbname+" WITH truncate_only\n")
  #file.write("DBCC Shrinkfile('Teste_Log',1)")
  file.close()

def run_command():
  global disk
  global log
  print('Start backup')
  log+="Start backup: "+disk+" - "+get_hour_now()+"\n"

  output = subprocess.call('sqlcmd -S '+ config.dbserver +' -U '+ config.u +' -P '+ config.p + ' -i "'+os.path.dirname(os.path.realpath(__file__))+'/sql/dbbkp.sql"')
  log += "End backup: "+disk+" - "+get_hour_now()+"\n"

def compact_file():
  global disk
  global log
  print('Start Compact file: '+disk)
  log+="Start Compact file: "+disk+" - "+get_hour_now()+"\n"
  zf = zipfile.ZipFile(disk.replace('.bak','.zip'), mode='w')
  if os.path.isfile(disk):
      try:
          zf.write(disk, compress_type=compression)
      finally:
          print('closing compress')
          log+="Ended Compact file: "+disk+" - "+get_hour_now()+"\n"
          zf.close()

      #delete the file
      print('Deleting '+disk)
      log+="Deleting "+disk+" - "+get_hour_now()+"\n"
      os.remove(disk)
  else:
      print('File not exists')
      log+="File "+disk+" not exists - "+get_hour_now()+"\n"

  print("Log: "+log)

def write_log_file():
  global disk
  global log
  logfile = open(disk.replace('.bak','.log'),"w")
  logfile.write(log)
  logfile.close()

def send_mail(subject,msg):
  try:
    msg1 = Message()
    msg1['Subject'] = subject
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

def get_hour_now():
  return "hour["+str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"]"

if __name__ == '__main__':
  backup_mmsql()
  print(log)