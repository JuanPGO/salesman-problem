from leerInformacion import cargarCaso
from matrizDistancias import matrizEuclidiana, distanciaTour
from codificacionVecindarios import *
from heuristicas import *
from esqueletoConcurrencia import *
import os
import sys
import random
from pprint import pprint

def listar_archivos_tsp():
    """Listar todos los archivos .tsp en el directorio data/"""
    archivos = os.listdir("data")
    return [archivo for archivo in archivos if archivo.endswith(".tsp")]

def generarPoblacion(caso:dict, matriz:list) -> dict:
    """
    Genera una población inicial para el algoritmo genético combinando varias heurísticas
    """
    poblacion = []
    
    # Heurística 1: Vecino más cercano
    vecinoMasCercano = heuristicaVecinoMasCercano(caso, matriz)
    individuo1 = {
        'tour': vecinoMasCercano['tour'],
        'fo': distanciaTour(vecinoMasCercano, matriz)
    }
    poblacion.append(individuo1)
    
    # Heurística 2: Inserción más cercana
    insercionMasCercana = heuristicaInsercionMasCercana(caso, matriz)
    individuo2 = {
        'tour': insercionMasCercana['tour'],
        'fo': distanciaTour(insercionMasCercana, matriz)
    }
    poblacion.append(individuo2)
    
    # Heurística 3: Inserción más lejana
    insercionMasLejana = heuristicaInsercionMasLejana(caso, matriz)
    individuo3 = {
        'tour': insercionMasLejana['tour'],
        'fo': distanciaTour(insercionMasLejana, matriz)
    }
    poblacion.append(individuo3)
    
    # Heurística 4: Savings
    savings = heuristicaSavings(caso, matriz)
    individuo4 = {
        'tour': savings['tour'],
        'fo': distanciaTour(savings, matriz)
    }
    poblacion.append(individuo4)
    
    # Heurística 5: Christofides
    try:
        christofides = heuristicaChristofides(caso, matriz)
        individuo5 = {
            'tour': christofides['tour'],
            'fo': distanciaTour(christofides, matriz)
        }
        poblacion.append(individuo5)
    except Exception as e:
        print(f"No se pudo ejecutar Christofides: {e}")
    
    # Generar vecindarios a partir del mejor individuo
    # Ordenamos por función objetivo (menor es mejor)
    poblacion.sort(key=lambda ind: ind['fo'])
    mejor_individuo = poblacion[0]
    
    # Generamos vecindarios del mejor individuo encontrado
    vecindarioMejor = vecinos_concurrentes(mejor_individuo['tour'])
    for operacion, datos in vecindarioMejor:
        individuo = {
            'tour': datos['s_i'],
            'fo': datos['fo']
        }
        poblacion.append(individuo)
    
    return poblacion

def algoritmo_genetico_chu_beasley(caso, matriz, max_generaciones=100, tam_poblacion=10):
    """
    Implementa el algoritmo genético de Chu-Beasley para el TSP
    """
    # Generar población inicial
    poblacion = generarPoblacion(caso, matriz)
    
    # Mantener solo los mejores individuos si la población es muy grande
    poblacion.sort(key=lambda ind: ind['fo'])
    if len(poblacion) > tam_poblacion:
        poblacion = poblacion[:tam_poblacion]
    
    # Almacenar el mejor individuo de todas las generaciones
    mejor_global = poblacion[0]
    print(f"Generación 0: Mejor FO = {mejor_global['fo']}")
    
    # Evolución de la población
    for gen in range(1, max_generaciones + 1):
        # Selección de padres por torneo binario
        padre1 = seleccion_torneo(poblacion)
        padre2 = seleccion_torneo(poblacion)
        
        # Cruce OX (Order Crossover)
        hijo = cruce_ox(padre1['tour'], padre2['tour'])
        
        # Mutación con probabilidad
        if random.random() < 0.2:  # 20% de probabilidad de mutación
            hijo = mutacion_2opt(hijo)
        
        # Evaluar el hijo
        hijo_evaluado = {'tour': hijo, 'fo': calcular_fo(hijo, matriz)}
        
        # Reemplazo en la población siguiendo el esquema de Chu-Beasley
        reemplazo_chu_beasley(poblacion, hijo_evaluado)
        
        # Actualizar el mejor global
        if poblacion[0]['fo'] < mejor_global['fo']:
            mejor_global = poblacion[0]
            print(f"Generación {gen}: Mejor FO = {mejor_global['fo']}")
    
    return mejor_global

