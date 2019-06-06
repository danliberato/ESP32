# Import socket module 
#https://gist.github.com/giefko/2fa22e01ff98e72a5be2
import socket 
import sys
import json
import os
import time

max_buffer_size = 1024
#host = "localhost"
host = "192.168.4.1"
port = 8888
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def Main(): 
	
	try:
		soc.connect((host, port))
	except Exception as err:
		print("Connection error: ", err)
		sys.exit()
		
	print('[ Options ]')
	options()

	opt = ''
	while opt != 'x':
		opt = input('>')
		if opt == 's': 					# SEND FILE TO SERVER
			soc.send(opt.encode())		#send option to server
			nome = input('Select the file: '+os.getcwd()+'/')

			if os.path.exists(nome):
				#time.sleep(1)
				soc.send(nome.encode())	#send file name to server
				#time.sleep(1)
			
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

		elif opt == 'r':				# RECEIVE FILE FROM SERVER
			soc.send(opt.encode())		#send option to server
			f_name = input('Nome do arquivo a ser recebido: ')
	
			soc.send(f_name.encode())
			time.sleep(1)
			response = soc.recv(2).decode()
			if response == '!f':
				
				f_size = int(soc.recv(6).decode()) #receive file size
				#f_size = receive_input(soc,max_buffer_size)
				
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
		elif opt == 'd':				#DELETE A FILE
			soc.send(opt.encode())
		else:				#default
			print('Please select an option...')
			options()
	
	soc.send(opt.encode())
	soc.close()
	sys.exit()
	
def receive_input(connection, max_buffer_size):
	client_input = connection.recv(max_buffer_size)
	client_input_size = sys.getsizeof(client_input)

	if client_input_size > max_buffer_size:
		print("The input size is greater than expected {}".format(client_input_size))

	result = client_input.decode().rstrip()  # decode and strip end of line

	return result


def options():
	print('  s : Send a file')
	print('  d : Delete a file')
	print('  r : Receive a file')
	print('  x : Exit')

if __name__ == '__main__': 
	Main()
