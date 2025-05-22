from leerInformacion import cargarCaso
from matrizDistancias import matrizEuclidiana, distanciaTour
from codificacionVecindarios import *
from heuristicas import *
from esqueletoConcurrencia import *
import os
import sys
import random
import numpy as np
import multiprocessing as mp
from time import perf_counter
import math
from pprint import pprint

def listar_archivos_tsp():
    """Listar todos los archivos .tsp en el directorio data/"""
    archivos = os.listdir("data")
    return [archivo for archivo in archivos if archivo.endswith(".tsp")]

def es_tour_unico(tour, poblacion):
    """
    Verifica si un tour es único en la población.
    
    Args:
        tour: Tour a verificar
        poblacion: Lista de individuos en la población
        
    Returns:
        bool: True si el tour es único, False si ya existe en la población
    """
    return not any(np.array_equal(np.array(ind['tour']), np.array(tour)) for ind in poblacion)

def generarPoblacion(caso:dict, matriz:list) -> list:
    """
    Genera una población inicial para el algoritmo genético combinando 
    5 heurísticas diferentes, perturbaciones swap y soluciones aleatorias.
    
    Args:
        caso: Diccionario con los datos del problema TSP
        matriz: Matriz de distancias entre ciudades
        
    Returns:
        Lista de individuos que conforman la población inicial
    """
    # Calcular tamaño deseado de la población (mitad de la dimensión, redondeando hacia arriba)
    tam_poblacion_deseado = math.ceil(caso['dimension'] / 2)
    print(f"Tamaño de población deseado: {tam_poblacion_deseado} individuos")
    
    # Almacenar la población inicial
    población_inicial = []
    
    # 1. Generar individuos mediante heurísticas
    print("\n1. GENERACIÓN DE INDIVIDUOS POR HEURÍSTICAS")
    print("-"*40)
    
    # Heurística 1: Vecino más cercano
    inicio = time.time()
    resultado_vcn = heuristicaVecinoMasCercano(caso, matriz)
    tiempo_vcn = time.time() - inicio
    distancia_vcn = distanciaTour(resultado_vcn, matriz)
    
    individuo1 = {
        'tour': resultado_vcn['tour'],
        'fo': distancia_vcn,
        'tipo': 'Vecino más cercano',
        'tiempo': tiempo_vcn
    }
    población_inicial.append(individuo1)
    
    # Heurística 2: Inserción más cercana
    inicio = time.time()
    resultado_imc = heuristicaInsercionMasCercana(caso, matriz)
    tiempo_imc = time.time() - inicio
    distancia_imc = distanciaTour(resultado_imc, matriz)
    
    individuo2 = {
        'tour': resultado_imc['tour'],
        'fo': distancia_imc,
        'tipo': 'Inserción más cercana',
        'tiempo': tiempo_imc
    }
    población_inicial.append(individuo2)
    
    # Heurística 3: Inserción más lejana
    inicio = time.time()
    resultado_iml = heuristicaInsercionMasLejana(caso, matriz)
    tiempo_iml = time.time() - inicio
    distancia_iml = distanciaTour(resultado_iml, matriz)
    
    individuo3 = {
        'tour': resultado_iml['tour'],
        'fo': distancia_iml,
        'tipo': 'Inserción más lejana',
        'tiempo': tiempo_iml
    }
    población_inicial.append(individuo3)
    
    # Heurística 4: Savings
    inicio = time.time()
    resultado_savings = heuristicaSavings(caso, matriz)
    tiempo_savings = time.time() - inicio
    distancia_savings = distanciaTour(resultado_savings, matriz)
    
    individuo4 = {
        'tour': resultado_savings['tour'],
        'fo': distancia_savings,
        'tipo': 'Savings',
        'tiempo': tiempo_savings
    }
    población_inicial.append(individuo4)
    
    # Heurística 5: Christofides
    try:
        inicio = time.time()
        resultado_christofides = heuristicaChristofides(caso, matriz)
        tiempo_christofides = time.time() - inicio
        distancia_christofides = distanciaTour(resultado_christofides, matriz)
        
        individuo5 = {
            'tour': resultado_christofides['tour'],
            'fo': distancia_christofides,
            'tipo': 'Christofides',
            'tiempo': tiempo_christofides
        }
        población_inicial.append(individuo5)
    except Exception as e:
        print(f"No se pudo ejecutar Christofides: {e}")
    
    # Obtener tours semilla de las heurísticas
    tours_semilla = [ind['tour'] for ind in población_inicial]
    
    # Calcular cuántos individuos faltan por generar
    individuos_faltantes = tam_poblacion_deseado - len(población_inicial)
    print(f"\nSe requieren {individuos_faltantes} individuos adicionales para completar la población de {tam_poblacion_deseado}")
    
    if individuos_faltantes > 0:
        # Dividir en dos grupos: perturbación swap y aleatorios
        perturbaciones_requeridas = individuos_faltantes // 2
        aleatorios_requeridos = individuos_faltantes - perturbaciones_requeridas
        
        print(f"Se generarán:")
        print(f"- {perturbaciones_requeridas} individuos mediante perturbación swap")
        print(f"- {aleatorios_requeridos} individuos aleatorios")
        
        # Primero generar mediante perturbación swap (usando concurrencia)
        if perturbaciones_requeridas > 0:
            # Crear lista con los nombres de las heurísticas
            nombres_heuristicas = ["Vecino más cercano", "Inserción más cercana", "Inserción más lejana", "Savings", "Christofides"]
            # Ajustar si Christofides no está disponible
            if len(tours_semilla) < 5:
                nombres_heuristicas = nombres_heuristicas[:len(tours_semilla)]
            
            # Generar exactamente las perturbaciones requeridas
            print(f"\nGenerando {perturbaciones_requeridas} perturbaciones swap...")
            perturbaciones = generar_perturbaciones_swap_exactas(tours_semilla, matriz, perturbaciones_requeridas, nombres_heuristicas)
            
            # Añadir perturbaciones a la población, evitando duplicados
            for perturbacion in perturbaciones:
                nuevo_individuo = {
                    'tour': perturbacion['tour'],
                    'fo': perturbacion['fo'],
                    'tipo': f"Perturbación swap sobre {perturbacion['origen']}"
                }
                población_inicial.append(nuevo_individuo)
        
        # Luego generar individuos aleatorios
        if aleatorios_requeridos > 0:
            # Calcular cuántos individuos aleatorios faltan
            aleatorios_faltantes = tam_poblacion_deseado - len(población_inicial)
            
            # Generar individuos aleatorios
            print(f"\nGenerando {aleatorios_faltantes} individuos aleatorios...")
            individuos_aleatorios = generar_individuos_aleatorios(caso, matriz, aleatorios_faltantes, población_inicial)
            
            # Añadir a la población
            for individuo in individuos_aleatorios:
                nuevo_individuo = {
                    'tour': individuo['tour'],
                    'fo': individuo['fo'],
                    'tipo': 'Aleatorio'
                }
                población_inicial.append(nuevo_individuo)
    
    # Mostrar toda la información de la población generada
    print("\n=== POBLACIÓN INICIAL GENERADA ===")
    for i, individuo in enumerate(población_inicial):
        # Si es una heurística mostramos también el tiempo
        if 'tiempo' in individuo:
            print(f"Individuo {i+1}: {individuo['tipo']}: FO={individuo['fo']} (tiempo: {individuo['tiempo']:.4f}s)")
        else:
            print(f"Individuo {i+1}: {individuo['tipo']}: FO={individuo['fo']}")
        print(f"Tour: {individuo['tour']}")
    
    print(f"\nResumen: {len(población_inicial)} individuos de {tam_poblacion_deseado} deseados")
    if len(población_inicial) < tam_poblacion_deseado:
        print(f"Advertencia: No se pudo generar la población completa, se generaron {len(población_inicial)} individuos")
    
    return población_inicial