def seleccion_torneo(poblacion, tam_torneo=2):
    """Selección por torneo binario"""
    competidores = random.sample(poblacion, tam_torneo)
    return min(competidores, key=lambda ind: ind['fo'])

def cruce_ox(padre1, padre2):
    """Cruce OX (Order Crossover) para permutaciones"""
    n = len(padre1)
    # Puntos de corte
    punto1 = random.randint(0, n-2)
    punto2 = random.randint(punto1+1, n-1)
    
    # Inicializar hijo con -1 (valor no válido)
    hijo = [-1] * n
    
    # Copiar el segmento del padre1 entre los puntos de corte
    for i in range(punto1, punto2+1):
        hijo[i] = padre1[i]
    
    # Completar el hijo con los elementos del padre2 en orden
    j = (punto2 + 1) % n
    for i in range(n):
        # Iterar sobre los elementos del padre2
        elemento = padre2[(punto2 + 1 + i) % n]
        if elemento not in hijo:
            hijo[j] = elemento
            j = (j + 1) % n
            if j == punto1:
                break
    
    return hijo

def mutacion_2opt(tour):
    """Mutación usando el operador 2-opt"""
    n = len(tour)
    i = random.randint(1, n-2)
    j = random.randint(i+1, n-1)
    
    # Invertir el segmento entre i y j
    nuevo_tour = tour.copy()
    nuevo_tour[i:j+1] = reversed(tour[i:j+1])
    
    return nuevo_tour

def calcular_fo(tour, matriz):
    """Calcula la función objetivo (distancia total) de un tour"""
    distancia = 0
    n = len(tour)
    
    for i in range(n-1):
        indice_actual = tour[i] - 1
        indice_siguiente = tour[i+1] - 1
        distancia += matriz[indice_actual][indice_siguiente]
    
    # Cerrar el ciclo (último -> primero)
    indice_ultimo = tour[-1] - 1
    indice_primero = tour[0] - 1
    distancia += matriz[indice_ultimo][indice_primero]
    
    return distancia

def reemplazo_chu_beasley(poblacion, hijo):
    """
    Reemplazo siguiendo el esquema de Chu-Beasley:
    1. El hijo solo reemplaza a un individuo si es mejor
    2. Se reemplaza al peor individuo que sea diferente al hijo
    """
    # Ordenar población por FO (menor es mejor)
    poblacion.sort(key=lambda ind: ind['fo'])
    
    # Verificar que el hijo sea mejor que al menos el peor individuo
    if hijo['fo'] < poblacion[-1]['fo']:
        # Buscar el individuo más parecido al hijo para reemplazarlo
        max_similitud = 0
        indice_reemplazo = -1
        
        for i in range(len(poblacion)-1, -1, -1):
            # Calcular similitud (elementos en común)
            similitud = sum(1 for a, b in zip(poblacion[i]['tour'], hijo['tour']) if a == b)
            
            if similitud > max_similitud:
                max_similitud = similitud
                indice_reemplazo = i
        
        # Reemplazar el individuo elegido
        if indice_reemplazo >= 0:
            poblacion[indice_reemplazo] = hijo
            # Reordenar la población
            poblacion.sort(key=lambda ind: ind['fo'])

def algoritmo_ils(caso, matriz, max_iteraciones=100):
    """
    Implementa el algoritmo ILS (Iterated Local Search) para el TSP
    """
    # Generar solución inicial con la mejor heurística
    poblacion = generarPoblacion(caso, matriz)
    # Ordenar por FO (menor es mejor)
    poblacion.sort(key=lambda ind: ind['fo'])
    
    # Mejor solución inicial
    mejor_solucion = poblacion[0]
    print(f"Solución inicial: FO = {mejor_solucion['fo']}")
    
    # Iteraciones de ILS
    for i in range(max_iteraciones):
        # Búsqueda local en la solución actual
        vecindario = vecinos_concurrentes(mejor_solucion['tour'])
        # Encontrar el mejor vecino
        mejor_vecino = None
        for operacion, datos in vecindario:
            if mejor_vecino is None or datos['fo'] < mejor_vecino['fo']:
                mejor_vecino = {'tour': datos['s_i'], 'fo': datos['fo']}
        
        # Actualizar la mejor solución si se encontró una mejora
        if mejor_vecino and mejor_vecino['fo'] < mejor_solucion['fo']:
            mejor_solucion = mejor_vecino
            print(f"Iteración {i+1}: Mejor FO = {mejor_solucion['fo']}")
        else:
            # Si no hay mejora, aplicar perturbación
            solucion_perturbada = perturbar_solucion(mejor_solucion['tour'])
            fo_perturbada = calcular_fo(solucion_perturbada, matriz)
            
            # Continuar con la solución perturbada
            mejor_solucion = {'tour': solucion_perturbada, 'fo': fo_perturbada}
    
    return mejor_solucion

