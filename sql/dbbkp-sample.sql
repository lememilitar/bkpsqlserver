BACKUP DATABASE [databasename] TO DISK=[bkp_file_path]
BACKUP LOG [databasename] WITH truncate_only
DBCC Shrinkfile('Teste_Log',1)