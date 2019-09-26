import socket
import sys
import errno
import pickle
import hashlib
import concurrent.futures

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


def receiveFile(clientSocket):
    print("Receiving file from server...")
    messageHeader = clientSocket.recv(HEADERSIZE)
    messageLength = int(messageHeader.decode("utf-8").strip())
    print("File size:", messageLength)

    file = open(FILE_1, 'wb')

    data = b""
    bytesLeft = messageLength
    while bytesLeft > 0:
        print(f"{bytesLeft} Bytes left")
        #data = data + clientSocket.recv(1024)
        file.write(clientSocket.recv(1024))
        bytesLeft = bytesLeft - 1024

    #data = clientSocket.recv(messageLength)
    #print("data: ", data)

    file.close()
    print("File received.")
    return file


def receiveDigest(s):
    print("Receiving digest from server...")
    try:
        # Desarmar header para saber el tamaño en bytes del mensaje
        messageHeader = s.recv(HEADERSIZE)
        # Atrapo el tamaño en bytes del mensaje que se va a recibir
        messageLength = int(messageHeader.decode("utf-8").strip())
        # Se recibe el mensaje del socket que contiene el digest del archivo
        digest = s.recv(messageLength)

        print(f"Digest received from server: {digest}")
        return digest
    except Exception as e:
        print('General error', str(e))


def compareDigest(digest):
    print("Iniciando compararacion del digest:")
    file = open(FILE_1, 'rb')
    fileContent = file.read()
    h = hashlib.sha256()
    h.update(fileContent)
    digestToCompare = h.digest()
    if digestToCompare == digest:
        return True #Retorna verdadero si son iguales
    else:
        return False

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
            msg = input("Digite su mensaje:") # Digitar PREPARED
            message = createMessage(msg)
            s.sendall(message)
        # Si el servidor nos lista los archivos
        elif "ARCHIVOS" in message["message"]:
            print("C:", message["message"])
            msg = input("Escoga un archivo:") # Digitar el numero del archivo
            message = createMessage(msg)
            s.sendall(message)
            # Empezar a recibir archivo
            #file = receiveFile(s)

            file = receiveFile(s)

            # Luego de recibir el archivo se pide el digest:
            msg = input("Digite su mensaje:")  # Digitar DIGEST
            message = createMessage(msg)
            s.sendall(message)

            #Recibir digest
            digest = receiveDigest(s)
            #Se compara el digest recibido por el calculado
            res = compareDigest(digest)
            if res:
                print("El archivo no fue alterado.")
            else:
                print("El archivo FUE alterado.")


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


#with concurrent.futures.ThreadPoolExecutor() as executor:
    


'''
def receiveFileVersion2(clientSocket):
    print("Empezando a recibir archivo...")
    arch = open(FILE_1, 'wb')  # Cambiar el nombre del archivo para que sea único y no haya interferencia en el directorio
    # Desarmar header para saber el tamaño en bytes del mensaje
    messageHeader = clientSocket.recv(HEADERSIZE)
    print("Message header:", messageHeader)
    # Atrapo el tamaño en bytes del mensaje que se va a recibir
    messageLength = int(messageHeader.decode("utf-8").strip())
    # Se recibe el mensaje del socket
    data = b""
    i=0
    while True:
        print(f"recibiendo...{i}")
        packet = clientSocket.recv(4096)
        if not packet: break
        data += packet
        i=i+1
    #message = clientSocket.recv(messageLength)
    message = pickle.loads(data)
    data = message["file"]

    #Con el fileSize puedo saber cuantos bytes ocupa exactamente el archivo

    #Escribimos en el archivo
    arch.write(data)
    arch.close()
    print("Archivo recibido.")
    return arch
'''


'''
def receiveFile(s):
    arch = open(FILE_1, 'wb')  #Cambiar el nombre del archivo para que sea único y no haya interferencia en el directorio
    # Vamos a tener que crear una variable compartida para los IDs
    print("Empezando a recibir archivo...")
    f = s.recv(1024)
    i=0
    while f:
        print(f"Recibiendo archivo parte {i}...")
        arch.write(f)
        f = s.recv(1024)
        i=i+1
    print("Cerrando archivo de escritura")
    arch.close()
    print("Archivo recibido.")
    return arch
'''