def generar_individuos_aleatorios(caso, matriz, cantidad, poblacion_existente):
    """
    Genera individuos aleatorios para la población inicial.
    Asegura que sean diferentes a los existentes en la población.
    
    Args:
        caso: Diccionario con la información del caso
        matriz: Matriz de distancias
        cantidad: Cantidad de individuos aleatorios a generar
        poblacion_existente: Lista de individuos ya existentes en la población
        
    Returns:
        Lista de individuos aleatorios generados
    """
    individuos_aleatorios = []
    dimension = caso['dimension']
    
    # Contador de intentos para evitar bucles infinitos
    max_intentos = cantidad * 10
    intentos = 0
    
    while len(individuos_aleatorios) < cantidad and intentos < max_intentos:
        # Generar tour aleatorio
        tour_aleatorio = list(range(1, dimension + 1))
        random.shuffle(tour_aleatorio)
        
        # Verificar si es único
        if es_tour_unico(tour_aleatorio, poblacion_existente) and es_tour_unico(tour_aleatorio, individuos_aleatorios):
            # Calcular FO
            fo = calcular_fo(tour_aleatorio, matriz)
            
            # Crear individuo
            individuo = {
                'tour': tour_aleatorio,
                'fo': fo
            }
            
            individuos_aleatorios.append(individuo)
        
        intentos += 1
    
    return individuos_aleatorios