def perturbar_solucion(tour):
    """
    Perturba una solución aplicando múltiples movimientos aleatorios
    para escapar de óptimos locales
    """
    perturbado = tour.copy()
    n = len(perturbado)
    
    # Número de perturbaciones
    num_perturbaciones = random.randint(2, max(3, n // 10))
    
    for _ in range(num_perturbaciones):
        tipo_perturbacion = random.choice(['swap', '2opt', 'insert'])
        
        if tipo_perturbacion == 'swap':
            # Intercambiar dos ciudades aleatorias
            i, j = random.sample(range(n), 2)
            perturbado[i], perturbado[j] = perturbado[j], perturbado[i]
        
        elif tipo_perturbacion == '2opt':
            # Invertir un segmento aleatorio
            i = random.randint(0, n-2)
            j = random.randint(i+1, n-1)
            perturbado[i:j+1] = reversed(perturbado[i:j+1])
        
        elif tipo_perturbacion == 'insert':
            # Mover una ciudad a otra posición
            i = random.randint(0, n-1)
            j = random.randint(0, n-1)
            if i != j:
                ciudad = perturbado.pop(i)
                perturbado.insert(j, ciudad)
    
    return perturbado

def menu_principal():
    """
    Muestra el menú principal y maneja la selección del usuario
    """
    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Algoritmo TSP ILS (Iterated Local Search)")
        print("2. Algoritmo Genético (Chu-Beasley)")
        print("3. Salir")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            dataset = seleccionar_dataset()
            if dataset:
                print(f"\nEjecutando TSP ILS con el dataset {dataset}...")
                caso = cargarCaso(f"data/{dataset}")
                matriz = matrizEuclidiana(caso)
                mejor_solucion = algoritmo_ils(caso, matriz)
                
                print("\n=== RESULTADO FINAL ===")
                print(f"Mejor distancia encontrada: {mejor_solucion['fo']}")
                print(f"Tour: {mejor_solucion['tour']}")
        
        elif opcion == '2':
            dataset = seleccionar_dataset()
            if dataset:
                print(f"\nEjecutando Algoritmo Genético con el dataset {dataset}...")
                caso = cargarCaso(f"data/{dataset}")
                matriz = matrizEuclidiana(caso)
                mejor_solucion = algoritmo_genetico_chu_beasley(caso, matriz)
                
                print("\n=== RESULTADO FINAL ===")
                print(f"Mejor distancia encontrada: {mejor_solucion['fo']}")
                print(f"Tour: {mejor_solucion['tour']}")
        
        elif opcion == '3':
            print("Saliendo del programa...")
            break
        
        else:
            print("Opción no válida. Intente de nuevo.")

def seleccionar_dataset():
    """
    Muestra los datasets disponibles y permite al usuario seleccionar uno
    """
    archivos_tsp = listar_archivos_tsp()
    
    if not archivos_tsp:
        print("Error: No se encontraron datasets en el directorio 'data/'")
        return None
    
    print("\n=== DATASETS DISPONIBLES ===")
    for i, archivo in enumerate(archivos_tsp, 1):
        print(f"{i}. {archivo}")
    
    while True:
        try:
            opcion = int(input("\nSeleccione un dataset (número): "))
            if 1 <= opcion <= len(archivos_tsp):
                return archivos_tsp[opcion-1]
            else:
                print(f"Seleccione un número entre 1 y {len(archivos_tsp)}")
        except ValueError:
            print("Por favor, ingrese un número válido")

if __name__ == "__main__":
    menu_principal()
    



