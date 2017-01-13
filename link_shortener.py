from flask import Flask, url_for, request, json, redirect
import MySQLdb, sys, ConfigParser

#Config reader helper method. Taken from online
def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

#Base62(0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ) encoding algorithm. Taken from online
def encode(num, alphabet="123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    if num == 0:
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        num, rem = divmod(num, base)
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)

	
#Read in variable from settings.ini
Config = ConfigParser.ConfigParser()
Config.read("settings.ini")
host = ConfigSectionMap("Database")['host']					   #your host, usually localhost
user = ConfigSectionMap("Database")['user']					   #your username
password = ConfigSectionMap("Database")['passwd']			   #your password
database_name = ConfigSectionMap("Database")['database_name']  #your database name
port = ConfigSectionMap("Server")['port']					   #your port number
is_redirect = ConfigSectionMap("Server")['is_redirect']		   #does the server redirect you to the url? Is either "ON" or "OFF"

#Connecting to the MySQL database. Set parameters in the ini file
try:
    db = MySQLdb.connect(host, user, password, database_name)
    cursor = db.cursor()        
    cursor.execute("""CREATE TABLE IF NOT EXISTS links (
					  link_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
					  link varchar(255),
					  link_key varchar(64),
					  PRIMARY KEY (link_id))""")	
except MySQLdb.Error:
	sys.exit("ERROR IN DATABASE CONNECTION")

#Setting up the server.
app = Flask(__name__)	

#Main page. User sends url post request and gets a encoded url as a response.
@app.route('/', methods = ['GET', 'POST'])
def api_root():

	if request.method == 'GET':
		return "yay it works"

	elif request.method == 'POST' and request.headers['Content-Type'] == 'application/json':
		dataDict = json.loads(request.data)	
		if 'url' in dataDict.keys():
			try:
				url = dataDict.get('url')
				#check if url is in the table
				cursor.execute("""SELECT * FROM links 
								  WHERE link = %s""", (url,))
								  
				#if the url is not in the table, we add it and encode its key using the primary_id number
				if cursor.rowcount == 0:
					cursor.execute("""INSERT INTO links (link) 
									  VALUES (%s)""", (url,))
					key = encode(cursor.lastrowid)
					cursor.execute("""UPDATE links SET link_key = %s
									  WHERE link_id = %s""", (key, cursor.lastrowid,))
					db.commit()
					return "{'response': 'localhost:" + port + "/" + key + "'}"
					
				#if the url is in the table, we just return the link key
				else:
					return "{'response': 'localhost:" + port + "/" + cursor.fetchone()[2] + "'}"		
			except MySQLdb.Error:
				return "{'response': 'Something blew up in the sql query'}"
		else:
			return "{'response': 'You need to have a url key in the json request. See the readme!'}"
	else:
		return "{'response': 'You need to send a json request. See the readme!'}";

#Encoded url page. Returns the website link.		
@app.route('/<link_key>')
def api_link_key(link_key):
	try:
		cursor.execute("""SELECT * FROM links 
						  WHERE link_key = %s""", (link_key,))
		if cursor.rowcount == 0:
			return "{'response': 'invalid key'}"
		else:
			if is_redirect == "OFF":
				return "{'response': '" + cursor.fetchone()[1] + "'}"
			else:
				return redirect(cursor.fetchone()[1])
	except MySQLdb.Error:
		return "{'response': 'Something blew up in the sql query'}"

#Run the server!
app.run(port = port)


