#  
#  chat_server.py
#
#  This file sets up a very simple chat server.
#  Start the server using defaults by running:
#     python chat_server.py
#
#  To see configuration options, type 
#     python chat_server.py --help
#  into your command line.
#
#  To-do improvements and known issues: 
#        - Add settimeout() to client sockets, allowing for
#          the detection and removal of unresponsive clients.
#
#        - Handling messages dynamically instead of using 
#          a static buffer
#
#        - Storing {username : socket} correlations 
#
#        - The server can't stop, won't stop.
#
#        - Exclude sender from the receivers list.
#
#        - Error handling
#
#        - Enforce unique usernames
#
#        - Send/Receive confirmation of message receipt
#          and transmission
#
#  Written by Kevin Doyle for Meta - Unified Search, 2015
#  Developed and tested using Python 2.7
#
#  Resources reviewed in addition to python module documentation:
#     http://pymotw.com/2/socket/
#     https://docs.python.org/2/howto/sockets.html
#     http://pymotw.com/2/threading/
#    

import argparse
import logging
import Queue
import socket
import sys
import threading

class ClientListener(threading.Thread):
   """Handles incoming messages from clients"""
   
   def __init__(self, sock, address, message_queue, clients):
      threading.Thread.__init__(self)
      self.sock = sock
      self.addr = address
      self.msg_queue = message_queue
      self.client_sockets = clients
      
   def run(self):
      self.username = self.register_user()
      self.user_session()

   def execute_command(self, command_line):
      """Parses and executes commands"""
      command_line = command_line.split(' ')
      
      if len(command_line) == 2:
         command = command_line[1].strip()
      
         if command == 'exit':
            self.queue_message(">> SERVER: Goodbye {0}!".format(self.username))
            # Remove socket from list before closing to avoid errors
            self.client_sockets.remove(self.sock)
            self.sock.close()
            exit()
      
   def user_session(self):
      """User messages and commands are handled here."""
      logging.info("Entered user session")
      self.queue_message(">> Welcome, {0}!".format(self.username))
      
      while True:
         user_input = self.receive_message()
         if user_input.startswith('/command'):
            self.execute_command(user_input)
         else:
            message = ">> {0}: {1}".format(self.username, user_input)
            self.queue_message(message)
         
   def queue_message(self, message):
      """Adds a message to the queue"""
      logging.info("Queueing message: {0}".format(message))
      logging.debug("Message queue size before: {0}".format(self.msg_queue.qsize()))
      # Note: 'put' will block for 3 seconds, then message is lost. Needs better handling.
      self.msg_queue.put(message, True, 3)
      logging.debug("Message queue size after: {0}".format(self.msg_queue.qsize()))

   def receive_message(self):
      """
      Receives data sent from the client. 
      Note: returning '' is handled as an indication of connection error
      """
      logging.info("begin: receive_message")
      message = ''

      data = self.sock.recv(1024)
      logging.debug("get_message-- data = {0}".format(data))

      if len(data) > 0:
         message += data
      else:
         pass
         
      logging.info("end: get_message")
      return message

   def register_user(self):
      """Prompts a new connection for an alias"""
      welcome = ">> SERVER: Hello! Please type a name for yourself."
      self.sock.sendall(welcome)
      username = self.receive_message()
      return username

   
def distributer(socket_list, message_queue):
   """
   Takes messages from the front of the queue and sends them
   to every connected client. Note that socket list and 
   message_queue are both modified from other threads. 
   """
   logging.info("begin: distributor()")
   
   while True:
      # .get(True)- 'True' blocks while the queue is empty to save CPU time
      message = message_queue.get(True)
      for user in socket_list:
         user.sendall(message)
   
   
if __name__ == '__main__':

   # Handles command line arguments
   parser = argparse.ArgumentParser()
   parser.add_argument("--port", help="port for the server address",
                       type=int, default='8001')
   parser.add_argument("--host", help="host for the server address",
                       type=str, default='')
   parser.add_argument("--debug", help="type ON for debug logging output",
                       type=str, default='OFF')
   args = parser.parse_args()
   server_host = args.host
   server_port = args.port
   server_address = (server_host, server_port)

   if args.debug == "ON":
      logging_level = logging.DEBUG
   else:
      logging_level = logging.INFO
   logging.basicConfig(level=logging_level, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

   try:
      # Sets up the server
      serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      logging.info("Server socket will be listening on {0}".format(server_address))
      serv_socket.bind(server_address)
      serv_socket.listen(1)
      logging.info("Now listening")
      
      client_sockets = [] # Collection object for client connections
      message_queue = Queue.Queue()
      
      # Continuously sends queued messages to all the connected sockets
      message_distribution = threading.Thread(target=distributer, args=(client_sockets, message_queue))
      message_distribution.daemon = True
      message_distribution.start()
      
      # Accepts clients and gives each a thread to handle incoming messages.
      while True:
         client_socket, client_address = serv_socket.accept()
         logging.info("New connection from {0}".format(client_socket.getsockname()))
         client_sockets.append(client_socket)
         new_client = ClientListener(client_socket, client_address, message_queue, client_sockets) 
         new_client.daemon = True
         new_client.start()

   finally:
      # Collect running threads
      for fiber in threading.enumerate():
         if fiber.name.startswith("Main"):
            continue
         fiber.join(1)
      
      # Close all sockets
      for user in client_sockets:
         user.close()
      
      logging.info("Closing socket listening at {0}".format(serv_socket.getsockname()))
      serv_socket.close()