# bomberGame

This is a multiplayer game. You can play it with players connected to your local network. 


REQUIREMENTS:

	- Python3( sudo apt-get install python3 )
	- Pip	 ( sudo apt-get install python3-pip )
	- Pygame ( sudo python3 -m pip install pygame )
	- Pyro4  ( sudo python3 -m pip install pyro4 )


STEPS:

    1 - Get your ip address and put it in line 142 of server.py and in line 10 of client.py
    2 - In terminal run: sudo pyro4-ns -n 192.168.0.4 -p 7777 (set your ip)
    3 - Open another terminal, go to folder spaceKingGame and run the server.py file ex: python3 server.py
    4 - Open another terminal in your computer or another local network computer, go to folder spaceKingGame and run the client.py ex: python3 play.py
    5 - Enjoy yourself! 

contacts: 
e-mail: igorduartetkd@gmail.com
