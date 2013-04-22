#!/opt/bin/python2.6

import serial
import psycopg2
import datetime
import socket
import io
import json

class Teleinfo:

	ser = serial.Serial()
	
	def __init__ (self, port='/dev/ttyUSB0'):
		self.ser = serial.Serial(port, baudrate=1200, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN)
	
	def checksum (self, etiquette, valeur):
		sum = 32
		for c in etiquette: sum = sum + ord(c)
		for c in valeur: 	sum = sum + ord(c)
		sum = (sum & 63) + 32
		return chr(sum)
		
	def read (self):
		# Attendre le debut du message
		while self.ser.read(1) != chr(2): pass
		
		message = ""
		fin = False
		
		while not fin:
			char = self.ser.read(1)
			if char != chr(3):
				message = message + char
			else:
				fin = True
		
		trames = [
			trame.split(" ")
			for trame in message.strip("\r\n\x03").split("\r\n")
			]
			
		tramesValides = dict([
			[trame[0],trame[1]]
			for trame in trames
			if ( (len(trame) == 3) and (self.checksum(trame[0],trame[1]) == trame[2])
			   or(len(trame) == 4) and (self.checksum(trame[0],trame[1]) == ' ') )
			])
			
		return tramesValides

if __name__ == "__main__":
	ti = Teleinfo()
	db = psycopg2.connect("host=localhost dbname=houseonwire user=houseonwire")
	while True:
		data = ti.read()
		dbc = db.cursor()
		dbc.execute( "INSERT INTO teleinfo (isousc,hchc,hchp,ptec,iinst,imax,papp, date)\
			VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
			  (data["ISOUSC"], data["HCHC"], data["HCHP"], data["PTEC"][0:2],
			   data["IINST"], data["IMAX"], data["PAPP"],
			   datetime.datetime.now() ) )
		dbc.execute( "COMMIT;" );
		dbc.close()

		msg = { "PAPP":data["PAPP"], "HC":data["HCHC"], "HP":data["HCHP"], "PTEC":data["PTEC"] }
		msg[ "date" ] = str(datetime.datetime.now())
		msg = json.dumps( msg )
		print len(msg),msg
		content = io.BytesIO()
		content.write("\x01\x00")
		content.write( chr(len(msg)+1) )
		content.write( "\x00" )
		content.write( msg )
		content.write( "\n" )

		print content.getvalue()
		print content.getvalue()

		s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(("192.168.0.106", 6543))
		s.send(content.getvalue())
		s.close()
