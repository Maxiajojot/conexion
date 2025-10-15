import socket
import threading
import sys

HOST = "127.0.0.1"  
PORT = 8000

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Crear un socket con el protrocolo TCP
cliente.connect( (HOST, PORT) ) #Coneccion al servidor

try:
    usuario = input("Ingrese tu usuario: ") #Pedis el nombre de usuario por consola
except KeyboardInterrupt: #Por si apretas Ctrl + C
    print("\033[93mSaliendo...\nVuelva pronto\033[0m")
    cliente.close() #Cerrar el socket para liberar recursos
    sys.exit(0) #Terminar el proceso 

if not usuario:
    usuario = "Anonimo"


def recive_mensajes(): #Hilo de receptores, escucha lo que llegue al servidor
    while True:
        try:
            data = cliente.recv(1024) #Espera datos con max(1024)
            if not data: #Si es que llega vacio, cerra la conexion
                print("Servidor cerro la conexion")
                try: cliente.close() 
                except OSError: pass
                break

            mensaje = data.decode('utf-8', errors='replace') #Descodifica bytes a str
            if mensaje == "@usuario": #Protocolo para que cuando envie el mensaje le ponga el username
                try:
                    cliente.send(usuario.encode('utf-8'))
                except OSError: #Si ya estaba cerrodo, ignora el error
                    break
            else:
                print(mensaje)
        except (ConnectionResetError, OSError): #Si el server se cae o hay un error de red
            print("Servidor Cerrado")
            try:
                cliente.close()
            except OSError:
                pass
            break

def enviar_mensajes(): #Funcion principal
    try:
        while True:
            texto = input("") #Espera que ingreses un mensaje
            mensaje = f"{usuario}: {texto}" #Envia el mensaje con el usuario
            cliente.send(mensaje.encode('utf-8')) #Lo manda al server en bytes UTF-8
    except KeyboardInterrupt: #Por si apretas Ctrl + C
        pass
    finally:
        print("Saliendo")
        cliente.close()
        sys.exit(0)

recive_thread = threading.Thread(target=recive_mensajes, daemon=True) #Creo un hilo aparte para escuchar del server, para que el input no se bloquee
#El deamon=true es por si el programa termina, el hilo muere
recive_thread.start() #Arranca el hilo receptor      

enviar_mensajes()