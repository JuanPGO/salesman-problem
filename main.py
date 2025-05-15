"""
Script principal para ejecutar y comparar todos los algoritmos del TSP implementados.
"""

import time
import os
import matplotlib.pyplot as plt
from typing import List, Dict
import numpy as np
import multiprocessing as mp
from time import perf_counter

# Importar todos los módulos necesarios
from leerInformacion import cargarCaso
from matrizDistancias import matrizEuclidiana, distanciaTour
from heuristicas import heuristicaVecinoMasCercano, heuristicaInsercionMasCercana
from heuristicas import heuristicaInsercionMasLejana, heuristicaSavings, heuristicaChristofides
from codificacionVecindarios import two_opt
from busquedaLocal import busqueda_local_mejor_mejora, busqueda_local_primera_mejora, ejecutar_busqueda_local
from perturbacion import perturbacion_3opt, perturbacion_parcial
from ils import ils_algorithm, ejecutar_ils_completo
from esqueletoConcurrencia import vecinos_concurrentes
import random

def ejecutar_comparativa_completa(archivo_instancia: str) -> Dict:
    """
    Ejecuta todos los algoritmos implementados y compara sus resultados.
    
    Args:
        archivo_instancia: Ruta al archivo de la instancia TSP
        
    Returns:
        Diccionario con todos los resultados y comparativas
    """
    # Cargar datos y preprocesar
    caso = cargarCaso(archivo_instancia)
    matriz = matrizEuclidiana(caso)
    
    # Obtener el nombre de la instancia del nombre de archivo
    nombre_instancia = os.path.basename(archivo_instancia).split('.')[0]
    
    print("="*60)
    print(f"COMPARATIVA COMPLETA PARA: {nombre_instancia}")
    print(f"Dimensión: {caso['dimension']} ciudades")
    print("="*60)
    
    # Almacenar resultados
    resultados = {}
    
    # 1. Ejecutar heurísticas constructivas
    print("\n1. HEURÍSTICAS CONSTRUCTIVAS")
    print("-"*40)
    
    # Vecino más cercano
    inicio = time.time()
    resultado_vcn = heuristicaVecinoMasCercano(caso, matriz)
    tiempo_vcn = time.time() - inicio
    distancia_vcn = distanciaTour(resultado_vcn, matriz)
    
    print(f"Vecino más cercano: {distancia_vcn} (tiempo: {tiempo_vcn:.4f}s)")
    resultados['vecino_mas_cercano'] = {
        'tour': resultado_vcn['tour'],
        'distancia': distancia_vcn,
        'tiempo': tiempo_vcn
    }
    
    # Inserción más cercana
    inicio = time.time()
    resultado_imc = heuristicaInsercionMasCercana(caso, matriz)
    tiempo_imc = time.time() - inicio
    distancia_imc = distanciaTour(resultado_imc, matriz)
    
    print(f"Inserción más cercana: {distancia_imc} (tiempo: {tiempo_imc:.4f}s)")
    resultados['insercion_mas_cercana'] = {
        'tour': resultado_imc['tour'],
        'distancia': distancia_imc,
        'tiempo': tiempo_imc
    }
    
    # 2. Ejecutar búsqueda local con la mejor heurística
    print("\n2. BÚSQUEDA LOCAL")
    print("-"*40)
    
    # Usar la mejor heurística como punto de partida
    mejor_heuristica = resultado_vcn if distancia_vcn < distancia_imc else resultado_imc
    nombre_mejor_heuristica = "Vecino más cercano" if distancia_vcn < distancia_imc else "Inserción más cercana"
    
    print(f"Mejor heurística constructiva: {nombre_mejor_heuristica} ({distanciaTour(mejor_heuristica, matriz)})")
    
    # Configurar vecindarios (solo two_opt como se sugiere)
    vecindarios = [two_opt]
    
    # Búsqueda local con mejor mejora
    inicio = time.time()
    resultado_bl_mejor = busqueda_local_mejor_mejora(mejor_heuristica['tour'], matriz, vecindarios, max_iter=30)
    tiempo_bl_mejor = time.time() - inicio
    
    print(f"Búsqueda local (mejor mejora): {resultado_bl_mejor['distancia']} (tiempo: {tiempo_bl_mejor:.4f}s)")
    resultados['busqueda_local_mejor_mejora'] = {
        'tour': resultado_bl_mejor['tour'],
        'distancia': resultado_bl_mejor['distancia'],
        'tiempo': tiempo_bl_mejor
    }
    
    # Búsqueda local con primera mejora
    inicio = time.time()
    resultado_bl_primera = busqueda_local_primera_mejora(mejor_heuristica['tour'], matriz, vecindarios, max_iter=30)
    tiempo_bl_primera = time.time() - inicio
    
    print(f"Búsqueda local (primera mejora): {resultado_bl_primera['distancia']} (tiempo: {tiempo_bl_primera:.4f}s)")
    resultados['busqueda_local_primera_mejora'] = {
        'tour': resultado_bl_primera['tour'],
        'distancia': resultado_bl_primera['distancia'],
        'tiempo': tiempo_bl_primera
    }
    
    # 3. Ejecutar ILS con la configuración básica
    print("\n3. ITERATED LOCAL SEARCH (ILS)")
    print("-"*40)
    
    # Configuración básica de ILS (se puede ajustar)
    inicio = time.time()
    resultado_ils = ils_algorithm(
        caso,
        matriz,
        heuristicaInsercionMasCercana if distancia_imc < distancia_vcn else heuristicaVecinoMasCercano,
        busqueda_local_mejor_mejora if resultado_bl_mejor['distancia'] < resultado_bl_primera['distancia'] else busqueda_local_primera_mejora,
        perturbacion_3opt,  # Usar 3-opt como perturbación
        vecindarios=vecindarios,
        max_iteraciones=20,
        max_sin_mejora=10,
        tiempo_limite=30  # 30 segundos máximo
    )
    tiempo_ils = time.time() - inicio
    
    print(f"ILS básico: {resultado_ils['distancia']} (tiempo: {tiempo_ils:.4f}s)")
    print(f"  Mejoras encontradas: {resultado_ils['mejoras_encontradas']}")
    print(f"  Iteraciones totales: {resultado_ils['iteraciones_totales']}")
    
    resultados['ils_basico'] = {
        'tour': resultado_ils['tour'],
        'distancia': resultado_ils['distancia'],
        'tiempo': tiempo_ils,
        'mejoras': resultado_ils['mejoras_encontradas'],
        'iteraciones': resultado_ils['iteraciones_totales'],
        'historial': resultado_ils['historial_mejoras']
    }
    
    # OPCIONAL: Ejecutar análisis completo de ILS
    ejecutar_completo = input("\n¿Desea ejecutar el análisis completo de ILS? (puede tardar varios minutos) [s/N]: ")
    if ejecutar_completo.lower() == 's':
        print("\n4. ANÁLISIS COMPLETO DE ILS (todas las configuraciones)")
        print("-"*40)
        
        inicio = time.time()
        mejor_ils = ejecutar_ils_completo(caso, matriz)
        tiempo_completo = time.time() - inicio
        
        print(f"\nMejor configuración ILS: {mejor_ils['distancia']} (tiempo total: {tiempo_completo:.2f}s)")
        print(f"  Configuración: {mejor_ils['configuracion']}")
        
        resultados['ils_mejor_config'] = mejor_ils
    
    # 4. Generar gráficas comparativas
    generar_graficas = input("\n¿Desea generar gráficas comparativas? [s/N]: ")
    if generar_graficas.lower() == 's':
        print("\nGenerando gráficas...")
        generar_graficas_comparativas(resultados, nombre_instancia)
    
    # 5. Imprimir resumen final
    print("\n" + "="*60)
    print("RESUMEN DE RESULTADOS")
    print("="*60)
    
    # Ordenar resultados por calidad (distancia)
    resultados_ordenados = sorted([
        ('Vecino más cercano', resultados['vecino_mas_cercano']['distancia']),
        ('Inserción más cercana', resultados['insercion_mas_cercana']['distancia']),
        ('Búsqueda local (mejor mejora)', resultados['busqueda_local_mejor_mejora']['distancia']),
        ('Búsqueda local (primera mejora)', resultados['busqueda_local_primera_mejora']['distancia']),
        ('ILS básico', resultados['ils_basico']['distancia']),
    ], key=lambda x: x[1])
    
    print("Algoritmos ordenados por calidad (menor distancia):")
    for i, (nombre, distancia) in enumerate(resultados_ordenados):
        print(f"{i+1}. {nombre}: {distancia}")
    
    return resultados

