
from leerInformacion import cargarCaso
from matrizDistancias import matrizEuclidiana, distanciaTour
from codificacionVecindarios import *
from heuristicas import *
from esqueletoConcurrencia import *
import os
import sys
import random
import numpy as np
import time
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
    print("\n1. GENERACIÓN DE INDIVIDUOS")
    print("-"*40)
    
    print("Generando 5 individuos por las heuristicas trabajadas...")
    inicio_total_heuristicas = time.time()
    
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

    # Corregir el tour de Savings si tiene longitud incorrecta
    if len(resultado_savings['tour']) != caso['dimension']:
        print(f"Corrigiendo tour de Savings: longitud original {len(resultado_savings['tour'])}, debería ser {caso['dimension']}")
        # Si el tour es más largo que la dimensión, truncarlo
        if len(resultado_savings['tour']) > caso['dimension']:
            # Encontrar y eliminar elementos duplicados
            tour_savings = []
            visitados = set()
            for ciudad in resultado_savings['tour']:
                if ciudad not in visitados:
                    tour_savings.append(ciudad)
                    visitados.add(ciudad)
                    if len(tour_savings) == caso['dimension']:
                        break
            resultado_savings['tour'] = tour_savings
        # Si el tour es más corto que la dimensión, completarlo
        elif len(resultado_savings['tour']) < caso['dimension']:
            # Encontrar nodos faltantes
            nodos_existentes = set(resultado_savings['tour'])
            nodos_faltantes = [i for i in range(1, caso['dimension'] + 1) if i not in nodos_existentes]
            # Añadir nodos faltantes al final del tour
            resultado_savings['tour'].extend(nodos_faltantes)

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
        
        # Corregir el tour de Christofides si tiene longitud incorrecta
        if len(resultado_christofides['tour']) != caso['dimension']:
            print(f"Corrigiendo tour de Christofides: longitud original {len(resultado_christofides['tour'])}, debería ser {caso['dimension']}")
            # Si el tour es más largo que la dimensión, truncarlo
            if len(resultado_christofides['tour']) > caso['dimension']:
                # Encontrar y eliminar elementos duplicados
                tour_christofides = []
                visitados = set()
                for ciudad in resultado_christofides['tour']:
                    if ciudad not in visitados:
                        tour_christofides.append(ciudad)
                        visitados.add(ciudad)
                        if len(tour_christofides) == caso['dimension']:
                            break
                resultado_christofides['tour'] = tour_christofides
            # Si el tour es más corto que la dimensión, completarlo
            elif len(resultado_christofides['tour']) < caso['dimension']:
                # Encontrar nodos faltantes
                nodos_existentes = set(resultado_christofides['tour'])
                nodos_faltantes = [i for i in range(1, caso['dimension'] + 1) if i not in nodos_existentes]
                # Añadir nodos faltantes al final del tour
                resultado_christofides['tour'].extend(nodos_faltantes)
        
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
    
    tiempo_total_heuristicas = time.time() - inicio_total_heuristicas
    print(f"Tiempo total de generación de las heuristicas: {tiempo_total_heuristicas:.4f}s")
    
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
            print(f"Generando {perturbaciones_requeridas} perturbaciones swap...")
            
            inicio_perturbaciones = time.time()
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
            print(f"Generando {aleatorios_faltantes} individuos aleatorios...")
            
            inicio_aleatorios = time.time()
            individuos_aleatorios = generar_individuos_aleatorios(caso, matriz, aleatorios_faltantes, población_inicial)
            tiempo_aleatorios = time.time() - inicio_aleatorios
            
            # Añadir a la población
            for individuo in individuos_aleatorios:
                nuevo_individuo = {
                    'tour': individuo['tour'],
                    'fo': individuo['fo'],
                    'tipo': 'Aleatorio'
                }
                población_inicial.append(nuevo_individuo)
            
            print(f"Tiempo total de generación de los aleatorios: {tiempo_aleatorios:.4f}s")
    
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
    
    # Tamaño de la generación (cuántos descendientes generar a la vez)
    tamaño_generacion = max(10, tam_población // 2)
    
    inicio = time.time()
    
    for gen in range(1, max_generaciones + 1):
        # Generar descendencia
        print(f"\nGeneración {gen}")
        descendientes = generar_descendencia(población, matriz, tamaño_generacion, prob_mutación)
        
        # Ordenar descendientes por calidad (menor FO es mejor)
        descendientes.sort(key=lambda ind: ind['fo'])
        
        # Verificar si hay mejora global
        hay_mejora = False
        
        # Intentar incorporar los mejores descendientes en la población
        for hijo in descendientes:
            # Reemplazo en la población siguiendo el esquema de Chu-Beasley
            reemplazado = reemplazo_chu_beasley(población, hijo, matriz)
            
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

def generar_descendencia(poblacion, matriz, n_descendientes, prob_mutacion=0.2):
    """
    Genera descendencia mediante torneos, cruces y mutaciones sin usar concurrencia.
    
    Args:
        poblacion: Población actual
        matriz: Matriz de distancias
        n_descendientes: Número de descendientes a generar
        prob_mutacion: Probabilidad de mutación
        
    Returns:
        Lista de descendientes generados
    """
    # Lista para almacenar los descendientes
    descendientes = []
    
    # Iniciar medición de tiempo
    tiempo_inicio = time.time()
    
    # Generar n_descendientes descendientes
    for descendiente_idx in range(n_descendientes):
        # Si es el primer descendiente, mostrar información detallada
        if descendiente_idx == 0:
            print("\n2. SELECCIÓN")
            print("-"*40)
            
            # Selección del padre (torneo binario)
            candidatos_padre = random.sample(poblacion, 2)
            candidatos_padre.sort(key=lambda ind: ind['fo'])
            padre = candidatos_padre[0]  # El mejor candidato (menor FO)
            
            # Mostrar información de los candidatos a padre
            print("Torneo Padre")
            print(f"Candidato 1: Individuo {poblacion.index(candidatos_padre[0])+1}, FO={candidatos_padre[0]['fo']}")
            print(f"Candidato 2: Individuo {poblacion.index(candidatos_padre[1])+1}, FO={candidatos_padre[1]['fo']}")
            print(f"Seleccionado como PADRE: Individuo {poblacion.index(padre)+1}, FO={padre['fo']}")
            
            # Selección de la madre (torneo binario)
            candidatos_madre = random.sample(poblacion, 2)
            candidatos_madre.sort(key=lambda ind: ind['fo'])
            madre = candidatos_madre[0]  # El mejor candidato (menor FO)
            
            # Mostrar información de los candidatos a madre
            print("\nTorneo Madre")
            print(f"Candidato 1: Individuo {poblacion.index(candidatos_madre[0])+1}, FO={candidatos_madre[0]['fo']}")
            print(f"Candidato 2: Individuo {poblacion.index(candidatos_madre[1])+1}, FO={candidatos_madre[1]['fo']}")
            print(f"Seleccionado como MADRE: Individuo {poblacion.index(madre)+1}, FO={madre['fo']}")
            
            print("\n3. RECOMBINACIÓN")
            print("-"*40)
            
            # Generar los 5 descendientes con diferentes operadores de cruce
            # Stefan Jacobs (SJX)
            hijo_sjx = cruce_sjx(padre['tour'], madre['tour'])
            fo_sjx = calcular_fo(hijo_sjx, matriz)
            print(f"SJX: FO={fo_sjx}")
            
            # Partially Matched Crossover (PMX)
            hijo_pmx = cruce_pmx(padre['tour'], madre['tour'])
            fo_pmx = calcular_fo(hijo_pmx, matriz)
            print(f"PMX: FO={fo_pmx}")
            
            # Order Crossover (OX)
            hijo_ox = cruce_ox(padre['tour'], madre['tour'])
            fo_ox = calcular_fo(hijo_ox, matriz)
            print(f"OX: FO={fo_ox}")
            
            # Order Based Crossover (OBX)
            hijo_obx = cruce_obx(padre['tour'], madre['tour'])
            fo_obx = calcular_fo(hijo_obx, matriz)
            print(f"OBX: FO={fo_obx}")
            
            # Cycle Crossover (CX)
            hijo_cx = cruce_cx(padre['tour'], madre['tour'])
            fo_cx = calcular_fo(hijo_cx, matriz)
            print(f"CX: FO={fo_cx}")
            
            # Ranking de descendientes por FO
            descendientes_ranking = [
                {'tipo': 'SJX', 'tour': hijo_sjx, 'fo': fo_sjx},
                {'tipo': 'PMX', 'tour': hijo_pmx, 'fo': fo_pmx},
                {'tipo': 'OX', 'tour': hijo_ox, 'fo': fo_ox},
                {'tipo': 'OBX', 'tour': hijo_obx, 'fo': fo_obx},
                {'tipo': 'CX', 'tour': hijo_cx, 'fo': fo_cx}
            ]
            
            # Ordenar por FO (menor es mejor)
            descendientes_ranking.sort(key=lambda d: d['fo'])
            
            # Seleccionar el mejor descendiente
            mejor_descendiente = descendientes_ranking[0]
            print(f"\nMejor operador de recombinación: {mejor_descendiente['tipo']} con FO={mejor_descendiente['fo']}")
            
            # Aplicar mutación (opcional, según probabilidad)
            if random.random() < prob_mutacion:
                print("\n4. MUTACIÓN")
                print("-"*40)
                
                # Aplicar ambos operadores de mutación
                tour_shift = mutacion_shift(mejor_descendiente['tour'])
                fo_shift = calcular_fo(tour_shift, matriz)
                print(f"Shift(1,0): FO={fo_shift}")
                
                tour_2opt = mutacion_2opt(mejor_descendiente['tour'])
                fo_2opt = calcular_fo(tour_2opt, matriz)
                print(f"2-opt: FO={fo_2opt}")
                
                # Elegir el mejor operador de mutación
                if fo_shift <= fo_2opt:
                    mejor_descendiente['tour'] = tour_shift
                    mejor_descendiente['fo'] = fo_shift
                    print(f"Mejor operador de mutación: Shift(1,0) con FO={fo_shift}")
                else:
                    mejor_descendiente['tour'] = tour_2opt
                    mejor_descendiente['fo'] = fo_2opt
                    print(f"Mejor operador de mutación: 2-opt con FO={fo_2opt}")
            
            # Añadir a la lista de descendientes
            descendientes.append(mejor_descendiente)
        else:
            # Para el resto de descendientes, procedimiento sin detalles
            # Selección de padres por torneo binario
            padre = seleccion_torneo(poblacion)
            madre = seleccion_torneo(poblacion)
            
            # Generar los 5 descendientes con diferentes operadores de cruce
            hijos = [
                {'tipo': 'SJX', 'tour': cruce_sjx(padre['tour'], madre['tour'])},
                {'tipo': 'PMX', 'tour': cruce_pmx(padre['tour'], madre['tour'])},
                {'tipo': 'OX', 'tour': cruce_ox(padre['tour'], madre['tour'])},
                {'tipo': 'OBX', 'tour': cruce_obx(padre['tour'], madre['tour'])},
                {'tipo': 'CX', 'tour': cruce_cx(padre['tour'], madre['tour'])}
            ]
            
            # Calcular FO para cada hijo
            for hijo in hijos:
                hijo['fo'] = calcular_fo(hijo['tour'], matriz)
            
            # Ordenar por FO (menor es mejor)
            hijos.sort(key=lambda h: h['fo'])
            
            # Seleccionar el mejor descendiente
            mejor_descendiente = hijos[0]
            
            # Aplicar mutación (opcional, según probabilidad)
            if random.random() < prob_mutacion:
                # Aplicar ambos operadores de mutación
                tour_shift = mutacion_shift(mejor_descendiente['tour'])
                fo_shift = calcular_fo(tour_shift, matriz)
                
                tour_2opt = mutacion_2opt(mejor_descendiente['tour'])
                fo_2opt = calcular_fo(tour_2opt, matriz)
                
                # Elegir el mejor operador de mutación
                if fo_shift <= fo_2opt:
                    mejor_descendiente['tour'] = tour_shift
                    mejor_descendiente['fo'] = fo_shift
                else:
                    mejor_descendiente['tour'] = tour_2opt
                    mejor_descendiente['fo'] = fo_2opt
            
            # Añadir a la lista de descendientes
            descendientes.append(mejor_descendiente)
    
    # Finalizar medición de tiempo
    tiempo_fin = time.time()
    tiempo_ejecucion = tiempo_fin - tiempo_inicio
    
    print(f"Tiempo de generación de {n_descendientes} descendientes: {tiempo_ejecucion:.4f}s")
    
    return descendientes

def seleccion_torneo(poblacion, tam_torneo=2):
    """
    Selección por torneo binario: selecciona al mejor de tam_torneo individuos aleatorios.
    
    Args:
        poblacion: Lista de individuos que forman la población
        tam_torneo: Tamaño del torneo (número de competidores)
        
    Returns:
        El mejor individuo seleccionado
    """
    competidores = random.sample(poblacion, tam_torneo)
    return min(competidores, key=lambda ind: ind['fo'])

def cruce_ox(padre1, padre2):
    """
    Cruce OX (Order Crossover) para permutaciones
    
    Args:
        padre1: Lista con el tour del primer padre
        padre2: Lista con el tour del segundo padre
        
    Returns:
        Lista con el tour generado por el cruce OX
    """
    # Verificar que los padres tengan la misma longitud
    if len(padre1) != len(padre2):
        print(f"Error en OX: Los padres tienen longitudes diferentes: {len(padre1)} y {len(padre2)}")
        # Devolver copia del padre1 como medida de emergencia
        return padre1.copy()
    
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
    elementos_usados = set(hijo[punto1:punto2+1])
    elementos_restantes = [e for e in padre2 if e not in elementos_usados]
    
    if not elementos_restantes:
        print("Advertencia: OX no pudo generar un tour válido. Usando padre1 como respaldo.")
        return padre1.copy()
    
    for elemento in elementos_restantes:
        hijo[j] = elemento
        j = (j + 1) % n
        if j == punto1:
            break
    
    # Verificar validez del tour (debe contener todos los nodos una sola vez)
    if -1 in hijo or len(set(hijo)) != n:
        print("Advertencia: OX generó un tour inválido. Usando padre1 como respaldo.")
        return padre1.copy()
    
    return hijo

def cruce_sjx(padre1, padre2):
    """
    Cruce SJX (Stefan Jacobs) para permutaciones:
    - Se generan dos números enteros p y q
    - Se toman q genes a partir de la posición p de la solución padre
    - El resto de los genes son tomados de la madre
    
    Args:
        padre1: Lista con el tour del primer padre
        padre2: Lista con el tour del segundo padre
        
    Returns:
        Lista con el tour generado por el cruce SJX
    """
    # Verificar que los padres tengan la misma longitud
    if len(padre1) != len(padre2):
        print(f"Error en SJX: Los padres tienen longitudes diferentes: {len(padre1)} y {len(padre2)}")
        # Devolver copia del padre1 como medida de emergencia
        return padre1.copy()
    
    n = len(padre1)
    # Generar posición p y cantidad de genes q
    p = random.randint(0, n-1)
    # Aseguramos que q no exceda la longitud restante
    q = random.randint(1, min(n-p, n//2))
    
    # Inicializar hijo con -1 (valor no válido)
    hijo = [-1] * n
    
    # Copiar q genes desde la posición p del padre
    for i in range(p, min(p+q, n)):
        hijo[i] = padre1[i]
    
    # Crear lista de elementos que faltan por incluir (los que no están en el hijo)
    elementos_faltantes = []
    for elemento in padre2:
        if elemento not in hijo:
            elementos_faltantes.append(elemento)
    
    # Completar con genes de la madre en las posiciones vacías
    idx_faltante = 0
    for j in range(n):
        if hijo[j] == -1:  # Si la posición está vacía
            if idx_faltante < len(elementos_faltantes):
                hijo[j] = elementos_faltantes[idx_faltante]
                idx_faltante += 1
    
    # Verificar validez del tour (debe contener todos los nodos una sola vez)
    if -1 in hijo or len(set(hijo)) != n:
        print("Advertencia: SJX generó un tour inválido. Usando padre1 como respaldo.")
        return padre1.copy()
    
    return hijo

def cruce_pmx(padre1, padre2):
    """
    Cruce PMX (Partially Matched Crossover) para permutaciones:
    - Se generan dos puntos de corte sobre el padre
    - Se extraen los genes dentro de ese rango
    - Se copian en la descendencia respetando la posición
    - Se llenan los demás genes con la información de la madre
    - Si hay repeticiones, se reemplazan usando mapeo
    """
    # Verificar que los padres tengan la misma longitud
    if len(padre1) != len(padre2):
        return padre1.copy()
    
    n = len(padre1)
    # Generar puntos de corte
    punto1 = random.randint(0, n-2)
    punto2 = random.randint(punto1+1, n-1)
    
    # Inicializar hijo
    hijo = [-1] * n
    
    # Paso 1: Copiar el segmento del padre1
    for i in range(punto1, punto2+1):
        hijo[i] = padre1[i]
    
    # Paso 2: Crear mapeo de valores
    mapeo = {}
    for i in range(punto1, punto2+1):
        if padre1[i] != padre2[i]:
            mapeo[padre2[i]] = padre1[i]
    
    # Paso 3: Llenar las posiciones restantes
    for i in range(n):
        if i < punto1 or i > punto2:  # Solo procesar posiciones fuera del segmento
            valor = padre2[i]
            
            # Seguir el mapeo hasta encontrar un valor que no esté en el segmento
            while valor in mapeo:
                valor = mapeo[valor]
            
            hijo[i] = valor
    
    # Verificación final
    if len(set(hijo)) == n and -1 not in hijo:
        return hijo
    
    # Si algo salió mal, intentar reparar el tour
    valores_faltantes = set(range(1, n+1)) - set(hijo)
    valores_duplicados = [x for x in hijo if hijo.count(x) > 1]
    
    if valores_duplicados and valores_faltantes:
        for i, valor in enumerate(hijo):
            if valor in valores_duplicados and valor != padre1[i]:
                valor_faltante = valores_faltantes.pop()
                hijo[i] = valor_faltante
                if not valores_faltantes:
                    break
    
    # Verificación final después de la reparación
    if len(set(hijo)) == n and -1 not in hijo:
        return hijo
        
    # Si aún no es válido, devolver una copia del padre1
    return padre1.copy()

def cruce_obx(padre1, padre2):
    """
    Cruce OBX (Order Based Crossover) para permutaciones:
    - Se genera un punto de corte sobre el padre
    - Se extraen los genes a la izquierda del punto de corte del padre
    - Se usan todos los genes de la madre que no fueron empleados
    
    Args:
        padre1: Lista con el tour del primer padre
        padre2: Lista con el tour del segundo padre
        
    Returns:
        Lista con el tour generado por el cruce OBX
    """
    # Verificar que los padres tengan la misma longitud
    if len(padre1) != len(padre2):
        print(f"Error en OBX: Los padres tienen longitudes diferentes: {len(padre1)} y {len(padre2)}")
        # Devolver copia del padre1 como medida de emergencia
        return padre1.copy()
    
    n = len(padre1)
    # Generar punto de corte
    punto = random.randint(1, n-1)  # Al menos un elemento del padre, al menos uno de la madre
    
    # Inicializar hijo
    hijo = [-1] * n
    
    # Copiar genes a la izquierda del punto de corte desde el padre
    for i in range(punto):
        hijo[i] = padre1[i]
    
    # Completar con genes de la madre que no estén ya en el hijo
    j = punto
    elementos_usados = set(hijo[:punto])
    elementos_faltantes = [e for e in padre2 if e not in elementos_usados]
    
    for elemento in elementos_faltantes:
        if j < n:
            hijo[j] = elemento
            j += 1
    
    # Verificar validez del tour (debe contener todos los nodos una sola vez)
    if -1 in hijo or len(set(hijo)) != n:
        print("Advertencia: OBX generó un tour inválido. Usando padre1 como respaldo.")
        return padre1.copy()
    
    return hijo

def cruce_cx(padre1, padre2):
    """
    Cruce CX (Cycle Crossover) para permutaciones:
    - Identifica ciclos entre el padre y la madre
    - Alterna ciclos entre padre y madre para formar el hijo
    
    Args:
        padre1: Lista con el tour del primer padre
        padre2: Lista con el tour del segundo padre
        
    Returns:
        Lista con el tour generado por el cruce CX
    """
    # Verificar que los padres tengan la misma longitud
    if len(padre1) != len(padre2):
        print(f"Error en CX: Los padres tienen longitudes diferentes: {len(padre1)} y {len(padre2)}")
        # Devolver copia del padre1 como medida de emergencia
        return padre1.copy()
    
    n = len(padre1)
    hijo = [-1] * n
    visitados = [False] * n
    
    try:
        # Comenzar con el primer elemento
        ciclo_par = True  # Alternamos ciclos pares e impares
        
        for i in range(n):
            if not visitados[i]:
                # Nuevo ciclo
                j = i
                while not visitados[j] and j < n:
                    visitados[j] = True
                    # Si es ciclo par, tomamos del padre, si es impar, de la madre
                    if ciclo_par:
                        hijo[j] = padre1[j]
                    else:
                        hijo[j] = padre2[j]
                    
                    # Buscar el índice del valor del padre2 en padre1
                    try:
                        valor = padre2[j]
                        if valor in padre1:
                            j = padre1.index(valor)
                        else:
                            # Si el valor no está en padre1, salir del ciclo
                            break
                    except (ValueError, IndexError):
                        # Si hay un error al buscar el índice, salir del ciclo
                        break
                
                # Cambiamos de ciclo
                ciclo_par = not ciclo_par
    except Exception as e:
        print(f"Error en CX: {e}")
        return padre1.copy()
    
    # Si quedan posiciones sin asignar, llenarlas con valores del padre1
    for i in range(n):
        if hijo[i] == -1:
            # Buscar un valor del padre1 que no esté ya en el hijo
            for valor in padre1:
                if valor not in hijo:
                    hijo[i] = valor
                    break
    
    # Verificar validez del tour (debe contener todos los nodos una sola vez)
    if -1 in hijo or len(set(hijo)) != n:
        print("Advertencia: CX generó un tour inválido. Usando padre1 como respaldo.")
        return padre1.copy()
    
    return hijo

def mutacion_shift(tour):
    """
    Mutación Shift(1,0) - Reubicación de servicios entre itinerarios.
    Mueve un servicio (nodo) a una nueva posición en el tour.
    
    Args:
        tour: Tour a mutar
        
    Returns:
        Nuevo tour después de la mutación
    """
    n = len(tour)
    # Seleccionar posición origen y destino aleatorias
    origen = random.randint(0, n-1)
    destino = random.randint(0, n-1)
    
    # Si origen y destino son iguales, no hay cambio
    if origen == destino:
        return tour.copy()
    
    nuevo_tour = tour.copy()
    valor = nuevo_tour.pop(origen)
    
    # Insertar el valor en la posición destino
    if origen < destino:
        nuevo_tour.insert(destino-1, valor)
    else:
        nuevo_tour.insert(destino, valor)
    
    return nuevo_tour

def mutacion_2opt(tour):
    """
    Mutación usando el operador 2-opt
    Intercambia dos conexiones en una porción del orden de atención.
    
    Args:
        tour: Tour a mutar
        
    Returns:
        Nuevo tour después de la mutación
    """
    n = len(tour)
    # Seleccionar puntos de corte aleatorios (al menos 2 posiciones de distancia)
    i = random.randint(0, n-3)
    j = random.randint(i+2, n-1)
    
    # Crear nuevo tour invirtiendo el segmento entre i y j
    nuevo_tour = tour.copy()
    nuevo_tour[i+1:j+1] = reversed(tour[i+1:j+1])
    
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

def reemplazo_chu_beasley(poblacion, hijo, matriz):
    """
    Reemplazo siguiendo el esquema de Chu-Beasley con intensificación:
    1. El hijo solo reemplaza a un individuo si es mejor
    2. Se reemplaza al peor individuo que sea diferente al hijo
    3. Se intensifica la solución mediante rotaciones antes de la inserción
    
    Args:
        poblacion: Lista de individuos que forman la población
        hijo: Nuevo individuo a insertar en la población
        matriz: Matriz de distancias para calcular FO
        
    Returns:
        bool: True si se realizó un reemplazo, False en caso contrario
    """
    # Ordenar población por FO (menor es mejor)
    poblacion.sort(key=lambda ind: ind['fo'])
    
    # Verificar que el hijo sea mejor que al menos el peor individuo
    if hijo['fo'] < poblacion[-1]['fo']:
        # Intensificación: explorar rotaciones del tour para mejorar la solución
        mejor_tour = intensificar_rotaciones(hijo['tour'], hijo['fo'], matriz)
        hijo['tour'] = mejor_tour['tour']
        hijo['fo'] = mejor_tour['fo']
        
        # Actualización
        print("\n5. ACTUALIZACIÓN")
        print("-"*40)
        print(f"Función objetivo del descendiente mejorado: {hijo['fo']}")
        print(f"Peor individuo en la población: {poblacion[-1]['fo']}")
        
        # Reemplazar al peor individuo de la población
        poblacion[-1] = hijo
        
        # Reordenar la población
        poblacion.sort(key=lambda ind: ind['fo'])
        print(f"Actualización exitosa. Nueva peor FO: {poblacion[-1]['fo']}")
        
        return True
    else:
        print("\n5. ACTUALIZACIÓN")
        print("-"*40)
        print(f"No hay mejora. FO del descendiente: {hijo['fo']}")
        print(f"Peor individuo en la población: {poblacion[-1]['fo']}")
        print("No se realiza actualización.")
        
        return False

def intensificar_rotaciones(tour, fo_original, matriz=None):
    """
    Intensificación mediante rotaciones de la secuencia.
    Explora todas las rotaciones posibles del tour para encontrar la mejor.
    
    Args:
        tour: Tour a rotar
        fo_original: Función objetivo del tour original
        matriz: Matriz de distancias (si no se proporciona, se mantiene la FO original)
        
    Returns:
        Diccionario con el mejor tour encontrado y su FO
    """
    n = len(tour)
    mejor_tour = tour
    mejor_fo = fo_original
    
    # Si no se proporciona matriz, devolver el tour original (no podemos calcular la FO)
    if matriz is None:
        return {'tour': mejor_tour, 'fo': mejor_fo}
    
    # Explorar todas las rotaciones posibles
    for i in range(1, n):
        # Rotar el tour (i posiciones)
        tour_rotado = tour[i:] + tour[:i]
        fo_rotado = calcular_fo(tour_rotado, matriz)
        
        # Actualizar si encontramos una mejor solución
        if fo_rotado < mejor_fo:
            mejor_tour = tour_rotado
            mejor_fo = fo_rotado
    
    return {'tour': mejor_tour, 'fo': mejor_fo}

def generar_perturbaciones_swap_exactas(tours_semilla, matriz, total_requerido, nombres_heuristicas=None):
    """
    Genera exactamente el número de perturbaciones requeridas usando el operador swap,
    distribuidas uniformemente entre los tours semilla, sin usar concurrencia.
    
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
    
    # Lista para almacenar todas las perturbaciones
    perturbaciones = []
    
    # Calcular cuántas perturbaciones por tour semilla
    # Distribuir uniformemente
    n_tours = len(tours_semilla)
    perturbaciones_por_tour = [total_requerido // n_tours] * n_tours
    
    # Distribuir las perturbaciones restantes (si hay)
    extras = total_requerido % n_tours
    for i in range(extras):
        perturbaciones_por_tour[i] += 1
    
    # Iniciar medición de tiempo
    tiempo_inicio = time.time()
    
    # Generar perturbaciones para cada tour semilla
    for i, tour_base in enumerate(tours_semilla):
        n_perturbaciones = perturbaciones_por_tour[i]
        origen_heuristica = nombres_heuristicas[i]
        
        # Función integrada para generar perturbaciones para este tour
        n = len(tour_base)
        intentos = 0
        max_intentos = n_perturbaciones * 10  # Limitar intentos para evitar bucles infinitos
        
        # Tours existentes para verificar unicidad
        tours_existentes = [p['tour'] for p in perturbaciones] if perturbaciones else []
        
        # Perturbaciones generadas para este tour
        perturbaciones_tour = []
        
        while len(perturbaciones_tour) < n_perturbaciones and intentos < max_intentos:
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
            for tour_existente in tours_existentes + [p['tour'] for p in perturbaciones_tour]:
                if np.array_equal(np.array(nuevo_tour), np.array(tour_existente)):
                    es_unico = False
                    break
            
            if es_unico:
                resultado = {
                    'tour': nuevo_tour,
                    'fo': fo,
                    'tipo': 'swap',
                    'origen': origen_heuristica
                }
                perturbaciones_tour.append(resultado)
            
            intentos += 1
        
        if len(perturbaciones_tour) < n_perturbaciones:
            print(f"Advertencia: No se pudieron generar {n_perturbaciones} perturbaciones únicas para {origen_heuristica}. Se generaron {len(perturbaciones_tour)}")
        
        # Añadir las perturbaciones de este tour a la lista general
        perturbaciones.extend(perturbaciones_tour)
    
    # Finalizar medición de tiempo
    tiempo_fin = time.time()
    tiempo_ejecucion = tiempo_fin - tiempo_inicio
    
    print(f"Tiempo total de generación de perturbaciones swap: {tiempo_ejecucion:.4f}s")
    
    return perturbaciones

if __name__ == "__main__":
    print("Este módulo contiene implementaciones de algoritmos genéticos para el TSP.")
    print("Por favor, ejecute main.py para usar la interfaz de usuario.")
    



