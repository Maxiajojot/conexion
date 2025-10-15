import socket
import threading

HOST = "127.0.0.1"  
PORT = 8000

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Generar el socket con valores por defaut
servidor.bind((HOST,PORT)) #Establecer las conexciones con una tupla de dos valores, el host y el puerto en el que escucha
servidor.listen(5) #Cantidad de peticiones que puede manejar en cola el socket

print(f"Servidor escuchando en {HOST}:{PORT}")

clientes = [] #Almacena las conexiones de los clientes
usuarios = [] #Almacena los username de cada cliente

def broadcast(mensaje, cliente_mensajero): #Funcion que hace que le envie el mensaje a todos los clientes
    for cliente in clientes:
        if cliente != cliente_mensajero: #Enviar a todos menos al que envio el mensaje
            for _ in range(2):  # reintentar 2 veces
                try:
                    cliente.send(mensaje)
                    break  # si lo logro enviar, salimos del bucle
                except BlockingIOError:
                    #Si la red esta temporalmente ocupada, reintenta enviar
                    continue
                except (BrokenPipeError, ConnectionResetError, OSError):
                    # Si el cliente esta muerto o se desconecto
                    if cliente in clientes: #Si hay un error, elimina al cliente y su usuario de las listas.
                        idx = clientes.index(cliente)
                        usuario = usuarios[idx]
                        print(f"Error al enviar mensaje a {usuario}, se eliminará del chat.")
                        clientes.pop(idx)
                        usuarios.pop(idx)
                    try:
                        cliente.close() #Cerrar el socket para liberar recursos
                    except OSError:
                        pass
                    break  # Cierra el socket y rompe el bucle para pasar al siguiente cliente.


def manejar_mensajes(cliente):
    while True:
        try:
            mensaje = cliente.recv(1024)
            if not mensaje: #Si el mensaje esta vacio, el cliente cerro la conexcion
                if cliente in clientes:
                    idx = clientes.index(cliente) #Me dice en que posicion esta de la lista
                    usuario = usuarios[idx]
                    broadcast(f"Chatbot: {usuario} desconectado".encode('utf-8'), cliente)
                    clientes.pop(idx)
                    usuarios.pop(idx)
                try:
                    cliente.close()
                except OSError:
                    pass
                break
            broadcast(mensaje,cliente) #Si es que no estaba vacio, lo manda al broadcast
        except (ConnectionResetError, OSError):
            if cliente in clientes: #Elimina el usuario desconectado y le avisa a los demas
                idx = clientes.index(cliente)
                usuario = usuarios[idx]
                broadcast(f"Chatbot: {usuario} desconectado".encode('utf-8'), cliente)
                print(f"{usuario} se desconectó del servidor.")  
                clientes.pop(idx)
                usuarios.pop(idx)
            try:
                cliente.close()
            except OSError:
                pass
            break


def recive_conexcion(): #Espera a que llegue una conexión
    while True:
        cliente, direccion = servidor.accept() #Devuelve dos cosas cliente y direccion tupla(ip y port)
        try:
            cliente.send("@usuario".encode('utf-8')) #Sirve para pedirle el username al cliente
            dato = cliente.recv(1024)
            usuario = dato.decode('utf-8', errors='replace').strip() 
            
        except (ConnectionResetError, OSError) as e:
            print(f"Error de handshake con {direccion}: {e}")
            try:
                cliente.close()
            except OSError:
                pass
            continue

        clientes.append(cliente)
        usuarios.append(usuario)

        print(f"{usuario} se conecto al {str(direccion)}")

        mensaje = f"Chatbot: {usuario} se unio al chat!".encode('utf-8')
        broadcast(mensaje, cliente)
        try:
            cliente.send("Conectado al Servidor".encode('utf-8'))
        except OSError:
            pass
        
        thread = threading.Thread(target=manejar_mensajes, args=(cliente,)) 
        thread.start()

recive_conexcion()