def ejecutar_algoritmo_genetico(archivo_instancia: str) -> Dict:
    """
    Ejecuta el algoritmo genético de Chu-Beasley para resolver el TSP.
    
    Args:
        archivo_instancia: Ruta al archivo de la instancia TSP
        
    Returns:
        Diccionario con los resultados
    """
    # Cargar datos y preprocesar
    caso = cargarCaso(archivo_instancia)
    matriz = matrizEuclidiana(caso)
    
    # Obtener el nombre de la instancia del nombre de archivo
    nombre_instancia = os.path.basename(archivo_instancia).split('.')[0]
    
    print("="*60)
    print(f"ALGORITMO GENÉTICO (CHU-BEASLEY) PARA: {nombre_instancia}")
    print(f"Dimensión: {caso['dimension']} ciudades")
    print("="*60)
    
    # Calcular tamaño deseado de la población (mitad de la dimensión, redondeando hacia arriba)
    tam_poblacion_deseado = round(caso['dimension'] / 2)
    print(f"Tamaño de población deseado: {tam_poblacion_deseado} individuos")
    
    # Almacenar resultados
    resultados = {}
    
    # 1. Generar población inicial con todas las heurísticas
    print("\n1. GENERACIÓN DE POBLACIÓN INICIAL")
    print("-"*40)
    
    # Heurística 1: Vecino más cercano
    inicio = time.time()
    resultado_vcn = heuristicaVecinoMasCercano(caso, matriz)
    tiempo_vcn = time.time() - inicio
    distancia_vcn = distanciaTour(resultado_vcn, matriz)
    
    print(f"1. Vecino más cercano: {distancia_vcn} (tiempo: {tiempo_vcn:.4f}s)")
    print(f"   Tour: {resultado_vcn['tour']}")
    individuo1 = {
        'tour': resultado_vcn['tour'],
        'fo': distancia_vcn
    }
    
    # Heurística 2: Inserción más cercana
    inicio = time.time()
    resultado_imc = heuristicaInsercionMasCercana(caso, matriz)
    tiempo_imc = time.time() - inicio
    distancia_imc = distanciaTour(resultado_imc, matriz)
    
    print(f"2. Inserción más cercana: {distancia_imc} (tiempo: {tiempo_imc:.4f}s)")
    print(f"   Tour: {resultado_imc['tour']}")
    individuo2 = {
        'tour': resultado_imc['tour'],
        'fo': distancia_imc
    }
    
    # Heurística 3: Inserción más lejana
    inicio = time.time()
    resultado_iml = heuristicaInsercionMasLejana(caso, matriz)
    tiempo_iml = time.time() - inicio
    distancia_iml = distanciaTour(resultado_iml, matriz)
    
    print(f"3. Inserción más lejana: {distancia_iml} (tiempo: {tiempo_iml:.4f}s)")
    print(f"   Tour: {resultado_iml['tour']}")
    individuo3 = {
        'tour': resultado_iml['tour'],
        'fo': distancia_iml
    }
    
    # Heurística 4: Savings
    inicio = time.time()
    resultado_savings = heuristicaSavings(caso, matriz)
    tiempo_savings = time.time() - inicio
    distancia_savings = distanciaTour(resultado_savings, matriz)
    
    print(f"4. Savings: {distancia_savings} (tiempo: {tiempo_savings:.4f}s)")
    print(f"   Tour: {resultado_savings['tour']}")
    individuo4 = {
        'tour': resultado_savings['tour'],
        'fo': distancia_savings
    }
    
    # Heurística 5: Christofides
    try:
        inicio = time.time()
        resultado_christofides = heuristicaChristofides(caso, matriz)
        tiempo_christofides = time.time() - inicio
        distancia_christofides = distanciaTour(resultado_christofides, matriz)
        
        print(f"5. Christofides: {distancia_christofides} (tiempo: {tiempo_christofides:.4f}s)")
        print(f"   Tour: {resultado_christofides['tour']}")
        individuo5 = {
            'tour': resultado_christofides['tour'],
            'fo': distancia_christofides
        }
        población_inicial = [individuo1, individuo2, individuo3, individuo4, individuo5]
    except Exception as e:
        print(f"No se pudo ejecutar Christofides: {e}")
        población_inicial = [individuo1, individuo2, individuo3, individuo4]
    
    # Generar individuos adicionales para alcanzar el tamaño deseado de población
    print("\nGenerando individuos adicionales mediante perturbaciones concurrentes...")
    
    # Función para verificar si un tour es único en la población
    def es_tour_unico(tour, poblacion):
        return not any(np.array_equal(np.array(ind['tour']), np.array(tour)) for ind in poblacion)
    
    # Obtener tours semilla de las heurísticas
    tours_semilla = [ind['tour'] for ind in población_inicial]
    
    # Generar perturbaciones de forma concurrente
    # Ajustar el número de perturbaciones según el tamaño deseado
    n_perturbaciones_por_tipo = max(2, (tam_poblacion_deseado - len(población_inicial)) // (5 * len(tours_semilla)) + 1)
    
    print(f"Generando {n_perturbaciones_por_tipo} perturbaciones por tipo para cada tour semilla...")
    perturbaciones = generar_perturbaciones_concurrentes(tours_semilla, matriz, n_perturbaciones_por_tipo)
    
    # Ordenar perturbaciones por calidad (menor FO es mejor)
    perturbaciones.sort(key=lambda x: x['fo'])
    
    # Añadir perturbaciones a la población, evitando duplicados
    for perturbacion in perturbaciones:
        if len(población_inicial) >= tam_poblacion_deseado:
            break
            
        if es_tour_unico(perturbacion['tour'], población_inicial):
            nuevo_individuo = {
                'tour': perturbacion['tour'],
                'fo': perturbacion['fo']
            }
            población_inicial.append(nuevo_individuo)
            
            # Mostrar información
            indice = len(población_inicial)
            print(f"Individuo {indice}: FO={perturbacion['fo']} (perturbación {perturbacion['tipo']})")
            print(f"   Tour: {perturbacion['tour']}")
    
    print(f"\nPoblación inicial generada: {len(población_inicial)} individuos de {tam_poblacion_deseado} deseados")
    if len(población_inicial) < tam_poblacion_deseado:
        print(f"Advertencia: No se pudo generar la población completa, se generaron {len(población_inicial)} individuos")
    
    # 2. Ejecutar algoritmo genético
    print("\n2. EJECUCIÓN DEL ALGORITMO GENÉTICO")
    print("-"*40)
    
    # Parámetros del algoritmo genético
    max_generaciones = 100
    tam_población = len(población_inicial)
    prob_mutación = 0.2
    
    print(f"Parámetros: Generaciones={max_generaciones}, Tamaño población={tam_población}, Prob. mutación={prob_mutación}")
    
    # Ordenar población inicial por función objetivo
    población_inicial.sort(key=lambda ind: ind['fo'])
    mejor_individuo = población_inicial[0]
    
    print(f"Población inicial - Mejor individuo: FO={mejor_individuo['fo']}")
    print(f"Tour del mejor individuo inicial: {mejor_individuo['tour']}")
    
    # Evolución de la población
    población = población_inicial.copy()
    historial_mejoras = [(0, mejor_individuo['fo'])]
    
    inicio_ga = time.time()
    
    # Número de generaciones sin mejora
    gen_sin_mejora = 0
    max_gen_sin_mejora = 20  # Criterio de parada si no hay mejoras
    
    # Tamaño de la generación concurrente (cuántos descendientes generar a la vez)
    tamaño_generacion = max(10, tam_población // 2)
    
    for gen in range(1, max_generaciones + 1):
        # Generar descendencia de forma concurrente
        print(f"\nGeneración {gen}: Generando {tamaño_generacion} descendientes concurrentemente...")
        descendientes = generar_descendencia_concurrente(población, matriz, tamaño_generacion, prob_mutación)
        
        # Ordenar descendientes por calidad (menor FO es mejor)
        descendientes.sort(key=lambda ind: ind['fo'])
        
        # Mejor descendiente de esta generación
        mejor_descendiente = descendientes[0]
        
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
    
    tiempo_ga = time.time() - inicio_ga
    
    print(f"\nResultado final: FO={mejor_individuo['fo']} (tiempo: {tiempo_ga:.4f}s)")
    print(f"Tour final: {mejor_individuo['tour']}")
    print(f"Total de mejoras encontradas: {len(historial_mejoras)}")
    
    resultados['algoritmo_genetico'] = {
        'tour': mejor_individuo['tour'],
        'distancia': mejor_individuo['fo'],
        'tiempo': tiempo_ga,
        'mejoras': len(historial_mejoras) - 1,
        'historial': historial_mejoras
    }
    
    # 3. Generar gráficas
    generar_graficas = input("\n¿Desea generar gráficas del algoritmo genético? [s/N]: ")
    if generar_graficas.lower() == 's':
        print("\nGenerando gráficas...")
        generar_grafica_convergencia_ga(resultados, nombre_instancia)
    
    return resultados

def selección_torneo(población, tam_torneo=2):
    """Selección por torneo binario"""
    competidores = random.sample(población, tam_torneo)
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

def mutación_2opt(tour):
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

def reemplazo_chu_beasley(población, hijo):
    """
    Reemplazo siguiendo el esquema de Chu-Beasley:
    1. El hijo solo reemplaza a un individuo si es mejor
    2. Se reemplaza al peor individuo que sea diferente al hijo
    
    Returns:
        bool: True si se realizó un reemplazo, False en caso contrario
    """
    # Ordenar población por FO (menor es mejor)
    población.sort(key=lambda ind: ind['fo'])
    
    # Verificar que el hijo sea mejor que al menos el peor individuo
    if hijo['fo'] < población[-1]['fo']:
        # Buscar el individuo más parecido al hijo para reemplazarlo
        max_similitud = 0
        indice_reemplazo = -1
        
        for i in range(len(población)-1, -1, -1):
            # Calcular similitud (elementos en común)
            similitud = sum(1 for a, b in zip(población[i]['tour'], hijo['tour']) if a == b)
            
            if similitud > max_similitud:
                max_similitud = similitud
                indice_reemplazo = i
        
        # Reemplazar el individuo elegido
        if indice_reemplazo >= 0:
            población[indice_reemplazo] = hijo
            # Reordenar la población
            población.sort(key=lambda ind: ind['fo'])
            return True
    
    return False

def generar_grafica_convergencia_ga(resultados: Dict, nombre_instancia: str):
    """
    Genera una gráfica de convergencia para el algoritmo genético.
    
    Args:
        resultados: Diccionario con los resultados del algoritmo
        nombre_instancia: Nombre de la instancia para los títulos
    """
    # Crear directorio para gráficas si no existe
    if not os.path.exists('graficas'):
        os.makedirs('graficas')
    
    # Gráfica de convergencia
    plt.figure(figsize=(12, 6))
    
    historial = resultados['algoritmo_genetico']['historial']
    generaciones, fos = zip(*historial)
    
    plt.plot(generaciones, fos, 'o-', color='blue')
    plt.xlabel('Generación')
    plt.ylabel('Función Objetivo (distancia)')
    plt.title(f'Convergencia Algoritmo Genético - {nombre_instancia}')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(f'graficas/{nombre_instancia}_convergencia_ga.png')
    plt.close('all')
    
    print(f"Gráfica guardada en 'graficas/{nombre_instancia}_convergencia_ga.png'")

def generar_graficas_comparativas(resultados: Dict, nombre_instancia: str):
    """
    Genera gráficas comparativas de los algoritmos.
    
    Args:
        resultados: Diccionario con los resultados de todos los algoritmos
        nombre_instancia: Nombre de la instancia para los títulos
    """
    # Crear directorio para gráficas si no existe
    if not os.path.exists('graficas'):
        os.makedirs('graficas')
    
    # 1. Comparativa de calidad (distancia)
    plt.figure(figsize=(12, 6))
    
    algoritmos = [
        'vecino_mas_cercano', 
        'insercion_mas_cercana', 
        'busqueda_local_mejor_mejora', 
        'busqueda_local_primera_mejora', 
        'ils_basico'
    ]
    
    nombres = [
        'VCN', 
        'IMC', 
        'BL (Mejor)', 
        'BL (Primera)', 
        'ILS'
    ]
    
    distancias = [resultados[alg]['distancia'] for alg in algoritmos]
    
    plt.barh(nombres, distancias, color='skyblue')
    plt.xlabel('Distancia (menor es mejor)')
    plt.title(f'Comparativa de calidad - {nombre_instancia}')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Anotar valores
    for i, v in enumerate(distancias):
        plt.text(v + max(distancias)*0.01, i, str(v), va='center')
    
    plt.tight_layout()
    plt.savefig(f'graficas/{nombre_instancia}_calidad.png')
    
    # 2. Comparativa de tiempos
    plt.figure(figsize=(12, 6))
    
    tiempos = [resultados[alg]['tiempo'] for alg in algoritmos]
    
    plt.barh(nombres, tiempos, color='salmon')
    plt.xlabel('Tiempo (segundos)')
    plt.title(f'Comparativa de tiempos - {nombre_instancia}')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Anotar valores
    for i, v in enumerate(tiempos):
        plt.text(v + max(tiempos)*0.05, i, f"{v:.4f}s", va='center')
    
    plt.tight_layout()
    plt.savefig(f'graficas/{nombre_instancia}_tiempos.png')
    
    # 3. Gráfica de convergencia ILS
    if 'historial' in resultados['ils_basico']:
        plt.figure(figsize=(12, 6))
        
        historial = resultados['ils_basico']['historial']
        iteraciones, distancias = zip(*historial)
        
        plt.plot(iteraciones, distancias, 'o-', color='green')
        plt.xlabel('Iteración')
        plt.ylabel('Distancia')
        plt.title(f'Convergencia ILS - {nombre_instancia}')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(f'graficas/{nombre_instancia}_convergencia_ils.png')
    
    plt.close('all')
    print(f"Gráficas guardadas en directorio 'graficas/'")

# Funciones para perturbaciones concurrentes
def aplicar_perturbacion_2opt(lista_compartida, tour_base, matriz, n_perturbaciones=1):
    n = len(tour_base)
    mejor_tour = None
    mejor_fo = float('inf')
    
    for _ in range(n_perturbaciones):
        # Perturbación mediante inversión de un segmento (2-opt)
        nuevo_tour = tour_base.copy()
        i = random.randint(1, n-2)
        j = random.randint(i+1, n-1)
        nuevo_tour[i:j+1] = reversed(nuevo_tour[i:j+1])
        
        # Calcular FO
        fo = calcular_fo(nuevo_tour, matriz)
        
        if fo < mejor_fo:
            mejor_fo = fo
            mejor_tour = nuevo_tour
    
    if mejor_tour:
        resultado = {
            'tour': mejor_tour,
            'fo': mejor_fo,
            'tipo': '2opt'
        }
        lista_compartida.append(resultado)

def aplicar_perturbacion_swap(lista_compartida, tour_base, matriz, n_perturbaciones=1):
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
            'tipo': 'swap'
        }
        lista_compartida.append(resultado)

def aplicar_perturbacion_insert(lista_compartida, tour_base, matriz, n_perturbaciones=1):
    n = len(tour_base)
    mejor_tour = None
    mejor_fo = float('inf')
    
    for _ in range(n_perturbaciones):
        # Perturbación mediante inserción de una ciudad en otra posición
        nuevo_tour = tour_base.copy()
        num_inserts = random.randint(1, min(5, n//10 + 1))
        
        for _ in range(num_inserts):
            i = random.randint(0, n-1)
            j = random.randint(0, n-1)
            if i != j:
                ciudad = nuevo_tour.pop(i)
                nuevo_tour.insert(j, ciudad)
        
        # Calcular FO
        fo = calcular_fo(nuevo_tour, matriz)
        
        if fo < mejor_fo:
            mejor_fo = fo
            mejor_tour = nuevo_tour
    
    if mejor_tour:
        resultado = {
            'tour': mejor_tour,
            'fo': mejor_fo,
            'tipo': 'insert'
        }
        lista_compartida.append(resultado)

def aplicar_perturbacion_scramble(lista_compartida, tour_base, matriz, n_perturbaciones=1):
    n = len(tour_base)
    mejor_tour = None
    mejor_fo = float('inf')
    
    for _ in range(n_perturbaciones):
        # Perturbación mediante aleatorización de un segmento
        nuevo_tour = tour_base.copy()
        i = random.randint(0, n-3)
        longitud = random.randint(2, min(n//3, 10))
        j = min(i + longitud, n-1)
        segmento = nuevo_tour[i:j+1]
        random.shuffle(segmento)
        nuevo_tour[i:j+1] = segmento
        
        # Calcular FO
        fo = calcular_fo(nuevo_tour, matriz)
        
        if fo < mejor_fo:
            mejor_fo = fo
            mejor_tour = nuevo_tour
    
    if mejor_tour:
        resultado = {
            'tour': mejor_tour,
            'fo': mejor_fo,
            'tipo': 'scramble'
        }
        lista_compartida.append(resultado)

def aplicar_perturbacion_3opt(lista_compartida, tour_base, matriz, n_perturbaciones=1):
    n = len(tour_base)
    mejor_tour = None
    mejor_fo = float('inf')
    
    for _ in range(n_perturbaciones):
        # Implementación simple de 3-opt (tres cortes en el tour)
        nuevo_tour = tour_base.copy()
        try:
            puntos_corte = sorted(random.sample(range(1, n), 3))
            a, b, c = puntos_corte
            
            # Una de las posibles reconexiones en 3-opt (hay varias)
            segmento1 = nuevo_tour[:a]
            segmento2 = nuevo_tour[a:b]
            segmento3 = nuevo_tour[b:c]
            segmento4 = nuevo_tour[c:]
            nuevo_tour = segmento1 + list(reversed(segmento2)) + segmento3 + segmento4
            
            # Calcular FO
            fo = calcular_fo(nuevo_tour, matriz)
            
            if fo < mejor_fo:
                mejor_fo = fo
                mejor_tour = nuevo_tour
        except:
            continue
    
    if mejor_tour:
        resultado = {
            'tour': mejor_tour,
            'fo': mejor_fo,
            'tipo': '3opt'
        }
        lista_compartida.append(resultado)

def generar_perturbaciones_concurrentes(tours_semilla, matriz, n_perturbaciones_por_tipo=5):
    """
    Genera perturbaciones de forma concurrente usando múltiples procesos
    """
    # Instanciar el administrador de procesos
    manager = mp.Manager()
    # Creamos la memoria compartida
    lista_compartida = manager.list()
    
    # Lista para almacenar todos los procesos
    todos_procesos = []
    
    # Tipos de perturbación disponibles
    funciones_perturbacion = [
        aplicar_perturbacion_2opt,
        aplicar_perturbacion_swap,
        aplicar_perturbacion_insert,
        aplicar_perturbacion_scramble,
        aplicar_perturbacion_3opt
    ]
    
    # Crear procesos para cada tipo de perturbación y cada tour semilla
    for tour_base in tours_semilla:
        for funcion_perturbacion in funciones_perturbacion:
            proceso = mp.Process(
                target=funcion_perturbacion,
                args=(lista_compartida, tour_base, matriz, n_perturbaciones_por_tipo)
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
    
    print(f"Tiempo total de generación concurrente: {tiempo_ejecucion:.4f}s")
    print(f"Total de perturbaciones generadas: {len(lista_compartida)}")
    
    # Convertir a lista normal
    return list(lista_compartida)

# Función para generar descendencia de forma concurrente
def generar_descendencia_concurrente(poblacion, matriz, n_descendientes, prob_mutacion=0.2):
    """
    Genera descendencia de forma concurrente mediante torneos, cruces y mutaciones
    """
    # Función que ejecutará cada proceso
    def generar_individuo(lista_compartida):
        # Selección de padres por torneo binario
        padre1 = selección_torneo(poblacion)
        padre2 = selección_torneo(poblacion)
        
        # Cruce OX (Order Crossover)
        hijo = cruce_ox(padre1['tour'], padre2['tour'])
        
        # Mutación con probabilidad
        if random.random() < prob_mutacion:
            hijo = mutación_2opt(hijo)
        
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

if __name__ == "__main__":
    # Mostrar el menú principal
    print("\n=== MENÚ PRINCIPAL ===")
    print("1. Algoritmo TSP ILS (ya implementado)")
    print("2. Algoritmo Genético (Chu-Beasley)")
    
    algoritmo = input("\nSeleccione el algoritmo a utilizar: ")
    
    if algoritmo not in ['1', '2']:
        print("Opción inválida.")
        exit()
    
    # Mostrar instancias disponibles
    instancias = [f for f in os.listdir('data') if f.endswith('.tsp')]
    
    print("\nInstancias disponibles:")
    for i, instancia in enumerate(instancias):
        print(f"{i+1}. {instancia}")
    
    # Solicitar selección
    seleccion = int(input("\nSeleccione una instancia (número): ")) - 1
    
    if 0 <= seleccion < len(instancias):
        archivo_instancia = os.path.join('data', instancias[seleccion])
        
        if algoritmo == '1':
            # Ejecutar TSP ILS
            resultados = ejecutar_comparativa_completa(archivo_instancia)
        else:
            # Ejecutar algoritmo genético de Chu-Beasley
            resultados = ejecutar_algoritmo_genetico(archivo_instancia)
    else:
        print("Selección inválida.")