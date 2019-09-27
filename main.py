from tkinter import *
from tkinter import ttk

from client import *


def buildClientFrame(root):

    frame = Frame(root, highlightbackground="green", highlightcolor="green", highlightthickness=1, width=300, height=500)
    frame.pack(side=TOP, fill=BOTH, expand=1)

    label = Label(frame, text="Configuracion del Cliente", bg="green", fg="white")
    #label.grid(row=0, columnspan=2, sticky="nsew")
    label.pack(fill=X)

    labelArchivo = Label(frame, text="Seleccione un archivo:")
    #labelArchivo.grid(row=1, column=0, sticky="W")
    labelArchivo.pack(side=LEFT, fill=X)

    comboArchivo = ttk.Combobox(frame)
    comboArchivo['values'] = ["Archivo PDF", "Video MP4"]
    #comboArchivo.grid(row=2, column=0)
    comboArchivo.pack(side=LEFT, fill=X)

    botonDescargar = Button(frame, text="Descargar", fg="blue", command= lambda:startSingleConnection(comboArchivo))
    #botonDescargar.grid(row=2, column=1)
    botonDescargar.pack(side=LEFT,fill=X)


def buildServerFrame(root):
    frame = Frame(root, highlightbackground="green", highlightcolor="green", highlightthickness=1, width=300, height=500)
    frame.pack(fill=X,  expand=1)

    label = Label(frame, text="Configuracion del Servidor", bg="blue", fg="white")
    label.grid(row=0, columnspan=2, sticky="nsew")

    labelPrueba = Label(frame, text="Configuracion de la prueba:")
    labelPrueba.grid(row=1, column=0)

    labelNumConexiones = Label(frame, text="Numero de conexiones:")
    labelNumConexiones.grid(row=2, column=0, sticky="E")

    comboNumConexiones = ttk.Combobox(frame)
    comboNumConexiones['values'] = [i for i in range(1, 26)]
    comboNumConexiones.grid(row=2, column=1)

    labelArchivoServidor = Label(frame, text="Seleccione un archivo:")
    labelArchivoServidor.grid(row=3, column=0, sticky="E")

    comboArchivoServidor = ttk.Combobox(frame)
    comboArchivoServidor['values'] = ["Archivo PDF", "Video MP4"]
    comboArchivoServidor.grid(row=3, column=1)

    botonRealizarPrueba = Button(frame, text="Realizar prueba", fg="blue", bg="gray", command= lambda: doTestEvent(comboNumConexiones, comboArchivoServidor))
    botonRealizarPrueba.grid(row=4, columnspan=2)


def buildTestConnectionFrame(root):
    frame = Frame(root)
    frame.pack(side=BOTTOM, fill=BOTH)

    labelTestConnection = Label(frame, text="Test Connection", bg="purple", fg="white")
    labelTestConnection.pack(fill=X)

    botonTestConnection = Button(frame, text="Test Connection", fg="red", command=testConnection)
    #botonTestConnection.grid(columnspan=3)
    botonTestConnection.pack()


def center_window(w=300, h=200):
    # get screen width and height
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    # calculate position x, y
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
#startConnection(0)

root = Tk()
root.title("Aplicacion protocolo TCP")
#center_window(500, 300)
buildClientFrame(root)
buildServerFrame(root)
buildTestConnectionFrame(root)

root.mainloop()
