Meta Coding Challenge
   submission by Kevin Doyle
-----------------------------

What
-------------------
   There are two files included.
   
   chat_server.py runs a chat server. The server listens for
   clients trying to connect and manages the transmission of
   messages between connected users.
   
   chat_client.py connects to a running chat server. It handles
   sending and receiving messages from the server. 
   

Requirements
-------------------
   This code was developed using Python 2.7 on Windows and uses the 
   following standard libraries:
      argparse
      logging
      Queue
      socket
      sys
      threading
   Please use Python 2.7 to run these files.
   
   
How to use
-------------------
   Begin by starting a chat server. The default settings will have the 
   server listening for connections from all available addresses. To 
   do this, run:
   
      python chat_server.py
      
   To see more options, include: --help
   
   With a chat server running, you can now connect a client. The default
   address clients connect to is localhost:8001. You can connect to a
   specific server address with the following:
   
      python chat_client.py --host XXXX --port ####
      
   Where XXXX is replaced with your server's domain or IP address and 
   #### is replaced with the port your server is listening on. 

   Once your client is connected, you can disconnect by typing the 
   following into chat:
   
      /command exit
   

