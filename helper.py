import threading 
import socket

def broadcast(subnet,THREAD_CONTROLLER,phoneNum,BROADCAST_PORT) :
	for i in range(0,50) :
		thread = threading.Thread( target = addr4, args = ( subnet + str(i),phoneNum , THREAD_CONTROLLER,BROADCAST_PORT))
		thread.start()
	
def addr5(ip,start,end,phoneNum,BROADCAST_PORT) :
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
	s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
	for i in range(start,end) :
		#print start , ' - ' , end  , '\n'
		try :
			s.sendto(str(phoneNum),(ip+'.'+str(i),BROADCAST_PORT))
		except socket.error as error :
			pass

def addr4(ip,phoneNum,THREAD_CONTROLLER,BROADCAST_PORT) :
	global counter
	for i in range(0,THREAD_CONTROLLER) :
		thread = threading.Thread( target = addr5, args = (ip,i*(256/THREAD_CONTROLLER),(i+1)*(256/THREAD_CONTROLLER),phoneNum,BROADCAST_PORT))
		thread.start()