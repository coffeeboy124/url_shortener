from flask import Flask, url_for, request, json
import MySQLdb, sys

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

#Connecting to the MySQL database. Set parameters in the ini file
try:
    db = MySQLdb.connect(host="localhost",    # your host, usually localhost
						 user="root",         # your username
						 passwd="password",   # your password
						 db="noobcentral") 	  # your database
    cursor = db.cursor()        
    cursor.execute("""CREATE TABLE IF NOT EXISTS links (
					  link_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
					  link varchar(255),
					  link_key varchar(64),
					  PRIMARY KEY (link_id))""")	
except MySQLdb.Error:
	sys.exit("ERROR IN CONNECTION")

#Setting up the server.
app = Flask(__name__)	

#Main page. User sends url post request and gets a encoded url as a response.
@app.route('/', methods = ['GET', 'POST'])
def api_root():

	if request.method == 'GET':
		return "ECHO: GET\n"

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
					return "localhost:5000/" + key
					
				#if the url is in the table, we just return the link key
				else:
					return "localhost:5000/" + cursor.fetchone()[2]		
			except MySQLdb.Error:
				return "Something blew up in the sql query"
		else:
			return "You need to have a url key in the json request. See the readme!"
	else:
		return "You need to send a json request. See the readme!";

#Encoded url page. Returns the website link.		
@app.route('/<link_key>')
def api_link_key(link_key):
	try:
		cursor.execute("""SELECT * FROM links 
						  WHERE link_key = %s""", (link_key,))
		if cursor.rowcount == 0:
			return "invalid key"
		else:
			return cursor.fetchone()[1]
	except MySQLdb.Error:
		return "Something blew up in the sql query"

app.run()


