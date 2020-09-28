import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json

run = True
clients_lock = threading.Lock()
connected = 0

clients = {}
clientIds = []

def str_int_addr(address:str):
   splitaddr = address.split(',')

   a1 = splitaddr[0]
   a1 = a1.replace(" ","")
   a1 = a1.replace("(","")
   a1 = a1.replace("'","")

   a2 = splitaddr[1]
   a2 = a2.replace(" ","")
   a2 = a2.replace(")","")
   a2 = int(a2)

   return (a1,a2)

def connectionLoop(sock):
   global run
   global clientIds

   while run:
      data, addr = sock.recvfrom(1024)

      data = str(data)
      if addr in clients:
         if 'heartbeat' in data:
            clients[addr]['lastBeat'] = datetime.now()
      else:
         if 'connect' in data:
            clientIds.append(str(addr))
            clients[addr] = {}
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]['color'] = 0
            
            clientlist = {"list of all current players":clientIds}
            l = json.dumps(clientlist)
            cur = str_int_addr(str(addr))
            sock.sendto(bytes(l,'utf8'),cur)

            message = {"cmd": 0,"player":{"id":str(addr)}}
            m = json.dumps(message)
            for c in clients:
               sock.sendto(bytes(m,'utf8'), (c[0],c[1]))
                           
def cleanClients(sock):
   global run
   while run:
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
            print('Dropped Client: ', c)
            clients_lock.acquire()
            information = {"This client has been dropped":c}
            i = json.dumps(information)
            for cl in clients:
               sock.sendto(bytes(i,'utf8'), (cl[0],cl[1]))
            del clients[c]
            clients_lock.release()           
      time.sleep(1)

def gameLoop(sock):
   global run
   while run:
      GameState = {"cmd": 1, "players": []}
      clients_lock.acquire()
      print (clients)
      for c in clients:
         player = {}
         clients[c]['color'] = {"R": random.random(), "G": random.random(), "B": random.random()}
         player['id'] = str(c)
         player['color'] = clients[c]['color']
         GameState['players'].append(player)
      s=json.dumps(GameState)
      print(s)
      for c in clients:
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      clients_lock.release()
      time.sleep(1)

def main():
   global run
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,(s,))
   while run:
      time.sleep(1)

if __name__ == '__main__':
   main()