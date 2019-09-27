import socket
import sys
import errno
import pickle
import hashlib
import time
import datetime
import threading
import concurrent.futures
from tkinter import *
import tkinter.messagebox
import random

HEADERSIZE = 10

IP = "127.0.0.1"
PORT = 1236

FILE_1 = "./files/archivo_recibido.pdf"
FILE_NAME_1 = "./files/archivo_recibido"
FILE_NAME_2 = "./files/video_recibido"
LOG_FILE = "./logs/log_file_"
FILE_DICT = {
    "1" : "informe.pdf",
    "2" : "video-4.mp4"
}

def createMessage(message):
    #Chequear el atributo message size, puede que este incorrecto
    msg = {"messageSize": len(message.encode("utf-8")),
     "message": message.upper()}
    msg = pickle.dumps(msg)
    # Anadir header de 10 bytes
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


def receiveFile(clientSocket, id, fileId, logFileName):
    try:
        #Manejo de log:
        #logFileName = LOG_FILE + str(id) + ".txt"
        logFile = open(logFileName, 'a')

        print("Receiving file from server...")
        #Inicio de recepcion del archivo
        messageHeader = clientSocket.recv(HEADERSIZE)
        messageLength = int(messageHeader.decode("utf-8").strip())
        print("File size:", messageLength)

        if fileId == "1":
            fileName = FILE_NAME_1 + f"-{id}.pdf"

        elif fileId == "2":
            fileName = FILE_NAME_2 + f"-{id}.mp4"

        file = open(fileName, 'wb')
        data = b""
        bytesLeft = messageLength
        #Se empieza a tomar el tiempo de transferencia:
        startTime = time.perf_counter()
        while bytesLeft > 0:
            # print(f"{bytesLeft} Bytes left")
            # data = data + clientSocket.recv(1024)
            file.write(clientSocket.recv(1024))
            bytesLeft = bytesLeft - 1024
        finishTime = time.perf_counter()
        logFile.write(f"Tiempo de transferencia: {finishTime - startTime} segundo(s)\n")
        # data = clientSocket.recv(messageLength)
        # print("data: ", data)

        file.close()
        print("File received.")
        # Si las lineas de arriba no lanzan ninguna excepción, la transferencia del archivo fue exitosa:
        logFile.write("Estado de transferencia: Exitosa\n")
        logFile.close()
        # tkinter.messagebox.showinfo("Estado de solicitud", "El archivo fue recibido exitosamente")
        return fileName
    except Exception as e:
        logFile.write("Estado de transferencia: Error recibiendo archivo.\n")
        logFile.close()
        print('General error', str(e))




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


def compareDigest(digest, fileName):
    print("Iniciando compararacion del digest:")
    file = open(fileName, 'rb')
    fileContent = file.read()
    h = hashlib.sha256()
    h.update(fileContent)
    digestToCompare = h.digest()
    if digestToCompare == digest:
        return True #Retorna verdadero si son iguales
    else:
        return False


def testConnection():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP, PORT))

        message = createMessage("TEST")
        s.sendall(message)

        message = receiveMessage(s)
        if message['message'] == "OK":
            tkinter.messagebox.showinfo("Estado del test", "Test exitoso! Se pudo establecer una conexión con el servidor.")
        else:
            tkinter.messagebox.showerror("Estado del test", "Error conectandose con el servidor.")

    except Exception as e:
        tkinter.messagebox.showerror("Estado del test", "Error conectandose con el servidor.")
        print('General error', str(e))


def doTestEvent(comboBoxNumConexiones, comboBoxArchivo):
    print("Num con:", comboBoxNumConexiones.get())
    print("Archivo:", comboBoxArchivo.get())
    testId = random.randint(1, 100)
    if comboBoxNumConexiones.get() is not "" and comboBoxArchivo.get() is not "":
        if comboBoxArchivo.get() == "Archivo PDF":
            fileId = "1"
        elif comboBoxArchivo.get() == "Video MP4":
            fileId = "2"

        startMultipleConnections(int(comboBoxNumConexiones.get()), fileId, testId)
    else:
        tkinter.messagebox.showerror("Error", "Se deben llenar todos los campos.")


def startSingleConnection(comboBoxArchivo):
    print("Archivo:", comboBoxArchivo.get())
    if comboBoxArchivo.get() is not "":
        fileId = ""
        if comboBoxArchivo.get() == "Archivo PDF":
            fileId = "1"
        elif comboBoxArchivo.get() == "Video MP4":
            fileId = "2"

        start = time.perf_counter()
        startConnection(fileId, "")
        finish = time.perf_counter()
        tkinter.messagebox.showinfo("Resultados del test", f"Terminado en {round(finish - start, 2)} segundo(s)")

    else:
        tkinter.messagebox.showerror("Error", "Se deben llenar todos los campos.")


