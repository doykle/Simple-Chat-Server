#  
#  chat_client.py
#
#  This file connects to a very simple chat server.
#  Connect to a local server using defaults by running:
#     python chat_server.py
#
#  To see configuration options, type 
#     python chat_server.py --help
#  into your command line.
#
#  To-do improvements and known issues: 
#        - Handling messages dynamically instead of using 
#          a static buffer
#
#        - The 'lost connection' handling is not based on 
#          satisfactory testing
#
#        - Error handling
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
import socket
import sys
import threading

class ClientFeeder(threading.Thread):
   """
   Accepts incoming messages from the server and 
   prints the messages to stdout.
   
   Design inspiration from http://pymotw.com/2/threading/
   """
   def __init__(self, client_socket):
      threading.Thread.__init__(self)
      self.name = "ClientFeeder@{0}".format(client_socket.getsockname())
      self.sock = client_socket
      
   def run(self):
      logging.info("begin: run()")
      self.receive_message()

   def receive_message(self):
      """Receives messages and prints them to stdout"""
      logging.info("begin: receive_message()")
      
      while True:
         message = ''
         data = self.sock.recv(1024)
         
         if len(data) > 0:
            logging.debug("send_message-- data = {0}".format(data))
            message += data
            print message
         
         elif data == '':
            logging.info("send_message-- data = {0}! Connection lost!".format(data))
            break
            
         else:
            logging.debug("send_message-- data = {0}, no data collected".format(data))
      
      
def execute_command(sock, command_line):
   """Parses and executes commands"""
   logging.info("begin: execute_command({0})".format(command_line))
   command_line = command_line.split(' ')

   if len(command_line) == 2:
      command = command_line[1].strip()
      logging.debug("execute_command-- command = {0}".format(command))
   
      if command == 'exit':
         # Collect other threads before closing socket
         for fiber in threading.enumerate():
            if fiber.name.startswith("Main"):
               continue
            fiber.join(1)
         sys.exit(1)
         
      
def send_message(sock, prompt = ''):
   """Waits for input and sends message"""
   logging.info("begin: send_message()")
   
   while True:
      message = raw_input(prompt)
      sock.sendall(message)
      
      if message.startswith('/command'):
         execute_command(sock, message)


if __name__ == '__main__':

   # Handles command line arguments
   parser = argparse.ArgumentParser()
   parser.add_argument("--port", help="port for the server address",
                       type=int, default='8001')
   parser.add_argument("--host", help="host for the server address",
                       type=str, default='localhost')
   parser.add_argument("--debug", help="type ON for debug logging output",
                       type=str, default='OFF')
   args = parser.parse_args()
   server_host = args.host
   server_port = args.port
   server_address = (server_host, server_port)

   if args.debug == "ON":
      logging_level = logging.DEBUG
   else:
      logging_level = logging.ERROR
   logging.basicConfig(level=logging_level, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)
   logging.debug("server_address: {0}".format(server_address))
   
   try:
      # Create socket to server
      client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      client_socket.connect(server_address)
      logging.info("Now connected at {0}".format(client_socket.getsockname()))
      
      # New thread actively updates the chat space with new messages
      receiver = ClientFeeder(client_socket)
      receiver.daemon = True
      receiver.start()
      
      # MainThread is used to compose and send messages
      if threading.active_count() > 1:
         send_message(client_socket)
      
   finally:
      logging.info("Closing socket {0}".format(client_socket.getsockname()))
      client_socket.close()