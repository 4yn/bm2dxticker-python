from ctypes import *
from ctypes.wintypes import *
import json
import socket
import win32gui,win32process
from websocket_server import WebsocketServer

print "\n----------------IIDX TICKER----------------\n"
print "made by Jimboker http://github.com/4yn/"
print "viewer available at http://4yn.github.io/4yn/pyticker-client/viewer.html"
print "original idea and memory address data by smpn2\n\n"

# alias to functions
OpenProcess = windll.kernel32.OpenProcess
ReadProcessMemory = windll.kernel32.ReadProcessMemory
CloseHandle = windll.kernel32.CloseHandle
GetWindowPid = win32process.GetWindowThreadProcessId
EnumProcessModules = win32process.EnumProcessModules
GetModuleName = win32process.GetModuleFileNameEx

# variables
client_num = 0
memory_address = 0
phandle = 0
ticker = c_char_p("*********")
ticker_s = len(ticker.value)
bytesRead = c_ulong(0)
game = 0

# handle game data
config = json.load(open('config.txt'))
for g in config["gameList"]:
	if type(config["currentGame"])==int:
		if config["currentGame"] == g["gameIndex"]:
			game = g
	else:
		if config["currentGame"] == g["gameKey"]:
			game = g

if(game==0):
	print "\nPlease specify correct game in config.txt\ne.g.\n\n\t\"currentGame\": 22 ,\n\nfor PENDUAL \n\n" 
else:
	print "Running ticker for " + game["gameTitle"]

# create handle, define address
def initTicker():
	global phandle, memory_address
	CloseHandle(phandle)
	hwnd  = win32gui.FindWindow(None, game["windowTitle"])
	threadid,pid = GetWindowPid(hwnd)
	phandle = OpenProcess(0x1F0FFF,False,pid)
	modlist = EnumProcessModules(phandle)
	for mod in modlist:
		mname = GetModuleName(phandle,mod)
		if mname.endswith(game["moduleName"]):
			memory_address = mod + game["memoryOffset"]

# read address
def readTicker():
	ReadProcessMemory(phandle, memory_address, ticker, ticker_s, byref(bytesRead))

def clientJoin(client,server):
	global client_num
	client_num += 1
	if(client_num==1):
		initTicker()

def clientLeave(client,server):
	global client_num
	client_num -= 1
	if(client_num==0):
		CloseHandle(phandle)

def clientMsg(client,server,message):
	readTicker()
	server.send_message(client,ticker.value.replace('m','.'))

print "Starting server on " + str(socket.gethostbyname(socket.gethostname()))
server = WebsocketServer(config["serverPort"],"0.0.0.0")
server.set_fn_new_client(clientJoin)
server.set_fn_client_left(clientLeave)
server.set_fn_message_received(clientMsg)
server.run_forever()