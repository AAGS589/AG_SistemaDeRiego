import csv

class Terreno:
    def __init__(self, ladoX, ladoY):
        self.ladoX = ladoX
        self.ladoY = ladoY

    def generar_coordenadas(self, arboles, espacio_borde, espacio_adicional_x, espacio_adicional_y):
        coordenadas = []
        x_actual = espacio_borde
        y_actual = espacio_borde + espacio_adicional_y
        tipos_arboles = list(arboles.keys())

        filas = 5
        columnas = 5

        ancho_celda = (self.ladoX - 2 * espacio_borde) / columnas
        alto_celda = (self.ladoY - 2 * espacio_borde) / filas

        for fila in range(filas):
            for columna in range(columnas):
                tipo = tipos_arboles[(fila * columnas + columna) % len(tipos_arboles)]
                radio = arboles[tipo]

                x_celda = espacio_borde + columna * ancho_celda
                y_celda = espacio_borde + fila * alto_celda

                x_centro = x_celda + ancho_celda / 2
                y_centro = y_celda + alto_celda / 2

                arbol = (tipo, x_centro, y_centro)
                coordenadas.append(arbol)

        return coordenadas

    def distancia_minima(self, tipo1, tipo2):
        radios_copas = {"Mango": 7.5, "Limon": 5, "Nanche": 5, "Aguacate": 6, "Coco": 9}
        return radios_copas[tipo1] + radios_copas[tipo2]

    def guardar_coordenadas_csv(self, coordenadas, archivo):
        with open(archivo, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Tipo", "X", "Y"])
            for coord in coordenadas:
                writer.writerow(coord)

arboles = {
    'Mango': 7.5,
    'Limon': 5,
    'Nanche': 5,
    'Aguacate': 6,
    'Coco': 9,
}

terreno = Terreno(188, 188)
espacio_borde = 2
espacio_adicional_x = 2
espacio_adicional_y = 2

coordenadas = terreno.generar_coordenadas(arboles, espacio_borde, espacio_adicional_x, espacio_adicional_y)
terreno.guardar_coordenadas_csv(coordenadas, 'arboles2.csv')

