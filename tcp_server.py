import errno
import sys
from gc import collect
import usocket as socket
from connection_handler import ConnectionHandler
try:
    import _thread
except ImportError:
    import _dummy_thread as _thread
import uos as os
import pin_handler
from micropython import mem_info as m_info

opt = ''
f_dir = '/rcv'
print_lock = _thread.allocate_lock()
max_buffer_size = 1024
rootPass = 'root'
led = pin_handler.pin4

# thread client
def clientThread(sock, ip, port):
    #try:
    rootMode = False
    while True:
        m_info()
        gc.collect()
        gc.mem_free()
        m_info()
        opt = sock.recv(max_buffer_size).decode()
        if (not opt) or (opt == 'exit'): #       QUIT
            sock.close()
            print("Connection " + ip + ":" + port + " closed!")
            break
        
        elif opt == 'send': #SEND FILE TO SERVER
            f_name = sock.recv(max_buffer_size).decode()
            f_size = int(sock.recv(max_buffer_size).decode())
            fs_space = checkSpace()
            print('Client', ip , ':' , port , 'wants to send a file [',f_size,'bytes of ',fs_space,']...')
            if(f_size < fs_space):
                sock.send(b'!s')
                with open((f_dir+"/"+f_name), 'wb') as f: 
                    while f_size > 0:
                        data_buff = sock.recv(max_buffer_size)
                        f_size -= len(data_buff)
                        f.write(data_buff)
                        led.value(not led.value())
                    f.close()
                    led.value(0)
                        
                print('File received from ['+ ip + ':' + port + ']',checkSpace(), 'Bytes left.')
            else:
                print('System out of space!')
                
        elif opt == 'recv': #SEND FILE TO CLIENT
            f_name = receive_input(sock)
            
            print('Client wants to receive file',f_name)
            try:
                f = open(f_dir+'/'+f_name, 'r')
                sock.send(b'!f')
                sock.send('{: <{fill}}'.format(os.stat(f_dir+'/'+f_name)[6],fill=max_buffer_size))

                print('Transfer initiated...')
                data = f.read(max_buffer_size)
                while (data):
                   sock.send(data)
                   data = f.read(max_buffer_size)
                   led.value(not led.value())
                
                led.value(0)
                f.close()
                print('File sent to ['+ ip + ':' + port+']')
                
            except OSError as exc:
                if exc.args[0] == errno.ENOENT:
                    print('File not found!')
                    sock.send(b'!n')
                else:
                    print('ERROR:', exc.args[0])
                    
        elif opt == 'del' and rootMode:
            print('List:\n',os.listdir(f_dir))
            sock.send(str(os.listdir(f_dir)).encode())
            os.remove(f_dir +'/'+os.listdir()[sock.recv(max_buffer_size).decode()])
        
        elif opt == 'root':
            if (receive_input(sock) == rootPass):
                rootMode = not rootMode
                sock.send(str(rootMode).encode()) 
            #deepsleep(10000)
            #print('waking up...')
            
        else:
            pass
    #except MemoryError as error:
     #   print('Memory error, closing socket...')
      #  sock.close()
            

def receive_input(sock, max_size = max_buffer_size):
    client_input = sock.recv(max_size)
    client_input_size = len(client_input)

    if client_input_size > max_size:
        print("The input size is greater than expected {}".format(client_input_size))

    result = client_input.decode().rstrip()  # decode and strip end of line

    return result

def checkSpace():
    return os.statvfs('/')[0] * os.statvfs('/')[3]

def createFilePath():
    try:
        os.mkdir(f_dir)
    except OSError as exc:
         print()

#   MAIN
def Main():
    address = {}
    
    connection = ConnectionHandler()
    connection.startAP('ESP32_AP', '12312312')
    _thread.start_new_thread(connection.startWlanClient, ('Pretty Fly for a Wi-Fi', 'abyssus64'))
    
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
    
    try:
        soc.bind(('192.168.4.1', 8888))
    except OSError as exc:
        print("Error: Bind failed! ErrorNo:", exc.args[0])
        sys.exit()

    soc.listen(5)       # queue up to 5 requests
    print("Socket now listening...")

    createFilePath()
    # infinite loop- do not reset for every requests
    while True:
        sock, address = soc.accept()
        ip, port = str(address[0]), str(address[1])
        print("Client [" + ip + ":" + port + "] connected!")
    
        pin_handler.toggleLed()
        try:
            _thread.start_new_thread(clientThread, (sock, ip, port))
        except:
            print("Unable to start the thread!")

if __name__ == '__main__': 
    Main() 
