import random
import itertools
import csv
import os
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
        
        self.arboles_plantados = None
        self.mejor_individuo = None
        self.penalizacion_cruces = 0.1
        

        self.input_pobInicial.setText("20")   
        self.input_pobMaxima.setText("25")
        self.input_numGeneraciones.setText("50")
        self.input_presicion.setText("0.1")
        self.input_probCruza.setText("0.01")
        self.input_probMutacionIndividuo.setText("0.25")
        self.input_probMutacionGen.setText("0.99")
        
        self.dimensionesTerreno = 35344
        self.ladoX = 188
        self.ladoY = self.dimensionesTerreno / self.ladoX
        self.manguera = (0,0)

       
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
       
        
        self.arboles_plantados = self.generar_arboles_plantados()

      
        poblacion_inicial = self.generar_poblacion_inicial(self.arboles_plantados, self.pobInicial)

        
        self.mejor_individuo = self.algoritmo_genetico(poblacion_inicial, self.arboles_plantados)

        
        aptitud_mejor_individuo = self.funcion_aptitud(self.mejor_individuo, self.arboles_plantados)
           
       
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
    
    def arbol_valido(self, nuevo_arbol, arboles_plantados):
        x1, y1, tipo1 = nuevo_arbol
        for arbol in arboles_plantados:
            x2, y2, tipo2 = arbol
            distancia = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
            if distancia < self.distancia_minima(tipo1, tipo2):
                return False
        return True
    
    def distancia_minima(self, tipo1, tipo2):
        radios_copas = {"Mango": 7.5, "Limon": 5, "Nanche": 5, "Aguacate": 6, "Coco": 9}
        return radios_copas[tipo1] + radios_copas[tipo2]


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
        print("---------------------------Generando árboles---------------------------")
        arboles_plantados = []

        with open(archivo, "r") as f:
            reader = csv.reader(f)
            next(reader)  
            for row in reader:
                tipo, x, y = row
                arbol = (float(x), float(y), tipo)

                
                if 0 <= arbol[0] < self.ladoX and 0 <= arbol[1] < self.ladoY:
                    
                    if self.arbol_valido(arbol, arboles_plantados):
                        arboles_plantados.append(arbol)
                    else:
                        print(f"Advertencia: El árbol {arbol} no cumple con la distancia mínima y no será agregado.")
                else:
                    print(f"Advertencia: El árbol {arbol} está fuera de los límites del terreno y no será agregado.")
        print("---------------------------FIN    METODO ARBOLES PLANTADOS---------------------------")
        return arboles_plantados

    


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

        
    def algoritmo_genetico(self, poblacion, arboles_plantados):
        mejor_individuo = None
        mejor_aptitud = float('inf')
        mejora_aptitud = float('inf')
        self.mejor_aptitud_por_generacion = []

        generacion = 0
        while generacion < self.numGeneraciones and mejora_aptitud >= self.precision:

            aptitudes = [self.funcion_aptitud(individuo, arboles_plantados) for individuo in poblacion]

            indice_mejor_individuo = aptitudes.index(min(aptitudes))
            aptitud_mejor_individuo = aptitudes[indice_mejor_individuo]

            if aptitud_mejor_individuo < mejor_aptitud:
                mejora_aptitud = mejor_aptitud - aptitud_mejor_individuo
                mejor_aptitud = aptitud_mejor_individuo
                mejor_individuo = poblacion[indice_mejor_individuo]

            self.mejor_aptitud_por_generacion.append(mejor_aptitud)

            individuos_seleccionados = self.seleccion(poblacion, aptitudes)

            nueva_poblacion = []

            while len(nueva_poblacion) < len(poblacion):

                padre1 = random.choice(individuos_seleccionados)
                padre2 = random.choice(individuos_seleccionados)

                hijo = self.cruza(padre1, padre2)

                if random.random() < self.probMutacionIndividuo:
                    hijo = self.mutacion(hijo)

                nueva_poblacion.append(hijo)

            poblacion = self.poda(nueva_poblacion)

            poblacion = nueva_poblacion

            # Guardar la imagen del recorrido de la generación actual
            self.guardar_manguera_riego_por_generacion(arboles_plantados, mejor_individuo, self.manguera, generacion)

            print(f"Mejor individuo en la generación {generacion}: {mejor_individuo}")
            generacion += 1

        # Al final de todas las generaciones
        mejor_individuo = self.optimizacion_local_3_opt(mejor_individuo, arboles_plantados)

        self.guardar_manguera_riego_por_generacion(arboles_plantados, mejor_individuo, self.manguera, generacion)

        return mejor_individuo

    def se_cruzan(self, a, b, c, d):
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

        return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)


    def funcion_aptitud(self, individuo, arboles_plantados):
        def distancia(arbol1, arbol2):
            x1, y1, *_ = arbol1
            x2, y2, *_ = arbol2

            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

        bomba_de_agua = (0, 0)

        distancia_total = distancia(bomba_de_agua, arboles_plantados[individuo[0]])

        distancia_total += sum(distancia(arboles_plantados[individuo[i]], arboles_plantados[individuo[i + 1]])
                            for i in range(len(individuo) - 1))

        distancia_total += distancia(arboles_plantados[individuo[-1]], bomba_de_agua)

        penalizaciones_cruces = 0
        for i, arbol1 in enumerate(arboles_plantados):
            for j, arbol2 in enumerate(arboles_plantados):
                arbol3 = arboles_plantados[individuo[i - 1]]
                arbol4 = arboles_plantados[individuo[j - 1]]
                if i != j and self.se_cruzan(arbol1, arbol2, arbol3, arbol4):
                    penalizaciones_cruces += self.penalizacion_cruces

        return distancia_total + penalizaciones_cruces


    
    def seleccion(self, poblacion, aptitudes, k=2):
        seleccionados = []
        for _ in range(len(poblacion)):
            competidores = random.sample(list(enumerate(aptitudes)), k)
            ganador, aptitud_ganador = min(competidores, key=lambda x: x[1])
            seleccionados.append(poblacion[ganador])
        
        return seleccionados

    def cruza(self, padre1, padre2):
       
        punto_corte1 = random.randint(0, len(padre1) - 1)
        punto_corte2 = random.randint(0, len(padre1) - 1)

        if punto_corte1 > punto_corte2:
            punto_corte1, punto_corte2 = punto_corte2, punto_corte1
      
        hijo = [None] * len(padre1)
        hijo[punto_corte1:punto_corte2] = padre1[punto_corte1:punto_corte2]
        
        elementos_faltantes = [x for x in padre2 if x not in hijo[punto_corte1:punto_corte2]]

        for i in range(len(hijo)):
            if hijo[i] is None:
                hijo[i] = elementos_faltantes.pop(0)

        return hijo

    def mutacion(self, individuo):
        pos1 = random.randint(0, len(individuo) - 1)
        pos2 = random.randint(0, len(individuo) - 1)
       
        individuo[pos1], individuo[pos2] = individuo[pos2], individuo[pos1]
        return individuo
    
    def poda(self, poblacion, porcentaje_sobrevivientes=0.5):
        n_sobrevivientes = int(len(poblacion) * porcentaje_sobrevivientes)
        aptitudes = [self.funcion_aptitud(individuo, self.arboles_plantados) for individuo in poblacion]
        indices_ordenados = sorted(range(len(aptitudes)), key=lambda i: aptitudes[i], reverse=True)
        nueva_poblacion = [poblacion[i] for i in indices_ordenados[:n_sobrevivientes]]
        return nueva_poblacion
    
    def optimizacion_local_3_opt(self, individuo, arboles_plantados, max_iteraciones=100):
        def swap_3_opt(individuo, i, j, k):
            nuevo_individuo = individuo[:i] + individuo[i:j][::-1] + individuo[j:k][::-1] + individuo[k:]
            return nuevo_individuo

        mejor_individuo = individuo[:]
        mejor_aptitud = self.funcion_aptitud(individuo, arboles_plantados)

        n = len(individuo)
        iteracion = 0

        while iteracion < max_iteraciones:
            hubo_mejora = False
            for i in range(n):
                for j in range(i + 1, n):
                    for k in range(j + 1, n):
                        nuevo_individuo = swap_3_opt(mejor_individuo, i, j, k)
                        nueva_aptitud = self.funcion_aptitud(nuevo_individuo, arboles_plantados)

                        if nueva_aptitud < mejor_aptitud:
                            mejor_individuo = nuevo_individuo[:]
                            mejor_aptitud = nueva_aptitud
                            hubo_mejora = True

            if not hubo_mejora:
                break

            iteracion += 1

        return mejor_individuo


    def visualizar_arboles_plantados(self, arboles_plantados):
        plt.figure(figsize=(9, 5))
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

        plt.xlim(-5, self.ladoX + 5)
        plt.ylim(-5, self.ladoY + 5)

        plt.xlabel("Eje X")
        plt.ylabel("Eje Y")
        plt.title("Distribución de árboles plantados")

        
        plt.legend(loc="upper left", bbox_to_anchor=(1.05, 1), borderaxespad=0)

        plt.tight_layout()
        plt.show()

    def visualizar_manguera_riego(self, arboles_plantados, mejor_individuo, manguera):
        fig, ax = plt.subplots(figsize=(10, 6))
        colores = {"Mango": "red", "Limon": "green", "Nanche": "blue", "Aguacate": "yellow", "Coco": "purple"}

        elementos_leyenda = []

        for tipo, color in colores.items():
            elementos_leyenda.append(Line2D([0], [0], marker='o', color='w', label=tipo, markerfacecolor=color, markersize=8))

        for x, y, tipo in arboles_plantados:
            plt.scatter(x, y, color=colores[tipo], marker='o', s=50)
            plt.text(x, y, f"({int(x)}, {int(y)})", fontsize=10)

        ruta = [arboles_plantados[i] for i in mejor_individuo]

        arbol_cercano = self.arbol_mas_cercano(manguera, arboles_plantados)
        ruta.insert(0, arbol_cercano)

        ruta_x = [x for x, y, tipo in ruta]
        ruta_y = [y for x, y, tipo in ruta]

        plt.plot(ruta_x, ruta_y, color="black", linewidth=1, linestyle='--')

        plt.plot([manguera[0], arbol_cercano[0]], [manguera[1], arbol_cercano[1]], color="black", linewidth=1, linestyle="--")

        plt.scatter(*manguera, color="black", marker='s', s=50)
        plt.text(manguera[0], manguera[1], "Bomba", fontsize=12)

        for i in range(len(ruta) - 1):
            x1, y1, _ = ruta[i]
            x2, y2, _ = ruta[i + 1]
            plt.arrow(x1, y1, x2 - x1, y2 - y1, color="black", linestyle='--', length_includes_head=True, head_width=2, head_length=2)

        ultimo_arbol = ruta[-1]
        plt.scatter(ultimo_arbol[0], ultimo_arbol[1], color="orange", marker="*", s=100)
        plt.text(ultimo_arbol[0], ultimo_arbol[1], "Fin manguera", fontsize=12)

        plt.xlim(0, self.ladoX)
        plt.ylim(0, self.ladoY)

        plt.legend(handles=elementos_leyenda, loc="upper left", bbox_to_anchor=(1.05, 1), borderaxespad=0)
        plt.title("Plantación y recorrido de la manguera de riego")
        plt.tight_layout()
        plt.show()



    def graficar_aptitud(self):
        plt.plot(self.mejor_aptitud_por_generacion)
        plt.xlabel("Generación")
        plt.ylabel("Aptitud")
        plt.title("Evolución de la aptitud del mejor individuo")
        plt.show()
    
    def guardar_manguera_riego_por_generacion(self, arboles_plantados, mejor_individuo_por_generacion, manguera, generacion):
        fig, ax = plt.subplots(figsize=(10, 6))
        colores = {"Mango": "red", "Limon": "green", "Nanche": "blue", "Aguacate": "yellow", "Coco": "purple"}

        for arbol in arboles_plantados:
            x, y, tipo = arbol
            plt.scatter(x, y, c=colores[tipo], label=tipo, alpha=0.5)
        
        # Dibujar manguera de riego
        manguera_xy = [(arboles_plantados[i][0], arboles_plantados[i][1]) for i in mejor_individuo_por_generacion]
        manguera_xy.append((arboles_plantados[mejor_individuo_por_generacion[0]][0], arboles_plantados[mejor_individuo_por_generacion[0]][1]))
        manguera_line, = plt.plot(*zip(*manguera_xy), linestyle='-', color='black', linewidth=1, alpha=0.8)

        # Crear el directorio 'img' si no existe
        if not os.path.exists("img"):
            os.makedirs("img")

        # Guardar la imagen en el directorio 'img' con el número de generación en el nombre del archivo
        #print(f"Guardando imagen para la generación {generacion} en img/generacion_{generacion}.png")
        plt.savefig(f"img/generacion_{generacion}.png", bbox_inches="tight")
        plt.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    GUI = AG()
    GUI.show()
    sys.exit(app.exec_())