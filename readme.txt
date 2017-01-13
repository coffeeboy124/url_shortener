Author: Daniel Mao

Task: The service should take a long url, and output a shortened version of that
url. When the user navigates to the shortened version of the url it should
redirect them to the long url.

Python library requirements:
flask, MySQLdb, sys, ConfigParser

!!!Make sure to set the right variables in the settings.ini file. You need to put in your sql user, password, and database!!!
How to Run:
1. Download and unpack files to desired directory
2. Open terminal and cd to that directory
3. Type python link_shortener.py

Once you have the server running, you can encode urls by sending them to it via a POST request. Example below:

> curl -H "Content-type: application/json" -X POST localhost:5000 -d '{"url":"https://www.yahoo.com/"}'
	1. This example assumes that the port is 5000, it can be whatever you set it to be in the settings.ini file
	2. You must include "Content-type: application/json"
	3. You must send the data in the following format {"url": XXX}

The server responds with an encoded URL, which you can follow using a GET request. Example below:

> curl -H "Content-type: application/json" -X POST localhost:5000 -d '{"url":"https://www.yahoo.com/"}'
> {'response': 'localhost:5000/r'}
> curl localhost:5000/r
	1. This example assumes that the port is 5000, it can be whatever you set it to be in the settings.ini file

TODO: Right now the program encodes any string sent at it. Add a string checker to see if it is a valid link.