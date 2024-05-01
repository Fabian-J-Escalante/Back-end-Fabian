import tkinter as tk
from tkinter import filedialog
from collections import Counter
import heapq

class NodoHuffman:
    def __init__(self, caracter, frecuencia):
        self.caracter = caracter
        self.frecuencia = frecuencia
        self.izquierda = None
        self.derecha = None

    def __lt__(self, otro):
        return self.frecuencia < otro.frecuencia

def construir_arbol_huffman(frecuencias):
    cola_prioridad = [NodoHuffman(caracter, frecuencia) for caracter, frecuencia in frecuencias.items()]
    heapq.heapify(cola_prioridad)
    while len(cola_prioridad) > 1:
        izquierda = heapq.heappop(cola_prioridad)
        derecha = heapq.heappop(cola_prioridad)
        nodo_padre = NodoHuffman(None, izquierda.frecuencia + derecha.frecuencia)
        nodo_padre.izquierda = izquierda
        nodo_padre.derecha = derecha
        heapq.heappush(cola_prioridad, nodo_padre)
    return cola_prioridad[0]

def generar_tabla_codigos(raiz, codigo_actual='', tabla_codigos={}):
    if raiz is not None:
        if raiz.caracter is not None:
            tabla_codigos[raiz.caracter] = codigo_actual
        generar_tabla_codigos(raiz.izquierda, codigo_actual + '0', tabla_codigos)
        generar_tabla_codigos(raiz.derecha, codigo_actual + '1', tabla_codigos)
    return tabla_codigos

def comprimir_archivo(input_file, output_file, tabla_codigos):
    with open(input_file, 'r') as file:
        contenido = file.read()

    bits = ''
    for caracter in contenido:
        bits += tabla_codigos[caracter]

    padding = 8 - len(bits) % 8
    bits += padding * '0'

    bytes_comprimidos = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        bytes_comprimidos.append(int(byte, 2))

    with open(output_file, 'wb') as file:
        file.write(bytes_comprimidos)

def descomprimir_archivo(input_file, output_file, raiz):
    bits = ''
    with open(input_file, 'rb') as file:
        byte = file.read(1)
        while byte:
            bits += bin(ord(byte))[2:].rjust(8, '0')
            byte = file.read(1)

    nodo_actual = raiz
    contenido_descomprimido = ''
    for bit in bits:
        if bit == '0':
            nodo_actual = nodo_actual.izquierda
        else:
            nodo_actual = nodo_actual.derecha
        if nodo_actual.caracter is not None:
            contenido_descomprimido += nodo_actual.caracter
            nodo_actual = raiz

    with open(output_file, 'w') as file:
        file.write(contenido_descomprimido)

class HuffmanFrontend:
    def __init__(self, master):
        self.master = master
        master.title("Compresor de Archivos")
        
        self.examinar_button = tk.Button(master, text="Examinar", command=self.examinar_archivo)
        self.examinar_button.grid(row=4, column=1, padx=(10, 2), pady=20, sticky="ew")
        
        self.comprimir_button = tk.Button(master, text="Comprimir", command=self.comprimir_archivo, state=tk.DISABLED)
        self.comprimir_button.grid(row=4, column=2, padx=2, pady=20, sticky="ew")
        
        self.descomprimir_button = tk.Button(master, text="Descomprimir", command=self.descomprimir_archivo, state=tk.DISABLED)
        self.descomprimir_button.grid(row=4, column=3, padx=2, pady=20, sticky="ew")
        
        self.entradaCadena = tk.Text(master, width=80, height=3, wrap=tk.WORD)
        self.entradaCadena.grid(row=1, column=1, columnspan=5, padx=5, pady=10, sticky="w")
        
        self.entradaFrecuencia = tk.Text(master, width=80, height=8, wrap=tk.WORD)
        self.entradaFrecuencia.grid(row=2, column=1, columnspan=5, padx=5, pady=10, sticky="w")
        
        self.entradaArbol = tk.Text(master, width=80, height=11, wrap=tk.WORD)
        self.entradaArbol.grid(row=3, column=1, columnspan=5, padx=5, pady=10, sticky="w")
        
    def examinar_archivo(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.archivo = file_path
            self.comprimir_button.config(state=tk.NORMAL)
            self.descomprimir_button.config(state=tk.NORMAL)
            with open(self.archivo, 'r') as file:
                contenido = file.read()
                self.entradaCadena.delete('1.0', tk.END) 
                self.entradaCadena.insert(tk.END, contenido) 
                self.calcular_frecuencia()
                
    def calcular_frecuencia(self):
        with open(self.archivo, 'r') as file:
            contenido = file.read().replace(' ', '')
            self.frecuencias = Counter(contenido)
            self.entradaFrecuencia.delete('1.0', tk.END) 
            for caracter, frecuencia in self.frecuencias.items():
                self.entradaFrecuencia.insert(tk.END, f"{caracter}: {frecuencia}\n") 
            self.mostrar_arbol_huffman()
    
    def mostrar_arbol_huffman(self):
        arbol_huffman = construir_arbol_huffman(self.frecuencias)
        self.entradaArbol.delete('1.0', tk.END) 
        self.dibujar_arbol(arbol_huffman)
    
    def dibujar_arbol(self, nodo, nivel=0):
        if nodo:
            self.entradaArbol.insert(tk.END, " " * nivel)
            self.entradaArbol.insert(tk.END, f"({nodo.frecuencia})\n")
            self.dibujar_arbol(nodo.izquierda, nivel + 1)
            self.dibujar_arbol(nodo.derecha, nivel + 1)
    
    def comprimir_archivo(self):
        output_file = self.archivo + '.huf'
    
        with open(self.archivo, 'r') as file:
            contenido = file.read().replace(' ', '')
    
        frecuencias = Counter(contenido)
        tabla_codigos = generar_tabla_codigos(construir_arbol_huffman(frecuencias))
    
        bits = ''
        for caracter in contenido:
            bits += tabla_codigos[caracter]
    
        padding = 8 - len(bits) % 8
        bits += padding * '0'

        bytes_comprimidos = bytearray()
        for i in range(0, len(bits), 8):
            byte = bits[i:i+8]
            bytes_comprimidos.append(int(byte, 2))

        with open(output_file, 'wb') as file:
            file.write(bytes_comprimidos)

        print("Archivo comprimido correctamente.")
    
    def descomprimir_archivo(self):
        if hasattr(self, 'archivo') and self.archivo.endswith('.huf'):
            output_file = self.archivo[:-4] 
            descomprimir_archivo(self.archivo, output_file, construir_arbol_huffman(self.frecuencias))
            print("Archivo descomprimido correctamente.")
        else:
            print("El archivo seleccionado no es un archivo comprimido.")

root = tk.Tk()
root.title("Algoritmo de Huffman")
root.geometry("800x550")
root.resizable(0, 0)

Titulo = tk.Label(root, text="ALGORITMO DE HUFFMAN")
Titulo.grid(row=0, column=0, columnspan=6, padx=30, pady=20, sticky="nsew")

cadena = tk.Label(root, text=" Cadena: ")
cadena.grid(row=1, column=0, padx=10, pady=10, sticky="w")

frecuencia = tk.Label(root, text=" Frecuencia: ")
frecuencia.grid(row=2, column=0, padx=10, pady=10, sticky="w")

arbol = tk.Label(root, text=" Arbol: ")
arbol.grid(row=3, column=0, padx=10, pady=10, sticky="w")

app = HuffmanFrontend(root)
root.mainloop()