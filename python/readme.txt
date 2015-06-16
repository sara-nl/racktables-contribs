Installation instructions

1) Download the file to your PC. A working racktables installation is assumed. No harm can be done since all the operations towards the database are select like.

2) Install the following:
  2.0) sudo apt-get install python 
  2.1) sudo apt-get install python-mysqldb
  2.2) sudo apt-get install graphviz
  2.3) sudo apt-get install python-pip
  2.4) sudo pip install graphviz
  
3) Configure the IP/user/pass access data for the MySQL server in the python script:

    db = MySQLdb.connect(host="127.0.0.1", 	# your host, usually localhost
                   	     port=3306,
                         user="user", 			# your username
                         passwd="pass", 	# your password
                         db="racktables") 		# name of the data base

4) In order to build a topology, properly tag all your routers with the same tag.

5) Run the script and invoke the tag used at step 4.

enjoy!
  
