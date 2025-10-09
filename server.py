import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 1234))
s.listen(5)

while True:
    clientsocket , address = s.accept()
    print(f"Coneccion de {address} se ha establecido!")
    clientsocket.send(bytes("Bienvenido al servidor!","utf-8")) #Son un tipo de bytes utf-8
