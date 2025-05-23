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
import math

# Importar todos los módulos necesarios
from leerInformacion import cargarCaso
from matrizDistancias import matrizEuclidiana, distanciaTour
from heuristicas import heuristicaVecinoMasCercano, heuristicaInsercionMasCercana
from codificacionVecindarios import two_opt
from busquedaLocal import busqueda_local_mejor_mejora, busqueda_local_primera_mejora
from perturbacion import perturbacion_3opt
from ils import ils_algorithm
from geneticos import algoritmo_genetico_chu_beasley
import random

def listar_archivos_tsp():
    """Listar todos los archivos .tsp en el directorio data/"""
    archivos = os.listdir("data")
    return [archivo for archivo in archivos if archivo.endswith(".tsp")]

def seleccionar_dataset():
    """
    Muestra los datasets disponibles y permite al usuario seleccionar uno
    
    Returns:
        str: Nombre del archivo del dataset seleccionado o None si no hay datasets
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

def ejecutar_algoritmo_ils(archivo_instancia: str) -> Dict:
    """
    Ejecuta el algoritmo ILS (Iterated Local Search) para resolver el TSP.
    
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
    
    print(f"\nCOMPARATIVA COMPLETA PARA: {nombre_instancia}")
    print(f"Dimensión: {caso['dimension']} ciudades")
    print("="*70)
    
    # 1. HEURÍSTICAS CONSTRUCTIVAS
    print("\n1. HEURÍSTICAS CONSTRUCTIVAS")
    print("-"*40)
    
    # Vecino más cercano
    inicio = time.time()
    resultado_vcn = heuristicaVecinoMasCercano(caso, matriz)
    tiempo_vcn = time.time() - inicio
    distancia_vcn = distanciaTour(resultado_vcn, matriz)
    print(f"Vecino más cercano: {distancia_vcn} (tiempo: {tiempo_vcn:.4f}s)")
    
    # Inserción más cercana
    inicio = time.time()
    resultado_imc = heuristicaInsercionMasCercana(caso, matriz)
    tiempo_imc = time.time() - inicio
    distancia_imc = distanciaTour(resultado_imc, matriz)
    print(f"Inserción más cercana: {distancia_imc} (tiempo: {tiempo_imc:.4f}s)")
    
    # Determinar la mejor heurística constructiva
    if distancia_vcn <= distancia_imc:
        mejor_heuristica = "Vecino más cercano"
        resultado_inicial = resultado_vcn
        distancia_inicial = distancia_vcn
    else:
        mejor_heuristica = "Inserción más cercana"
        resultado_inicial = resultado_imc
        distancia_inicial = distancia_imc
    
    # 2. BÚSQUEDA LOCAL
    print("\n2. BÚSQUEDA LOCAL")
    print("-"*40)
    print(f"Mejor heurística constructiva: {mejor_heuristica} ({distancia_inicial})")
    
    # Búsqueda local (mejor mejora)
    inicio = time.time()
    resultado_bl_mejor = busqueda_local_mejor_mejora(
        resultado_inicial['tour'], 
        matriz, 
        [two_opt]
    )
    tiempo_bl_mejor = time.time() - inicio
    print(f"Búsqueda local (mejor mejora): {resultado_bl_mejor['distancia']} (tiempo: {tiempo_bl_mejor:.4f}s)")
    
    # Búsqueda local (primera mejora)
    inicio = time.time()
    resultado_bl_primera = busqueda_local_primera_mejora(
        resultado_inicial['tour'], 
        matriz, 
        [two_opt]
    )
    tiempo_bl_primera = time.time() - inicio
    print(f"Búsqueda local (primera mejora): {resultado_bl_primera['distancia']} (tiempo: {tiempo_bl_primera:.4f}s)")
    
    # 3. ITERATED LOCAL SEARCH (ILS)
    print("\n3. ITERATED LOCAL SEARCH (ILS)")
    print("-"*40)
    
    # Ejecutar algoritmo ILS
    inicio = time.time()
    resultado_ils = ils_algorithm(
        caso, 
        matriz, 
        heuristicaInsercionMasCercana,
        busqueda_local_mejor_mejora,
        perturbacion_3opt,
        vecindarios=[two_opt],
        max_iteraciones=100,
        max_sin_mejora=20,
        tiempo_limite=60
    )
    tiempo_ils = time.time() - inicio
    
    # Las iteraciones ya son impresas por ils_algorithm
    
    print(f"ILS básico: {resultado_ils['distancia']} (tiempo: {tiempo_ils:.4f}s)")
    print(f"    Mejoras encontradas: {resultado_ils['mejoras_encontradas']}")
    print(f"    Iteraciones totales: {resultado_ils['iteraciones_totales']}")
    
    # Preparar resultados para las gráficas
    resultados_completos = {
        'vecino_mas_cercano': {
            'distancia': distancia_vcn,
            'tiempo': tiempo_vcn
        },
        'insercion_mas_cercana': {
            'distancia': distancia_imc,
            'tiempo': tiempo_imc
        },
        'busqueda_local_mejor_mejora': {
            'distancia': resultado_bl_mejor['distancia'],
            'tiempo': tiempo_bl_mejor
        },
        'busqueda_local_primera_mejora': {
            'distancia': resultado_bl_primera['distancia'],
            'tiempo': tiempo_bl_primera
        },
        'ils_basico': {
            'distancia': resultado_ils['distancia'],
            'tiempo': tiempo_ils,
            'historial': resultado_ils['historial_mejoras']
        }
    }
    
    # Preguntar si se desean generar gráficas
    generar_graficas = input("\n¿Desea generar gráficas comparativas? [s/N]: ")
    if generar_graficas.lower() == 's':
        print("\nGenerando gráficas...")
        generar_graficas_comparativas(resultados_completos, nombre_instancia)
    
    return resultado_ils

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
    
    print(f"\nEjecutando Algoritmo Genético con el dataset {nombre_instancia}...")
    
    # Ejecutar algoritmo genético
    inicio = time.time()
    resultado_ga = algoritmo_genetico_chu_beasley(caso, matriz)
    tiempo_ga = time.time() - inicio
    
    # Calcular la distancia total del tour
    distancia = resultado_ga['distancia']
    
    print("\n=== RESULTADO FINAL ===")
    print(f"Mejor distancia encontrada: {distancia}")
    print(f"Tour: {resultado_ga['tour']}")
    print(f"Tiempo total: {tiempo_ga:.4f} segundos")
    print(f"Mejoras encontradas: {resultado_ga['mejoras']}")
    
    # 3. Generar gráficas
    generar_graficas = input("\n¿Desea generar gráficas del algoritmo genético? [s/N]: ")
    if generar_graficas.lower() == 's':
        print("\nGenerando gráficas...")
        generar_grafica_convergencia_ga(resultado_ga, nombre_instancia)
    
    return resultado_ga

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
    
    historial = resultados['historial']
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
                ejecutar_algoritmo_ils(f"data/{dataset}")
        
        elif opcion == '2':
            dataset = seleccionar_dataset()
            if dataset:
                ejecutar_algoritmo_genetico(f"data/{dataset}")
        
        elif opcion == '3':
            print("Saliendo del programa...")
            break
        
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    menu_principal()