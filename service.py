# damei@dameiSolutions
	import socket
	import fcntl
	import struct
	import socket
	import threading 
	import time
	import json
	import hashlib

	def get_ip_address(ifname):
	    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s', ifname[:15]))[20:24])

	try :
		SELF_IP = get_ip_address('eth0')
	except IOError :
		SELF_IP = get_ip_address('wlan0')	

	BROKER = '127.0.0.1'
	BROKER_UDP_PORT = 6068
	BROKER_UDP_REGISTRY_NODE_PORT = 6069
	BROKER_UDP_LCOATE_NODE_PORT = 6070
	NODE_UDP_PORT = 6071
	CALL_TCP_PORT_SND = 6072
	CALL_TCP_PORT_RCV = 6073
	CALL_VOICE_TRNSFR_PORT = 6074
	CALL_PORT = 6002
	MAX = 40000
	MAX_DGRAM = 40000

	DEVICE_HANDLER_PORT = 6003
	THREAD_CONTROLLER = 4


	class nodeHandler:
		## class initializer ##
		def __init__(self) :
			self.connectedDevices = { '966':{'ip' : '192.30.20.30' , 'status' : True } , '977':{'ip' : '192.12.43.21' , 'status' : True }, '988':{'ip' : '192.23.43.22' , 'status' : True },}
			self.pft = {}
			#self.deviceHandler()
			self.isFree = True	
			self.brokerRegistry()
			self.authDict = {}
			thread1 = threading.Thread( target = self.nodeUDPReciever , args = ())
			thread1.start()
			#thread2 = threading.Thread( target = self.statusInformer , args = ())
			#thread2.start()

		def md5(self,string) : 
			hashlib.md5.update()


		def brokerRegistry(self) :
			broRegSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			broRegSock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
			broRegSock.bind(('',BROKER_UDP_REGISTRY_NODE_PORT))
			broRegSock.settimeout(0.5)
			for phone in self.connectedDevices.keys() :
				#broRegSock.sendto('REGISTRY-' + json.dumps({phone:self.connectedDevices[phone]['ip']}),(BROKER,BROKER_UDP_PORT))
				broRegSock.sendto('REGISTRY-' + json.dumps({phone:SELF_IP}),(BROKER,BROKER_UDP_PORT))
				while True :
					data , address = broRegSock.recvfrom(MAX)
					if data == '200' :
						if address == (BROKER,BROKER_UDP_PORT) :
							break

		def nodeUDPReciever(self) :
			nodeUdpSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			nodeUdpSock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
			nodeUdpSock.bind(('',NODE_UDP_PORT))
			while True :
				data , address = nodeUdpSock.recvfrom(MAX)
				if 'PAIR-' in data :
					data = data.split('PAIR-')[1]
					self.connectedDevices.update({data:{ip:address[0],'status':True}})
					self.brokerRegistry()
				elif 'REM-AUTH-' in data :
					time.sleep(0.5)
					data = json.loads(data.split('AUTH-')[1])
					if data['to'] in self.authDict.keys() :
						if self.authDict[data['to']] == data['access_code'] :
							if self.connectedDevices[data['to']]['status'] :
								self.connectedDevices[data['to']]['status'] = False
								self.start_call(data)
					else :
						time.sleep(1)			
						if data['to'] in self.authDict.keys() :
							if self.authDict[data['to']] == data['access_code'] :
								if self.connectedDevices[data['to']]['status'] :
									self.connectedDevices[data['to']]['status'] = False
									self.start_call(data)
									

				elif 'ADV-AUTH-' in data :
					data = json.loads(data.split('ADV-AUTH-')[1])
					self.authDict.update({data['to']:data['access_code']})


		def locate(self,phoneNum,initNum) :
			locateSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)		
			locateSock.bind(('',BROKER_UDP_LCOATE_NODE_PORT))		
			locateSock.settimeout(1)
			locateSock.sendto('LOCATE-' + phoneNum + 'LOCATE-' + initNum,(BROKER,BROKER_UDP_PORT))
			data , address = locateSock.recvfrom(MAX)
			return data

		def call(self,phoneNum,initNum) :
			locateDict = json.loads(self.locate(phoneNum,initNum))
			if locateDict['location'] == 'OFFLINE' :
				print locateDict['to'] + ' is not available :-( '
			else :
				print locateDict['to'] + ' is at ' + locateDict['location']
			authSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			authSock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
			authSock.sendto('REM-AUTH-' + json.dumps(locateDict),(locateDict['location'],NODE_UDP_PORT))
			

		def start_call(self,data) :
			inThread = threading.Thread(target = self.inVoice , args = (data,))
			outThread = threading.Thread(target = self.outVoice , args = (data,))
			inThread.start()
			outThread.start()

		def inVoice(self,data) :
			try :
				inVoiceSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				trnsfrVoiceSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				inVoiceSock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
				trnsfrVoiceSock.connect((self.connectedDevices[data['to']]['ip'],CALL_TCP_PORT_SND))
				inVoiceSock.bind(('',CALL_TCP_PORT_RCV))
				inVoiceSock.listen(1)
				conSock , sc_detail_ = inVoiceSock.accept()
				while True :
					voice = conSock.recv(MAX)
					trnsfrVoiceSock.send(voice)
			except :
				self.connectedDevices[data['to']] = True

		def outVoice(self,data) :
			try :
				outVoiceSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				trnsfrVoiceSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				trnsfrVoiceSock.bind(('',CALL_TCP_PORT_SND))
				outVoiceSock.connect((data['to'],CALL_TCP_PORT_SND))
				while True :
					voice = trnsfrVoiceSock.recv(MAX)
					outVoiceSock.send(voice)				
					pass
			except :
				self.connectedDevices[data['to']] = True 

	dialer = nodeHandler()

	dialer.call('966','977')