def startMultipleConnections(numConnections, fileId, testId):
    start = time.perf_counter()
    threads = []

    try:
        for i in range(numConnections):
            t = threading.Thread(target=startConnection(fileId, testId))
            t.start()
            threads.append(t)

        for thread in threads:
            thread.join()

        finish = time.perf_counter()

        print(f"Terminado en {round(finish - start, 2)} second(s)")
        tkinter.messagebox.showinfo("Resultados del test", f"Terminado en {round(finish - start, 2)} segundo(s)")
    except Exception as e:
        tkinter.messagebox.showerror("Estado de la solicitud", "Error conectandose con el servidor.")
        print('General error', str(e))




def startConnection(fileId, testId):
    id = random.randint(1, 1000000)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP, PORT))
    except Exception as e:
        tkinter.messagebox.showinfo("Error conectandose al servidor",
                                 "El servidor no se encuentra en funcionamiento. Por favor intentar de nuevo mas tarde.")
        print('General error', str(e))
    #s.setblocking(False)
    #Enviar el primer mensaje
    #msg = input("Digite un mensaje: ")
    message = createMessage("HELLO")
    s.sendall(message)
    while True:
        message = receiveMessage(s)
        try:
            if message["message"] == "HELLO BACK":
                # El usuario debe digitar 'PREPARED'
                print("C:", message["message"])
                #msg = input("Digite su mensaje:") # Digitar PREPARED
                message = createMessage("PREPARED")
                s.sendall(message)
            # Si el servidor nos lista los archivos
            elif "ARCHIVOS" in message["message"]:
                print("C:", message["message"])
                #msg = input("Escoga un archivo:") # Digitar el numero del archivo
                message = createMessage(fileId)
                s.sendall(message)
                # Empezar a recibir archivo
                #file = receiveFile(s)

                #Generar log
                if testId is "":
                    logFileName = LOG_FILE + str(id) + ".txt"
                else:
                    logFileName = LOG_FILE + str(testId) + "_" + str(id) + ".txt"

                logFile = open(logFileName, 'w')
                logFile.write(f"LOG FILE\n\n")
                logFile.write(f"ID: {str(id)}\n")
                logFile.write(f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                logFile.write(f"Nombre del archivo: {FILE_DICT[fileId]}\n")
                logFile.write(f"ID Cliente: {id}\n")
                if testId is not "":
                    logFile.write(f"ID Prueba: {testId}\n")
                else:
                    logFile.write(f"ID Prueba: N/A\n")
                logFile.close()

                fileName = receiveFile(s, id, fileId, logFileName) #Retorna el nombre del archivo guardado

                # Luego de recibir el archivo se pide el digest:
                #msg = input("Digite su mensaje:")  # Digitar DIGEST
                message = createMessage(f"DIGEST{fileId}") # Está implicito en el mensaje DIGEST que el archivo fue recibido
                s.sendall(message)

                #Recibir digest
                digest = receiveDigest(s)
                #Se compara el digest recibido por el calculado
                res = compareDigest(digest, fileName)
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



#numConnections = input("digite el numero de conexiones simultaneas que quiere realizar al servidor:")
'''
start = time.perf_counter()
threads = []
for i in range(25):
    t = threading.Thread(target=startConnection(i))
    t.start()
    threads.append(t)

for thread in threads:
    thread.join()

finish = time.perf_counter()

print(f"Terminado en {round(finish-start, 2)} second(s)")
'''









'''
start = time.perf_counter()
startConnection(1)
startConnection(2)
startConnection(3)
startConnection(4)
startConnection(5)
startConnection(6)
startConnection(7)
startConnection(8)
startConnection(9)
startConnection(10)
startConnection(11)
startConnection(12)
startConnection(13)
startConnection(14)
startConnection(15)

finish = time.perf_counter()

print(f"Terminado en {round(finish-start, 2)} second(s)")
'''

'''

timeStart = time.time()




with concurrent.futures.ThreadPoolExecutor() as executor:
    results = [executor.submit(startConnection, i) for i in range(15)]
    #for f in concurrent.futures.as_completed(results):
timePassed = time.time() - timeStart
print("Segundos transcurridos:", timePassed)
'''



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