def aplicar_perturbacion_swap(lista_compartida, tour_base, matriz, n_perturbaciones=1, origen_heuristica=None):
    """
    Aplica perturbaciones mediante intercambio de ciudades (swap)
    
    Args:
        lista_compartida: Lista compartida para almacenar resultados
        tour_base: Tour base para realizar perturbaciones
        matriz: Matriz de distancias
        n_perturbaciones: Número de perturbaciones a realizar
        origen_heuristica: Nombre de la heurística de origen del tour base
    """
    n = len(tour_base)
    mejor_tour = None
    mejor_fo = float('inf')
    
    for _ in range(n_perturbaciones):
        # Perturbación mediante intercambio de dos ciudades
        nuevo_tour = tour_base.copy()
        num_swaps = random.randint(1, min(5, n//10 + 1))
        
        for _ in range(num_swaps):
            i, j = random.sample(range(n), 2)
            nuevo_tour[i], nuevo_tour[j] = nuevo_tour[j], nuevo_tour[i]
        
        # Calcular FO
        fo = calcular_fo(nuevo_tour, matriz)
        
        if fo < mejor_fo:
            mejor_fo = fo
            mejor_tour = nuevo_tour
    
    if mejor_tour:
        resultado = {
            'tour': mejor_tour,
            'fo': mejor_fo,
            'tipo': 'swap',
            'origen': origen_heuristica
        }
        lista_compartida.append(resultado)

def generar_perturbaciones_swap(tours_semilla, matriz, n_perturbaciones, nombres_heuristicas=None):
    """
    Genera perturbaciones usando únicamente el operador swap (intercambio de ciudades)
    
    Args:
        tours_semilla: Lista de tours base para generar perturbaciones
        matriz: Matriz de distancias
        n_perturbaciones: Número de perturbaciones a generar por tour semilla
        nombres_heuristicas: Lista con los nombres de las heurísticas correspondientes a cada tour
        
    Returns:
        Lista de perturbaciones generadas
    """
    # Si no se proporcionan nombres, usar valores por defecto
    if nombres_heuristicas is None:
        nombres_heuristicas = [f"Heurística {i+1}" for i in range(len(tours_semilla))]
    
    # Instanciar el administrador de procesos
    manager = mp.Manager()
    # Creamos la memoria compartida
    lista_compartida = manager.list()
    
    # Lista para almacenar todos los procesos
    todos_procesos = []
    
    # Crear procesos para cada tour semilla
    for i, tour_base in enumerate(tours_semilla):
        proceso = mp.Process(
            target=aplicar_perturbacion_swap,
            args=(lista_compartida, tour_base, matriz, n_perturbaciones, nombres_heuristicas[i])
        )
        todos_procesos.append(proceso)
    
    # Iniciar medición de tiempo
    tiempo_inicio = perf_counter()
    
    # Iniciar todos los procesos
    for proceso in todos_procesos:
        proceso.start()
    
    # Esperar a que todos los procesos terminen
    for proceso in todos_procesos:
        proceso.join()
    
    # Finalizar medición de tiempo
    tiempo_fin = perf_counter()
    tiempo_ejecucion = tiempo_fin - tiempo_inicio
    
    print(f"Tiempo total de generación de perturbaciones swap: {tiempo_ejecucion:.4f}s")
    print(f"Total de perturbaciones swap generadas: {len(lista_compartida)}")
    
    # Convertir a lista normal y ordenar por calidad (menor FO es mejor)
    perturbaciones = list(lista_compartida)
    perturbaciones.sort(key=lambda x: x['fo'])
    
    return perturbaciones

def generar_individuo_aleatorio(lista_compartida, dimension, matriz, tours_existentes):
    """
    Función que ejecutará cada proceso para generar un individuo aleatorio
    
    Args:
        lista_compartida: Lista compartida para almacenar resultados
        dimension: Dimensión del problema
        matriz: Matriz de distancias
        tours_existentes: Lista de tours existentes para evitar duplicados
    """
    # Generar tour aleatorio
    tour_aleatorio = list(range(1, dimension + 1))
    random.shuffle(tour_aleatorio)
    
    # Verificar si es único
    es_unico = True
    for tour_existente in tours_existentes:
        if np.array_equal(np.array(tour_aleatorio), np.array(tour_existente)):
            es_unico = False
            break
            
    if es_unico:
        # Calcular FO
        fo = calcular_fo(tour_aleatorio, matriz)
        
        # Crear individuo
        individuo = {
            'tour': tour_aleatorio,
            'fo': fo,
            'tipo': 'aleatorio'
        }
        
        lista_compartida.append(individuo)

def algoritmo_genetico_chu_beasley(caso, matriz, max_generaciones=100):
    """
    Implementa el algoritmo genético de Chu-Beasley para el TSP
    
    Args:
        caso: Diccionario con los datos del problema
        matriz: Matriz de distancias
        max_generaciones: Número máximo de generaciones
        
    Returns:
        Diccionario con la mejor solución encontrada
    """
    # Generar población inicial
    población_inicial = generarPoblacion(caso, matriz)
    
    # Parámetros del algoritmo genético
    tam_población = len(población_inicial)
    prob_mutación = 0.2
    
    print(f"Parámetros: Generaciones={max_generaciones}, Tamaño población={tam_población}, Prob. mutación={prob_mutación}")
    
    # Ordenar población inicial por función objetivo
    población_inicial.sort(key=lambda ind: ind['fo'])
    mejor_individuo = población_inicial[0]
    
    print(f"Población inicial - Mejor individuo: FO={mejor_individuo['fo']}")
    
    # Evolución de la población
    población = población_inicial.copy()
    historial_mejoras = [(0, mejor_individuo['fo'])]
    
    # Número de generaciones sin mejora
    gen_sin_mejora = 0
    max_gen_sin_mejora = 20  # Criterio de parada si no hay mejoras
    
    # Tamaño de la generación concurrente (cuántos descendientes generar a la vez)
    tamaño_generacion = max(10, tam_población // 2)
    
    inicio = time.time()
    
    for gen in range(1, max_generaciones + 1):
        # Generar descendencia de forma concurrente
        print(f"\nGeneración {gen}: Generando {tamaño_generacion} descendientes concurrentemente...")
        descendientes = generar_descendencia_concurrente(población, matriz, tamaño_generacion, prob_mutación)
        
        # Ordenar descendientes por calidad (menor FO es mejor)
        descendientes.sort(key=lambda ind: ind['fo'])
        
        # Verificar si hay mejora global
        hay_mejora = False
        
        # Intentar incorporar los mejores descendientes en la población
        for hijo in descendientes:
            # Reemplazo en la población siguiendo el esquema de Chu-Beasley
            reemplazado = reemplazo_chu_beasley(población, hijo)
            
            # Si se realizó un reemplazo y mejoró el mejor global, registrarlo
            if reemplazado and población[0]['fo'] < mejor_individuo['fo']:
                mejor_individuo = población[0]
                historial_mejoras.append((gen, mejor_individuo['fo']))
                hay_mejora = True
                gen_sin_mejora = 0
                print(f"Mejora encontrada: FO = {mejor_individuo['fo']}")
        
        # Si no hubo mejora, incrementar contador
        if not hay_mejora:
            gen_sin_mejora += 1
        
        # Mostrar información cada 10 generaciones
        if gen % 10 == 0 or hay_mejora:
            print(f"Generación {gen}: Mejor FO = {mejor_individuo['fo']}, Generaciones sin mejora: {gen_sin_mejora}")
        
        # Criterio de parada si no hay mejoras durante muchas generaciones
        if gen_sin_mejora >= max_gen_sin_mejora:
            print(f"Terminando la búsqueda: {max_gen_sin_mejora} generaciones sin mejora")
            break
    
    tiempo_total = time.time() - inicio
    
    # Construir resultado final
    resultado = {
        'tour': mejor_individuo['tour'],
        'distancia': mejor_individuo['fo'],
        'tiempo': tiempo_total,
        'mejoras': len(historial_mejoras) - 1,
        'historial': historial_mejoras
    }
    
    print(f"\nResultado final: FO={mejor_individuo['fo']} (tiempo: {tiempo_total:.4f}s)")
    
    return resultado

def generar_descendencia_concurrente(poblacion, matriz, n_descendientes, prob_mutacion=0.2):
    """
    Genera descendencia de forma concurrente mediante torneos, cruces y mutaciones
    
    Args:
        poblacion: Población actual
        matriz: Matriz de distancias
        n_descendientes: Número de descendientes a generar
        prob_mutacion: Probabilidad de mutación
        
    Returns:
        Lista de descendientes generados
    """
    # Función que ejecutará cada proceso
    def generar_individuo(lista_compartida):
        # Selección de padres por torneo binario
        padre1 = seleccion_torneo(poblacion)
        padre2 = seleccion_torneo(poblacion)
        
        # Cruce OX (Order Crossover)
        hijo = cruce_ox(padre1['tour'], padre2['tour'])
        
        # Mutación con probabilidad
        if random.random() < prob_mutacion:
            hijo = mutacion_2opt(hijo)
        
        # Evaluar el hijo
        fo_hijo = calcular_fo(hijo, matriz)
        hijo_evaluado = {'tour': hijo, 'fo': fo_hijo}
        
        # Añadir a la lista compartida
        lista_compartida.append(hijo_evaluado)
    
    # Instanciar el administrador de procesos
    manager = mp.Manager()
    # Creamos la memoria compartida
    lista_compartida = manager.list()
    
    # Lista para almacenar todos los procesos
    procesos = []
    
    # Crear procesos para generar descendencia
    for _ in range(n_descendientes):
        proceso = mp.Process(target=generar_individuo, args=(lista_compartida,))
        procesos.append(proceso)
    
    # Iniciar medición de tiempo
    tiempo_inicio = perf_counter()
    
    # Iniciar todos los procesos
    for proceso in procesos:
        proceso.start()
    
    # Esperar a que todos los procesos terminen
    for proceso in procesos:
        proceso.join()
    
    # Finalizar medición de tiempo
    tiempo_fin = perf_counter()
    tiempo_ejecucion = tiempo_fin - tiempo_inicio
    
    print(f"Tiempo de generación de {n_descendientes} descendientes: {tiempo_ejecucion:.4f}s")
    
    # Convertir a lista normal
    return list(lista_compartida)

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

def aplicar_perturbacion_swap_exactas(lista_compartida, tour_base, matriz, n_perturbaciones, origen_heuristica=None, población_existente=None):
    """
    Aplica exactamente n_perturbaciones mediante intercambio de ciudades (swap),
    asegurándose de que todas sean diferentes entre sí y diferentes de la población existente.
    
    Args:
        lista_compartida: Lista compartida para almacenar resultados
        tour_base: Tour base para realizar perturbaciones
        matriz: Matriz de distancias
        n_perturbaciones: Número exacto de perturbaciones a realizar
        origen_heuristica: Nombre de la heurística de origen del tour base
        población_existente: Lista de tours existentes para evitar duplicados
    """
    if población_existente is None:
        población_existente = []
    
    n = len(tour_base)
    perturbaciones_generadas = []
    intentos = 0
    max_intentos = n_perturbaciones * 10  # Limitar intentos para evitar bucles infinitos
    
    while len(perturbaciones_generadas) < n_perturbaciones and intentos < max_intentos:
        # Perturbación mediante intercambio de dos ciudades
        nuevo_tour = tour_base.copy()
        num_swaps = random.randint(1, min(5, n//10 + 1))
        
        for _ in range(num_swaps):
            i, j = random.sample(range(n), 2)
            nuevo_tour[i], nuevo_tour[j] = nuevo_tour[j], nuevo_tour[i]
        
        # Calcular FO
        fo = calcular_fo(nuevo_tour, matriz)
        
        # Verificar si es único
        es_unico = True
        for tour_existente in perturbaciones_generadas + población_existente:
            if isinstance(tour_existente, dict):
                tour_comp = tour_existente.get('tour', [])
            else:
                tour_comp = tour_existente
                
            if np.array_equal(np.array(nuevo_tour), np.array(tour_comp)):
                es_unico = False
                break
        
        if es_unico:
            resultado = {
                'tour': nuevo_tour,
                'fo': fo,
                'tipo': 'swap',
                'origen': origen_heuristica
            }
            perturbaciones_generadas.append(resultado)
            lista_compartida.append(resultado)
        
        intentos += 1
    
    if len(perturbaciones_generadas) < n_perturbaciones:
        print(f"Advertencia: No se pudieron generar {n_perturbaciones} perturbaciones únicas para {origen_heuristica}. Se generaron {len(perturbaciones_generadas)}")

def generar_perturbaciones_swap_exactas(tours_semilla, matriz, total_requerido, nombres_heuristicas=None):
    """
    Genera exactamente el número de perturbaciones requeridas usando el operador swap,
    distribuidas uniformemente entre los tours semilla.
    
    Args:
        tours_semilla: Lista de tours base para generar perturbaciones
        matriz: Matriz de distancias
        total_requerido: Número total de perturbaciones a generar
        nombres_heuristicas: Lista con los nombres de las heurísticas correspondientes a cada tour
        
    Returns:
        Lista de perturbaciones generadas
    """
    # Si no se proporcionan nombres, usar valores por defecto
    if nombres_heuristicas is None:
        nombres_heuristicas = [f"Heurística {i+1}" for i in range(len(tours_semilla))]
    
    # Instanciar el administrador de procesos
    manager = mp.Manager()
    # Creamos la memoria compartida
    lista_compartida = manager.list()
    
    # Calcular cuántas perturbaciones por tour semilla
    # Distribuir uniformemente
    n_tours = len(tours_semilla)
    perturbaciones_por_tour = [total_requerido // n_tours] * n_tours
    
    # Distribuir las perturbaciones restantes (si hay)
    extras = total_requerido % n_tours
    for i in range(extras):
        perturbaciones_por_tour[i] += 1
    
    # Lista para almacenar todos los procesos
    todos_procesos = []
    
    # Crear procesos para cada tour semilla
    for i, tour_base in enumerate(tours_semilla):
        proceso = mp.Process(
            target=aplicar_perturbacion_swap_exactas,
            args=(lista_compartida, tour_base, matriz, perturbaciones_por_tour[i], nombres_heuristicas[i]),
            kwargs={'población_existente': []}
        )
        todos_procesos.append(proceso)
    
    # Iniciar medición de tiempo
    tiempo_inicio = perf_counter()
    
    # Iniciar todos los procesos
    for proceso in todos_procesos:
        proceso.start()
    
    # Esperar a que todos los procesos terminen
    for proceso in todos_procesos:
        proceso.join()
    
    # Finalizar medición de tiempo
    tiempo_fin = perf_counter()
    tiempo_ejecucion = tiempo_fin - tiempo_inicio
    
    print(f"Tiempo total de generación de perturbaciones swap: {tiempo_ejecucion:.4f}s")
    print(f"Total de perturbaciones swap generadas: {len(lista_compartida)}")
    
    # Convertir a lista normal
    perturbaciones = list(lista_compartida)
    
    return perturbaciones

if __name__ == "__main__":
    print("Este módulo contiene implementaciones de algoritmos genéticos para el TSP.")
    print("Por favor, ejecute main.py para usar la interfaz de usuario.")
    



