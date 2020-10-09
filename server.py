import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json

clients_lock = threading.Lock()
connected = 0

clients = {}
clientList = []
droppedClients = []

def connectionLoop(sock):
   global clientList
   while True:
      data, addr = sock.recvfrom(1024)
      data = str(data)
      if addr in clients:
         if 'heartbeat' in data:
            clients[addr]['lastBeat'] = datetime.now()
      else:
         if 'connect' in data:
            clients[addr] = {}
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]['color'] = 0
            clientList.append(str(addr))
            msg = {"cmd": 0," new player has arrived":{'id':str(addr)}}
            fullMsg = {"cmd": 0,"list of current players:":clientList}
            for c in clients:
               if c == addr:
                  m = json.dumps(fullMsg)
               else:
                  m = json.dumps(msg)
               sock.sendto(bytes(m,'utf8'), (c[0],c[1]))

def cleanClients(sock):
   global droppedClients
   while True:
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
            print('Dropped Client: ', c)
            clients_lock.acquire()
            del clients[c]
            clients_lock.release()
            droppedClients.append(str(c))
      message = {"cmd": 2, "Players have just disconnected": droppedClients}
      m = json.dumps(message)
      if len(droppedClients) > 0:
         for c in clients:
            sock.sendto(bytes(m, 'utf8'), (c[0], c[1]))
      time.sleep(1)

def gameLoop(sock):
   while True:
      GameState = {"cmd": 1, "players": []}
      clients_lock.acquire()
      print(clients)
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
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   start_new_thread(gameLoop, (s, ))
   start_new_thread(connectionLoop, (s, ))
   start_new_thread(cleanClients,(s, ))
   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()