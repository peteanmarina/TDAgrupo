import random
import string
import pandas as pd
import numpy as np
import timeit
import time
import matplotlib.pyplot as plt
import solucion_pl as pl
import solucion_aproximacion as aprox
import solucion_backtracking as bt
import os
import glob
from scipy.optimize import curve_fit

def generar_nombre_aleatorio():
    return ''.join(random.choices(string.ascii_letters, k=5))

def generar_maestros_aleatorios(cantidad):
    maestros = {}
    for _ in range(cantidad):
        nombre = generar_nombre_aleatorio()
        habilidad = random.randint(1, 1000)
        maestros[nombre] = habilidad
    return maestros

def asignar_valores(k):
    cantidad_maestros = random.randint(k, 2 * k)
    maestros = generar_maestros_aleatorios(cantidad_maestros)
    return maestros

def generar_archivo(nombre_archivo):
    maestros = asignar_valores(random.randint(20, 35))
    with open(nombre_archivo, 'w') as file:
        file.write(f"{random.randint(5, 10)}\n")
        for nombre in maestros:
            file.write(f"{nombre}, {maestros[nombre]}\n")

def crear_sets():
    for i in range(1,10):
        generar_archivo(f"sets/set_largo_{i}.txt")

def generar_grafico_complejidad_teorica(solucion,tiempos,rango):
    name=""
    if solucion == "pl":  
        for r in rango:
            print(f"P.L {r}")
            name = "complejidad_pl.png"
    elif solucion == "bt":
        for r in rango:
            print(f"Backtraking {r}")
            name = "complejidad_bt.png"

    x = np.array(rango)
    y = np.array(tiempos)

    print(tiempos)

    popt, _ = ajustar_modelo_exponencial(x, y)

    plt.plot(x, y, 'r', label='Datos originales', markersize=8, color='blue')
    plt.plot(x, modelo_exponencial(x, *popt), label='Ajuste exponencial', color='green', linestyle='--', linewidth=2)
    plt.title('Ajuste de Complejidad Teórica (2^n) vs Tiempos de Ejecución')
    plt.xlabel('Tamaño de entrada (n)')
    plt.ylabel('Tiempo de ejecución (segundos)')
    plt.legend(loc='best')
    plt.grid(True, which='both', linestyle='--', linewidth=0.7)
    plt.ylim([0, max(y) * 1.1])
    plt.xlim([0, max(x) * 1.1])
    plt.savefig(name)
    plt.close()

def modelo_exponencial(x, a, b):
    return a * np.exp(b * x)

def ajustar_modelo_exponencial(x, y):
    popt, pcov = curve_fit(modelo_exponencial, x, y, p0=(1, 0.1))
    return popt, pcov

def generar_grafico_PL_BT():
    rango = range(7)
    
    print("P.L vs BT")

    tiempos_pl = []
    for r in rango:
        print(f"P.L {r}")
        tiempos_pl.append(timeit.timeit(lambda: pl.balancear_grupos_minima_diferencia(*asignar_valores(r)), globals=globals(), number=1))

    tiempos_bt = []
    for r in rango:
        print(f"Backtraking {r}")
        maestros, _ = asignar_valores(r)
        tiempos_bt.append(timeit.timeit(lambda: bt.backtrack(maestros, [[] for _ in range(r)], [0]*r, 0,r), globals=globals(), number=1))

    plt.plot(rango, tiempos_pl, 'r', label='Programacion Lineal',color='blue')
    plt.plot(rango, tiempos_bt, 'r', label='Backtraking',color='green')
    plt.xlabel('Tamaño de entrada (n)')
    plt.ylabel('Tiempo de ejecución (segundos)')
    plt.legend()
    plt.savefig('grafico_PL_BT.png')
    plt.close()
    generar_grafico_complejidad_teorica("pl",tiempos_pl,rango)
    generar_grafico_complejidad_teorica("bt", tiempos_bt,rango)
    
def comparaciones():

    archivos_nuestros = glob.glob(os.path.join('./sets', '*'))

    cota = []
    cadena = ""
    for archivo in archivos_nuestros:
        print(archivo)
        maestros_agua = {}
        with open(archivo, "r") as archivo:
            grupos = int(archivo.readline().strip())
            for linea in archivo:
                nombre, valor = map(str, linea.strip().split(','))
                maestro, habilidad = nombre,int(valor)
                maestros_agua[maestro] = habilidad

        inicio = time.time()
        coef, mejor_asignacion = pl.balancear_grupos_minima_diferencia(maestros_agua,grupos)
        fin = time.time()
        cadena+= f"-> {archivo.name} por minima diferencia\n"
        for i, grupo in enumerate(mejor_asignacion, 1):
            cadena+=f"Grupo {i}: {', '.join(grupo)}\n"
        cadena += f"Coeficiente: {coef}\n {archivo.name} - tardo {fin - inicio} segundos.\n\n"

        inicio = time.time()
        coef, mejor_asignacion = pl.balancear_grupos_mininima_desviacion(maestros_agua,grupos)
        fin = time.time()
        cadena+= f"-> {archivo.name} por minima desviacion\n"
        for i, grupo in enumerate(mejor_asignacion, 1):
            cadena+=f"Grupo {i}: {', '.join(grupo)}\n"
        cadena += f"Coeficiente: {coef}\n {archivo.name} - tardo {fin - inicio} segundos.\n\n"
        inicio = time.time()
        coef, mejor_asignacion = bt.backtrack(maestros_agua, [[] for _ in range(grupos)], [0]*grupos, 0,grupos)
        fin = time.time()
        cadena+= f"-> {archivo.name} por backtraking\n"
        for i, grupo in enumerate(mejor_asignacion, 1):
            cadena+=f"Grupo {i}: {', '.join(grupo)}\n"
        cadena += f"Coeficiente: {coef}\n {archivo.name} - tardo {fin - inicio} segundos.\n\n"        
        

        inicio = time.time()
        coef_aprox = aprox.aproximacion_tribu_agua(grupos,maestros_agua)
        fin = time.time()
        cadena+= f"-> {archivo.name} por aproximacion lineal\n"
        cadena += f"Coeficiente: {coef_aprox}\n {archivo.name} - tardo {fin - inicio} segundos.\n\n"

        cota.append(coef_aprox/coef)

    archivos_catedra = glob.glob(os.path.join('./sets_catedra', '*'))

    cadena_catedra = ""
    for archivo in archivos_catedra:
        print(archivo)
        maestros_agua = {}
        with open(archivo, "r") as archivo:
            grupos = int(archivo.readline().strip())
            for linea in archivo:
                nombre, valor = map(str, linea.strip().split(','))
                maestro, habilidad = nombre,int(valor)
                maestros_agua[maestro] = habilidad

        inicio = time.time()
        coef_aprox = aprox.aproximacion_tribu_agua(grupos,maestros_agua)
        fin = time.time()
        cadena_catedra+= f"-> {archivo.name} por aproximacion lineal\n"
        cadena_catedra += f"Coeficiente: {coef_aprox}\n\n"

    with open("sets/Comparaciones.txt", 'w') as archivo:
        archivo.write(cadena)
        archivo.write(f"Cota Empirica: {cota} con promedio {sum(cota)/len(archivos_nuestros)} y maximo {max(cota)}.")

    with open("sets/valores_aproximacion_catedra.txt", 'w') as archivo:
        archivo.write(cadena_catedra)
