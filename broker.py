import socket
import threading
import json
import random
import hashlib
	
BROKER = '127.0.0.1'
BROKER_UDP_PORT = 6068
BROKER_UDP_REGISTRY_NODE_PORT = 6069
BROKER_UDP_LCOATE_NODE_PORT = 6070
NODE_UDP_PORT = 6071
CALL_TCP_PORT_SND = 6072
CALL_TCP_PORT_RCV = 6073
MAX = 50000

def md5(string) :
    hasher = hashlib.md5()
    hasher.update(string.lower())
    return hasher.hexdigest().lower()

class brokerHandler:
	def __init__(self) :
		self.onlineDevices = {}
		thread1 = threading.Thread( target = self.brokerUDPReciever , args = ())
		thread1.start()
		thread1.join()

	def brokerUDPReciever(self) :
		broUdpSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		broUdpSock.bind(('',BROKER_UDP_PORT))
		broUdpSock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		while True :
			data , address = broUdpSock.recvfrom(MAX)
			if 'REGISTRY-' in data :
				self.onlineDevices.update(json.loads(data.split('REGISTRY-')[1]))
				broUdpSock.sendto('200',address)
			print '\n'
			for key,value in self.onlineDevices.iteritems() :
				print key,value
			print '\n'
			if 'LOCATE-' in data :
				key = data.split('LOCATE-')[1]
				access_code = md5(str(random.randrange(0,10000000)))
				try :
					location = self.onlineDevices[key]
				except KeyError :
					location = 'OFFLINE'
				reply = { 'for' : key , 'location' : location , 'access_code' : access_code}
				print reply
				broUdpSock.sendto('REQ-AUTH-'+json.dumps(reply),(reply['location'],NODE_UDP_PORT))				
				broUdpSock.sendto(json.dumps(reply),address)
				
				
				
app = brokerHandler()

