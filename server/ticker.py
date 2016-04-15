from ctypes import *
from ctypes.wintypes import *
import win32gui,win32process
import socket
import time
import os.path
from websocket_server import WebsocketServer

OpenProcess = windll.kernel32.OpenProcess
ReadProcessMemory = windll.kernel32.ReadProcessMemory
CloseHandle = windll.kernel32.CloseHandle

PROCESS_ALL_ACCESS = 0x1F0FFF

memory_address = 0x1143AE30
# memory_address = 0x0384AE30

ticker = c_char_p("*********")
ticker_s = len(ticker.value)
bytesRead = c_ulong(0)

num_clients = 0

phandle = 0

server_port=9001

server_port = int(raw_input())
memory_address = int(raw_input()[2:],16)

print "Targeting address: 0x" + hex(memory_address)

def get_window_pid(title):
    hwnd = win32gui.FindWindow(None, title)
    threadid,p_id = win32process.GetWindowThreadProcessId(hwnd)
    return p_id

def setup_process():
	global phandle
	pid = get_window_pid("beatmania IIDX 22 PENDUAL")
	phandle = OpenProcess(PROCESS_ALL_ACCESS,False,pid)

def read_process():
	ReadProcessMemory(phandle, memory_address, ticker, ticker_s, byref(bytesRead))

def close_process():
	CloseHandle(phandle)

def new_client(client, server):
	global num_clients 
	num_clients += 1
	if(num_clients==1):
		setup_process()
	server.send_message_to_all("CONNECT ")

def client_left(client, server):
	global num_clients
	num_clients -= 1
	if(num_clients==0):
		close_process()

def message_received(client, server, message):
	read_process()
	server.send_message_to_all(ticker.value.replace('m','.'))

print "Starting server on " + str(socket.gethostbyname(socket.gethostname()))

server = WebsocketServer(server_port,"0.0.0.0")
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()