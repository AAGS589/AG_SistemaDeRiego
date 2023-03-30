import random
import itertools
import csv
from random import sample
import math
import matplotlib.pyplot as plt
import pandas as pd 
from matplotlib import pyplot
from matplotlib.lines import Line2D
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication

class AG(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("style.ui",self)
        # ... (Widgets existentes)
        self.arboles_plantados = None
        self.mejor_individuo = None

        self.input_pobInicial.setText("50")   
        self.input_pobMaxima.setText("200")
        self.input_numGeneraciones.setText("2000")
        self.input_presicion.setText("0.99")
        self.input_probCruza.setText("0.01")
        self.input_probMutacionIndividuo.setText("0.25")
        self.input_probMutacionGen.setText("0.99")
        
        self.dimensionesTerreno = 35344
        self.ladoX = 188
        self.ladoY = self.dimensionesTerreno / self.ladoX
        self.manguera = (0,0)

        # Botones
        self.btn_iniciarAlgoritmo.clicked.connect(self.iniciarAlgoritmo)
        self.btn_verPlantacion.clicked.connect(self.verPlantacion)
        self.btn_verMangueraRiego.clicked.connect(self.verMangueraRiego)
        self.btn_graficaAptitud.clicked.connect(self.graficar_aptitud)


    def iniciarAlgoritmo(self):
        print("Iniciando Calculos.......")

        try:
            self.pobInicial = int(self.input_pobInicial.text())
            self.pobMaxima = int(self.input_pobMaxima.text())
            self.numGeneraciones = int(self.input_numGeneraciones.text())
            self.precision = float(self.input_presicion.text())
            self.probCruza = float(self.input_probCruza.text())
            self.probMutacionIndividuo = float(self.input_probMutacionIndividuo.text())
            self.probMutacionGen = float(self.input_probMutacionGen.text())
        except ValueError:
            print("Error: Por favor, ingrese valores válidos para todos los parámetros.")
            return
       
        # Generar lista de árboles plantados en el terreno
        self.arboles_plantados = self.generar_arboles_plantados()

        # Generar población inicial
        poblacion_inicial = self.generar_poblacion_inicial(self.arboles_plantados, self.pobInicial)

        # Ejecutar algoritmo genético
        self.mejor_individuo = self.algoritmo_genetico(poblacion_inicial, self.arboles_plantados)

        # Calcular la aptitud del mejor individuo
        aptitud_mejor_individuo = self.funcion_aptitud(self.mejor_individuo, self.arboles_plantados)
           
        # Mostrar resultados
        print("Mejor recorrido de manguera:", self.mejor_individuo)
        print("Aptitud del mejor recorrido de manguera:", aptitud_mejor_individuo)

    
    def verPlantacion(self):
        if self.arboles_plantados is not None:
            self.visualizar_arboles_plantados(self.arboles_plantados)
        else:
            print("La plantación no ha sido generada todavía.")

    def verMangueraRiego(self):
        if self.arboles_plantados is not None and self.mejor_individuo is not None:
            self.visualizar_manguera_riego(self.arboles_plantados, self.mejor_individuo, self.manguera)
        else:
            print("La plantación y/o el recorrido de la manguera no han sido generados todavía.")
    
    def distancia_minima(self, tipo1, tipo2):
        radios_copas = {"Mango": 7.5, "Limon": 5, "Nanche": 5, "Aguacate": 6, "Coco": 9}
        return radios_copas[tipo1] + radios_copas[tipo2]

    def arbol_valido(self, nuevo_arbol, arboles_plantados):
        x1, y1, tipo1 = nuevo_arbol
        for arbol in arboles_plantados:
            x2, y2, tipo2 = arbol
            distancia = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
            if distancia < self.distancia_minima(tipo1, tipo2):
                return False
        return True

    def arbol_mas_cercano(self, manguera, arboles):
        arbol_cercano = None
        distancia_minima = float('inf')
        
        for arbol in arboles:
            distancia = ((manguera[0] - arbol[0]) ** 2 + (manguera[1] - arbol[1]) ** 2) ** 0.5
            if distancia < distancia_minima:
                distancia_minima = distancia
                arbol_cercano = arbol
                
        return arbol_cercano


    def generar_arboles_plantados(self, archivo="arboles2.csv"):
        arboles_plantados = []

        with open(archivo, "r") as f:
            reader = csv.reader(f)
            next(reader)  # Saltar la fila del encabezado (Tipo, X, Y)
            for row in reader:
                tipo, x, y = row
                arbol = (float(x), float(y), tipo)

                # Validar que el árbol esté dentro de los límites del terreno
                if 0 <= arbol[0] < self.ladoX and 0 <= arbol[1] < self.ladoY:
                    # Validar que el árbol cumpla con la distancia mínima
                    if self.arbol_valido(arbol, arboles_plantados):
                        arboles_plantados.append(arbol)
                    else:
                        print(f"Advertencia: El árbol {arbol} no cumple con la distancia mínima y no será agregado.")
                else:
                    print(f"Advertencia: El árbol {arbol} está fuera de los límites del terreno y no será agregado.")
        print("---------------------------FIN    METODO ARBOLES PLANTADOS---------------------------")
        return arboles_plantados

    def visualizar_arboles_plantados(self, arboles_plantados):
        plt.figure(figsize=(7, 7))
        colors = {"Mango": "red", "Limon": "green", "Nanche": "blue", "Aguacate": "cyan", "Coco": "magenta"}
        markers = {"Mango": "o", "Limon": "s", "Nanche": "v", "Aguacate": "D", "Coco": "^"}
        labels = set()

        for arbol in arboles_plantados:
            x, y, tipo_arbol = arbol
            color = colors[tipo_arbol]
            marker = markers[tipo_arbol]

            if tipo_arbol not in labels:
                plt.scatter(x, y, c=color, label=tipo_arbol, marker=marker)
                labels.add(tipo_arbol)
            else:
                plt.scatter(x, y, c=color, marker=marker)

        plt.xlim(0, self.ladoX)
        plt.ylim(0, self.ladoY)

        plt.xlabel("Eje X")
        plt.ylabel("Eje Y")
        plt.title("Distribución de árboles plantados")

        # Ajusta la leyenda para que se adapte a la ventana
        plt.legend(loc="upper left", bbox_to_anchor=(1.05, 1), borderaxespad=0)

        plt.tight_layout()
        plt.show()

    # Esta función debe generar una población inicial de individuos,
    # donde cada individuo es una permutación aleatoria de la lista de árboles.
    def generar_poblacion_inicial(self, arboles_plantados, pobInicial):
        print("---------------------------INICIO METODO POBLACION INICIAL---------------------------")
        poblacion = []
        
        for _ in range(pobInicial):
            individuo = list(range(len(arboles_plantados)))
            random.shuffle(individuo)
            poblacion.append(individuo)
        print(poblacion)
        print("---------------------------FIN    METODO POBLACION INICIAL---------------------------")
        return poblacion

        # La función debe devolver el mejor individuo (recorrido de manguera) encontrado.
    def algoritmo_genetico(self, poblacion, arboles_plantados):
        mejor_individuo = None
        mejor_aptitud = float('inf')
        mejora_aptitud = float('inf')
        self.mejor_aptitud_por_generacion = []

        generacion = 0
        while generacion < self.numGeneraciones and mejora_aptitud >= self.precision:
            # Calcular las aptitudes de todos los individuos en la población
            aptitudes = [self.funcion_aptitud(individuo, arboles_plantados) for individuo in poblacion]

            # Actualizar el mejor individuo si se encuentra uno mejor en la población actual
            indice_mejor_individuo = aptitudes.index(min(aptitudes))
            aptitud_mejor_individuo = aptitudes[indice_mejor_individuo]

            if aptitud_mejor_individuo < mejor_aptitud:
                mejora_aptitud = mejor_aptitud - aptitud_mejor_individuo
                mejor_aptitud = aptitud_mejor_individuo
                mejor_individuo = poblacion[indice_mejor_individuo]
            
            self.mejor_aptitud_por_generacion.append(mejor_aptitud)

            # Seleccionar individuos para la cruza y la mutación
            individuos_seleccionados = self.seleccion(poblacion, aptitudes)

            # Crear una nueva población cruzando y mutando a los individuos seleccionados
            nueva_poblacion = []

            while len(nueva_poblacion) < len(poblacion):
                # Seleccionar dos padres al azar de los individuos seleccionados
                padre1 = random.choice(individuos_seleccionados)
                padre2 = random.choice(individuos_seleccionados)

                # Cruzar los padres para generar un hijo
                hijo = self.cruza(padre1, padre2)

                # Aplicar mutación al hijo con una cierta probabilidad
                if random.random() < self.probMutacionIndividuo:
                    hijo = self.mutacion(hijo)

                # Agregar el hijo a la nueva población
                nueva_poblacion.append(hijo)

            poblacion = self.poda(nueva_poblacion)
            # Reemplazar la población antigua con la nueva población
            poblacion = nueva_poblacion

            generacion += 1
        
        return mejor_individuo

        # Esta función debe calcular la suma de las distancias entre árboles
        # adyacentes en el recorrido de la manguera.
    def funcion_aptitud(self, individuo, arboles_plantados):
        def distancia(arbol1, arbol2):
            x1, y1, *_ = arbol1
            x2, y2, *_ = arbol2

            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


        # Agregar la posición de la bomba de agua
        bomba_de_agua = (self.ladoX / 2, 0)

        # Distancia desde la bomba de agua al primer árbol
        distancia_total = distancia(bomba_de_agua, arboles_plantados[individuo[0]])

        # Distancia entre árboles adyacentes
        distancia_total += sum(distancia(arboles_plantados[individuo[i]], arboles_plantados[individuo[i + 1]])
                                for i in range(len(individuo) - 1))

        # Distancia entre el último árbol y la bomba de agua
        distancia_total += distancia(arboles_plantados[individuo[-1]], bomba_de_agua)

        return distancia_total

        # Esta función debe seleccionar individuos de la población para la cruza
        # y mutación basándose en sus aptitudes (p. ej., usando selección por torneo).
    def seleccion(self, poblacion, aptitudes, k=2):
        seleccionados = []

        for _ in range(len(poblacion)):
            competidores = random.sample(list(enumerate(aptitudes)), k)
            ganador, aptitud_ganador = min(competidores, key=lambda x: x[1])
            seleccionados.append(poblacion[ganador])
        
        return seleccionados

    # Implementa un enfoque de cruza ordenada (OX) para este problema.
    def cruza(self, padre1, padre2):
        # Obtener dos puntos de corte aleatorios
        punto_corte1 = random.randint(0, len(padre1) - 1)
        punto_corte2 = random.randint(0, len(padre1) - 1)

        # Asegurar que punto_corte1 <= punto_corte2
        if punto_corte1 > punto_corte2:
            punto_corte1, punto_corte2 = punto_corte2, punto_corte1

        # Copiar la sección intermedia del primer padre al hijo
        hijo = [None] * len(padre1)
        hijo[punto_corte1:punto_corte2] = padre1[punto_corte1:punto_corte2]

        # Copiar los elementos restantes del segundo padre al hijo, manteniendo el orden relativo
        elementos_faltantes = [x for x in padre2 if x not in hijo[punto_corte1:punto_corte2]]

        # Colocar los elementos faltantes en las posiciones correctas del hijo
        for i in range(len(hijo)):
            if hijo[i] is None:
                hijo[i] = elementos_faltantes.pop(0)

        return hijo

        

    def mutacion(self, individuo):
     
        # Seleccionar dos posiciones aleatorias dentro del individuo
        pos1 = random.randint(0, len(individuo) - 1)
        pos2 = random.randint(0, len(individuo) - 1)

        # Intercambiar los elementos en las posiciones seleccionadas
        individuo[pos1], individuo[pos2] = individuo[pos2], individuo[pos1]
        return individuo
    
    def poda(self, poblacion, porcentaje_sobrevivientes=0.5):
        n_sobrevivientes = int(len(poblacion) * porcentaje_sobrevivientes)
        aptitudes = [self.funcion_aptitud(individuo, self.arboles_plantados) for individuo in poblacion]
        indices_ordenados = sorted(range(len(aptitudes)), key=lambda i: aptitudes[i], reverse=True)
        nueva_poblacion = [poblacion[i] for i in indices_ordenados[:n_sobrevivientes]]
        return nueva_poblacion


    def visualizar_manguera_riego(self, arboles_plantados, mejor_individuo, manguera):
        fig, ax = plt.subplots(figsize=(10, 8))
        colores = {"Mango": "red", "Limon": "green", "Nanche": "blue", "Aguacate": "yellow", "Coco": "purple"}

        # Crear una lista de elementos de leyenda
        elementos_leyenda = []

        for tipo, color in colores.items():
            elementos_leyenda.append(Line2D([0], [0], marker='o', color='w', label=tipo, markerfacecolor=color, markersize=8))

        for x, y, tipo in arboles_plantados:
            plt.scatter(x, y, color=colores[tipo], marker='o', s=50)

        # Dibujar la ruta de la manguera
        ruta = [arboles_plantados[i] for i in mejor_individuo]

        # Añadir el árbol más cercano al inicio de la ruta
        #manguera = (self.ladoX / 2, 0)
        arbol_cercano = self.arbol_mas_cercano(manguera, arboles_plantados)
        ruta.insert(0, arbol_cercano)

        ruta_x = [x for x, y, tipo in ruta]
        ruta_y = [y for x, y, tipo in ruta]

        plt.plot(ruta_x, ruta_y, color="black", linewidth=1, linestyle='--')

        # Dibujar la conexión entre la bomba y el árbol más cercano
        plt.plot([manguera[0], arbol_cercano[0]], [manguera[1], arbol_cercano[1]], color="black", linewidth=1, linestyle="--")

        plt.scatter(*manguera, color="black", marker='s', s=50)
        plt.text(manguera[0], manguera[1], "Bomba", fontsize=12)

        # Dibujar las flechas en la dirección de la manguera
        for i in range(len(ruta) - 1):
            x1, y1, _ = ruta[i]
            x2, y2, _ = ruta[i + 1]
            plt.arrow(x1, y1, x2 - x1, y2 - y1, color="black", linestyle='--', length_includes_head=True, head_width=2, head_length=2)

        # Marcar el final de la manguera
        ultimo_arbol = ruta[-1]
        plt.scatter(ultimo_arbol[0], ultimo_arbol[1], color="orange", marker="*", s=100)
        plt.text(ultimo_arbol[0], ultimo_arbol[1], "Fin manguera", fontsize=12)

        plt.xlim(0, self.ladoX)
        plt.ylim(0, self.ladoY)

        # Añadir la leyenda
        plt.legend(handles=elementos_leyenda, loc="upper left", bbox_to_anchor=(1.05, 1), borderaxespad=0)
        plt.title("Plantación y recorrido de la manguera de riego")
        plt.show()

    def graficar_aptitud(self):
        plt.plot(self.mejor_aptitud_por_generacion)
        plt.xlabel("Generación")
        plt.ylabel("Aptitud")
        plt.title("Evolución de la aptitud del mejor individuo")
        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    GUI = AG()
    GUI.show()
    sys.exit(app.exec_())