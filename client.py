import socket
import sys
import errno
import pickle

HEADERSIZE = 10

IP = "127.0.0.1"
PORT = 1236

FILE_1 = "./files/archivo_recibido.pdf"

def createMessage(message):
    #Chequear el atributo message size, puede que esté incorrecto
    msg = {"messageSize": len(message.encode("utf-8")),
     "message": message.upper()}
    msg = pickle.dumps(msg)
    # Añadir header de 10 bytes
    messageHeader = f"{len(msg):<{HEADERSIZE}}".encode("utf-8")

    print(f"Message header: {messageHeader}")
    print(f"Message payload: {msg}")

    # Retornamos el header con el mensaje convertido en bytes
    print(f"Sending message '{messageHeader + msg}'")
    return messageHeader + msg

def receiveMessage(clientSocket):
    print("Receiving message from server...")
    try:
        # Desarmar header para saber el tamaño en bytes del mensaje
        messageHeader = clientSocket.recv(HEADERSIZE)
        # Atrapo el tamaño en bytes del mensaje que se va a recibir
        messageLength = int(messageHeader.decode("utf-8").strip())
        # Se recibe el mensaje del socket
        message = clientSocket.recv(messageLength)
        message = pickle.loads(message)
        print(f"Message received from server: {message}")
        print(message)
        return message
    except Exception as e:
        print('General error', str(e))

def receiveFile(s):
    arch = open(FILE_1, 'wb')
    print("Empezando a recibir archivo...")
    f = s.recv(1024)
    while f:
        arch.write(f)
        f = s.recv(1024)
    arch.close()
    print("Archivo recibido.")
    return arch


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))
#s.setblocking(False)

#Enviar el primer mensaje
msg = input("Digite un mensaje: ")
message = createMessage(msg)
s.sendall(message)

while True:
    message = receiveMessage(s)
    try:
        if message["message"] == "HELLO BACK":
            # El usuario debe digitar 'PREPARED'
            print("C:", message["message"])
            msg = input("Digite su mensaje:")
            message = createMessage(msg)
            s.sendall(message)
        # Si el servidor nos lista los archivos
        elif "ARCHIVOS" in message["message"]:
            print("C:", message["message"])
            msg = input("Escoga un archivo:")
            message = createMessage(msg)
            s.sendall(message)
            # Empezar a recibir archivo
            file = receiveFile(s)
            #Cierro la conexión con el servidor
            s.close()
            break
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error', str(e))
            sys.exit()
        continue
    except Exception as e:
        print('General error', str(e))
        sys.exit()

