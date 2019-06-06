import socket 
import sys
import json
import os
import time
from getpass import getpass

max_buffer_size = 1024
#host = "localhost"
host = "192.168.4.1"
port = 8888
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def Main(): 
	rootMode = False
	
	try:
		soc.connect((host, port))
	except Exception as err:
		print("Connection error: ", err)
		sys.exit()
		
	options()

	opt = ''
	while opt != 'x':
		opt = input('  > ').lower()
		if opt == 'send': 					# SEND FILE TO SERVER
			soc.send(opt.encode())		#send option to server
			nome = input('Select the file: '+os.getcwd()+'/')

			if os.path.exists(nome):
				
				soc.send(nome.encode())	#send file name to server
				
				f_size = os.path.getsize(os.getcwd()+'/'+nome)
				soc.send(str(f_size).encode())	#send file size to server
				
				if(soc.recv(2).decode() == '!s'):
				
					f = open(nome,'rb')
					data = ''
				
					print('Transfer initiated...')
					t_start = time.time()
					data = f.read(max_buffer_size)
					while (data):
					   soc.send(data)
					   data = f.read(max_buffer_size)
					f.close()
					t_stop = time.time()
				else:
					print("System out of space!")
				
				print('File transfer complete in',round(t_stop - t_start,3),'s')
			else:
				print('File not found.')

		elif opt == 'recv':				# RECEIVE FILE FROM SERVER
			soc.send(opt.encode())		#send option to server
			f_name = input('File name to be received: ')
	
			soc.send(f_name.encode())
			response = soc.recv(2).decode()
			if response == '!f':
				
				f_size = int(receive_input(soc))
				
				print(f_size,"btyes incoming...")
				with open(('rcv/'+f_name), 'wb') as f:
					while f_size > 0:
						data_buff = soc.recv(max_buffer_size)
						f_size -= len(data_buff)
						f.write(data_buff)
					
				print('File transfer complete!')
				f.close()
			else:
				print('File not found!')
		elif opt == 'del':				#DELETE A  vbiusgdf
			if not rootMode:
				print('You have to login as root before try that option!')
			else:
				soc.send(opt.encode())
				print('RCV= ',receive_input(soc))
			
		elif opt == 'root':
			soc.send(opt.encode())
			soc.send(getpass("Insert password:").encode())
			rootMode = receive_input(soc)
			print('You have','now' if rootMode else 'not', 'root privileges')
		
		else:				#default
			print('Please select an option...')
			options()
	
	soc.send(opt.encode())
	soc.close()
	sys.exit()
	
def receive_input(connection, max_size = max_buffer_size):
	client_input = connection.recv(max_buffer_size)
	client_input_size = sys.getsizeof(client_input)

	if client_input_size > max_buffer_size:
		print("The input size is greater than expected {}".format(client_input_size))

	result = client_input.decode().rstrip()  # decode and strip end of line

	return result


def options():
	print('  --- Options ---')
	print('  send : Send a file')
	print('  del : Delete a file')
	print('  recv : Receive a file')
	print('  root : Enter as root')
	print('  x : Exit')
	print('  ---------------')

if __name__ == '__main__': 
	Main()
