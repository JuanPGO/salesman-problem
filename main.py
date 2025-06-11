# presentado por Juan Camilo Garcia y Juan Pablo Gómez

"""
Script principal para ejecutar y comparar todos los algoritmos del TSP implementados.
"""

import time
import os
import sys
import matplotlib.pyplot as plt
from typing import Dict

# Importar todos los módulos necesarios
from leerInformacion import cargarCaso
from matrizDistancias import matrizEuclidiana, distanciaTour
from heuristicas import heuristicaVecinoMasCercano, heuristicaInsercionMasCercana, heuristicaInsercionMasLejana, heuristicaSavings, heuristicaChristofides
from codificacionVecindarios import two_opt
from busquedaLocal import busqueda_local_mejor_mejora, busqueda_local_primera_mejora
from perturbacion import perturbacion_3opt
from ils import ils_algorithm
from geneticos import algoritmo_genetico_chu_beasley
from tsp_ortools import ejecutar_tsp_ortools
import random

def validar_archivo_tsp(ruta_archivo: str) -> bool:
    """
    Valida que el archivo TSP existe y es accesible.
    
    Args:
        ruta_archivo: Ruta al archivo TSP
        
    Returns:
        bool: True si el archivo es válido, False caso contrario
    """
    # Verificar si el archivo existe
    if not os.path.exists(ruta_archivo):
        print(f"Error: El archivo '{ruta_archivo}' no existe.")
        return False
    
    # Verificar si es un archivo (no un directorio)
    if not os.path.isfile(ruta_archivo):
        print(f"Error: '{ruta_archivo}' no es un archivo válido.")
        return False
    
    # Verificar si tiene extensión .tsp
    if not ruta_archivo.lower().endswith('.tsp'):
        print(f"Advertencia: El archivo '{ruta_archivo}' no tiene extensión .tsp")
        respuesta = input("¿Desea continuar de todas formas? [s/N]: ")
        if respuesta.lower() != 's':
            return False
    
    # Verificar si se puede leer el archivo
    try:
        with open(ruta_archivo, 'r') as f:
            f.read(1)  # Intentar leer al menos un carácter
    except Exception as e:
        print(f"Error: No se puede leer el archivo '{ruta_archivo}'. {e}")
        return False
    
    return True

def mostrar_ayuda():
    """
    Muestra la información de ayuda sobre cómo usar el programa.
    """
    print("=== AYUDA DEL PROGRAMA TSP ===")
    print("\nUso:")
    print("  python main.py <ruta_archivo>     - Ejecuta con el archivo especificado")
    print("  python main.py --help            - Muestra esta ayuda")
    print("\nEjemplos:")
    print("  python main.py data/wi29.tsp")
    print("  python main.py \"C:\\ruta\\archivo\\tsp\\wi29.tsp\"")
    print("\nNota: Es OBLIGATORIO especificar la ruta del archivo TSP como argumento.")

# FUNCIONES COMENTADAS - YA NO SE USAN CON LA NUEVA FUNCIONALIDAD
# def listar_archivos_tsp():
#     """Listar todos los archivos .tsp en el directorio data/"""
#     archivos = os.listdir("data")
#     return [archivo for archivo in archivos if archivo.endswith(".tsp")]

# def seleccionar_dataset():
#     """
#     Muestra los datasets disponibles y permite al usuario seleccionar uno
#     
#     Returns:
#         str: Nombre del archivo del dataset seleccionado o None si no hay datasets
#     """
#     archivos_tsp = listar_archivos_tsp()
#     
#     if not archivos_tsp:
#         print("Error: No se encontraron datasets en el directorio 'data/'")
#         return None
#     
#     print("\n=== DATASETS DISPONIBLES ===")
#     for i, archivo in enumerate(archivos_tsp, 1):
#         print(f"{i}. {archivo}")
#     
#     while True:
#         try:
#             opcion = int(input("\nSeleccione un dataset (número): "))
#             if 1 <= opcion <= len(archivos_tsp):
#                 return archivos_tsp[opcion-1]
#             else:
#                 print(f"Seleccione un número entre 1 y {len(archivos_tsp)}")
#         except ValueError:
#             print("Por favor, ingrese un número válido")

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

def ejecutar_algoritmo_ortools(archivo_instancia: str) -> Dict:
    """
    Ejecuta el algoritmo TSP usando OR-Tools con diferentes metaheurísticas.
    
    Args:
        archivo_instancia: Ruta al archivo de la instancia TSP
        
    Returns:
        Diccionario con los resultados
    """
    # Obtener el nombre de la instancia del nombre de archivo
    nombre_instancia = os.path.basename(archivo_instancia).split('.')[0]
    
    print(f"\n=== TSP CON OR-TOOLS ===")
    print(f"Instancia: {nombre_instancia}")
    print("="*50)
    
    # Ejecutar directamente TSP con OR-Tools
    resultado = ejecutar_tsp_ortools(archivo_instancia)
    
    # Preguntar si se desean generar gráficas
    if resultado and resultado.get('exito', False):
        generar_graficas = input("\n¿Desea generar gráficas comparativas con otros algoritmos? [s/N]: ")
        if generar_graficas.lower() == 's':
            print("\nGenerando comparativa con otros algoritmos...")
            generar_comparativa_ortools_vs_otros(archivo_instancia, resultado, nombre_instancia)
    
    return resultado

def generar_comparativa_ortools_vs_otros(archivo_instancia: str, resultado_ortools: Dict, nombre_instancia: str):
    """
    Genera una comparativa entre las diferentes metaheurísticas de OR-Tools.
    
    Args:
        archivo_instancia: Ruta al archivo de la instancia TSP
        resultado_ortools: Resultado del algoritmo OR-Tools con todos los resultados
        nombre_instancia: Nombre de la instancia para los títulos
    """
    try:
        print("Generando gráficas comparativas de metaheurísticas OR-Tools...")
        
        # Obtener todos los resultados de las metaheurísticas
        todos_resultados = resultado_ortools.get('todos_resultados', {})
        
        if not todos_resultados:
            print("No se encontraron resultados de metaheurísticas para generar gráficas.")
            return
        
        # Filtrar solo resultados exitosos
        resultados_exitosos = {k: v for k, v in todos_resultados.items() if v.get('exito', False)}
        
        if not resultados_exitosos:
            print("No hay resultados exitosos para generar gráficas.")
            return
        
        # Crear gráficas
        if not os.path.exists('graficas'):
            os.makedirs('graficas')
        
        # Preparar datos para las gráficas
        metaheuristicas = list(resultados_exitosos.keys())
        distancias = [resultados_exitosos[meta]['distancia'] for meta in metaheuristicas]
        tiempos = [resultados_exitosos[meta]['tiempo'] for meta in metaheuristicas]
        
        # Gráfica de calidad (distancias)
        plt.figure(figsize=(12, 8))
        colores = ['lightblue', 'lightgreen', 'orange', 'lightcoral', 'gold', 'lightpink']
        
        plt.barh(metaheuristicas, distancias, color=colores[:len(metaheuristicas)])
        plt.xlabel('Distancia (menor es mejor)')
        plt.title(f'Comparativa de Metaheurísticas OR-Tools - Calidad - {nombre_instancia}')
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Anotar valores
        for i, v in enumerate(distancias):
            plt.text(v + max(distancias)*0.01, i, str(v), va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'graficas/{nombre_instancia}_ortools_comparativa.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Gráfica de tiempos
        plt.figure(figsize=(12, 8))
        colores_tiempo = ['salmon', 'lightcoral', 'gold', 'lightsteelblue', 'lightseagreen', 'plum']
        
        plt.barh(metaheuristicas, tiempos, color=colores_tiempo[:len(metaheuristicas)])
        plt.xlabel('Tiempo (segundos)')
        plt.title(f'Comparativa de Metaheurísticas OR-Tools - Tiempos - {nombre_instancia}')
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Anotar valores
        for i, v in enumerate(tiempos):
            plt.text(v + max(tiempos)*0.05, i, f"{v:.4f}s", va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'graficas/{nombre_instancia}_ortools_tiempos.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Gráfica combinada (ranking de calidad vs tiempo)
        plt.figure(figsize=(14, 10))
        
        # Crear subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Ordenar por calidad (distancia)
        datos_ordenados = sorted(resultados_exitosos.items(), key=lambda x: x[1]['distancia'])
        metas_ord, datos_ord = zip(*datos_ordenados)
        distancias_ord = [d['distancia'] for _, d in datos_ordenados]
        tiempos_ord = [d['tiempo'] for _, d in datos_ordenados]
        
        # Subplot 1: Ranking por calidad
        ax1.barh(range(len(metas_ord)), distancias_ord, color=colores[:len(metas_ord)])
        ax1.set_yticks(range(len(metas_ord)))
        ax1.set_yticklabels(metas_ord)
        ax1.set_xlabel('Distancia (menor es mejor)')
        ax1.set_title(f'Ranking por Calidad - {nombre_instancia}')
        ax1.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Anotar valores en subplot 1
        for i, v in enumerate(distancias_ord):
            ax1.text(v + max(distancias_ord)*0.01, i, str(v), va='center', fontweight='bold')
        
        # Subplot 2: Tiempos correspondientes
        ax2.barh(range(len(metas_ord)), tiempos_ord, color=colores_tiempo[:len(metas_ord)])
        ax2.set_yticks(range(len(metas_ord)))
        ax2.set_yticklabels(metas_ord)
        ax2.set_xlabel('Tiempo (segundos)')
        ax2.set_title(f'Tiempos de Ejecución - {nombre_instancia}')
        ax2.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Anotar valores en subplot 2
        for i, v in enumerate(tiempos_ord):
            ax2.text(v + max(tiempos_ord)*0.05, i, f"{v:.4f}s", va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'graficas/{nombre_instancia}_ortools_ranking.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Gráficas comparativas guardadas en directorio 'graficas/':")
        print(f"  - {nombre_instancia}_ortools_comparativa.png (Comparativa de calidad)")
        print(f"  - {nombre_instancia}_ortools_tiempos.png (Comparativa de tiempos)")
        print(f"  - {nombre_instancia}_ortools_ranking.png (Ranking combinado)")
        
        # Mostrar resumen
        print(f"\n{'='*70}")
        print(f"RESUMEN COMPARATIVO METAHEURÍSTICAS OR-TOOLS - {nombre_instancia}")
        print(f"{'='*70}")
        print(f"{'Rank':<4} {'Metaheurística':<20} {'Distancia':<12} {'Tiempo':<10}")
        print("-" * 50)
        
        for i, (meta, datos) in enumerate(datos_ordenados, 1):
            print(f"{i:<4} {meta:<20} {datos['distancia']:<12} {datos['tiempo']:<10.4f}")
        
    except Exception as e:
        print(f"Error generando comparativa: {e}")

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
    
    # Ejecutar heurísticas constructivas para comparación
    print("\nEjecutando heurísticas constructivas para comparación...")
    
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
    
    # Inserción más lejana
    inicio = time.time()
    resultado_iml = heuristicaInsercionMasLejana(caso, matriz)
    tiempo_iml = time.time() - inicio
    distancia_iml = distanciaTour(resultado_iml, matriz)
    print(f"Inserción más lejana: {distancia_iml} (tiempo: {tiempo_iml:.4f}s)")
    
    # Savings
    inicio = time.time()
    resultado_savings = heuristicaSavings(caso, matriz)
    tiempo_savings = time.time() - inicio
    distancia_savings = distanciaTour(resultado_savings, matriz)
    print(f"Savings: {distancia_savings} (tiempo: {tiempo_savings:.4f}s)")
    
    # Christofides
    try:
        inicio = time.time()
        resultado_christofides = heuristicaChristofides(caso, matriz)
        tiempo_christofides = time.time() - inicio
        distancia_christofides = distanciaTour(resultado_christofides, matriz)
        print(f"Christofides: {distancia_christofides} (tiempo: {tiempo_christofides:.4f}s)")
    except Exception as e:
        print(f"No se pudo ejecutar Christofides: {e}")
        resultado_christofides = resultado_vcn  # Usar VCN como fallback
        tiempo_christofides = 0
        distancia_christofides = distancia_vcn
    
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
    
    # Preparar resultados para las gráficas
    resultados_completos = {
        'tour': resultado_ga['tour'],
        'distancia': distancia,
        'tiempo': tiempo_ga,
        'mejoras': resultado_ga['mejoras'],
        'historial': resultado_ga['historial'],
        'heuristicas': {
            'vcn': {
                'distancia': distancia_vcn,
                'tiempo': tiempo_vcn
            },
            'imc': {
                'distancia': distancia_imc,
                'tiempo': tiempo_imc
            },
            'iml': {
                'distancia': distancia_iml,
                'tiempo': tiempo_iml
            },
            'savings': {
                'distancia': distancia_savings,
                'tiempo': tiempo_savings
            },
            'christofides': {
                'distancia': distancia_christofides,
                'tiempo': tiempo_christofides
            }
        }
    }
    
    # Generar gráficas
    generar_graficas = input("\n¿Desea generar gráficas del algoritmo genético? [s/N]: ")
    if generar_graficas.lower() == 's':
        print("\nGenerando gráficas...")
        generar_graficas_comparativas_ga(resultados_completos, nombre_instancia)
    
    return resultados_completos

def generar_graficas_comparativas_ga(resultados: Dict, nombre_instancia: str):
    """
    Genera gráficas comparativas para el algoritmo genético.
    
    Args:
        resultados: Diccionario con los resultados del algoritmo
        nombre_instancia: Nombre de la instancia para los títulos
    """
    # Crear directorio para gráficas si no existe
    if not os.path.exists('graficas'):
        os.makedirs('graficas')
    
    # 1. Gráfica de convergencia
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
    plt.close()
    
    # 2. Gráfica de calidad (comparativa con otros algoritmos)
    plt.figure(figsize=(12, 6))
    
    # Comparar con todas las heurísticas constructivas
    algoritmos = [
        'Vecino más cercano',
        'Inserción más cercana',
        'Inserción más lejana',
        'Savings',
        'Christofides',
        'Algoritmo Genético'
    ]
    
    distancias = [
        resultados['heuristicas']['vcn']['distancia'],
        resultados['heuristicas']['imc']['distancia'],
        resultados['heuristicas']['iml']['distancia'],
        resultados['heuristicas']['savings']['distancia'],
        resultados['heuristicas']['christofides']['distancia'],
        resultados['distancia']
    ]
    
    plt.barh(algoritmos, distancias, color='skyblue')
    plt.xlabel('Distancia (menor es mejor)')
    plt.title(f'Comparativa de calidad - {nombre_instancia}')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Anotar valores
    for i, v in enumerate(distancias):
        plt.text(v + max(distancias)*0.01, i, str(v), va='center')
    
    plt.tight_layout()
    plt.savefig(f'graficas/{nombre_instancia}_calidad_ga.png')
    plt.close()
    
    # 3. Gráfica de tiempos
    plt.figure(figsize=(12, 6))
    
    tiempos = [
        resultados['heuristicas']['vcn']['tiempo'],
        resultados['heuristicas']['imc']['tiempo'],
        resultados['heuristicas']['iml']['tiempo'],
        resultados['heuristicas']['savings']['tiempo'],
        resultados['heuristicas']['christofides']['tiempo'],
        resultados['tiempo']
    ]
    
    plt.barh(algoritmos, tiempos, color='salmon')
    plt.xlabel('Tiempo (segundos)')
    plt.title(f'Comparativa de tiempos - {nombre_instancia}')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Anotar valores
    for i, v in enumerate(tiempos):
        plt.text(v + max(tiempos)*0.05, i, f"{v:.4f}s", va='center')
    
    plt.tight_layout()
    plt.savefig(f'graficas/{nombre_instancia}_tiempos_ga.png')
    plt.close()
    
    print(f"Gráficas guardadas en directorio 'graficas/'")

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

def menu_principal_con_archivo(archivo_tsp: str):
    """
    Muestra el menú principal cuando se especifica un archivo específico.
    
    Args:
        archivo_tsp: Ruta al archivo TSP a procesar
    """
    nombre_archivo = os.path.basename(archivo_tsp)
    
    while True:
        print(f"\n=== MENÚ PRINCIPAL - ARCHIVO: {nombre_archivo} ===")
        print("1. Algoritmo TSP ILS (Iterated Local Search)")
        print("2. Algoritmo Genético (Chu-Beasley)")
        print("3. TSP con OR-Tools (Metaheurísticas)")
        print("4. Salir")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            print(f"\nEjecutando ILS con archivo: {archivo_tsp}")
            ejecutar_algoritmo_ils(archivo_tsp)
        
        elif opcion == '2':
            print(f"\nEjecutando Algoritmo Genético con archivo: {archivo_tsp}")
            ejecutar_algoritmo_genetico(archivo_tsp)
        
        elif opcion == '3':
            print(f"\nEjecutando TSP con OR-Tools con archivo: {archivo_tsp}")
            ejecutar_algoritmo_ortools(archivo_tsp)
        
        elif opcion == '4':
            print("Saliendo del programa...")
            break
        
        else:
            print("Opción no válida. Intente de nuevo.")

# def menu_principal():
#     """
#     Muestra el menú principal y maneja la selección del usuario
#     """
#     while True:
#         print("\n=== MENÚ PRINCIPAL ===")
#         print("1. Algoritmo TSP ILS (Iterated Local Search)")
#         print("2. Algoritmo Genético (Chu-Beasley)")
#         print("3. Salir")
#         
#         opcion = input("\nSeleccione una opción: ")
#         
#         if opcion == '1':
#             dataset = seleccionar_dataset()
#             if dataset:
#                 ejecutar_algoritmo_ils(f"data/{dataset}")
#         
#         elif opcion == '2':
#             dataset = seleccionar_dataset()
#             if dataset:
#                 ejecutar_algoritmo_genetico(f"data/{dataset}")
#         
#         elif opcion == '3':
#             print("Saliendo del programa...")
#             break
#         
#         else:
#             print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    # Verificar si se pasaron argumentos de línea de comandos
    if len(sys.argv) > 1:
        # Si el primer argumento es --help, mostrar ayuda
        if sys.argv[1] in ["--help", "-h", "help"]:
            mostrar_ayuda()
        else:
            # Validar y usar el archivo especificado
            archivo_especificado = sys.argv[1]
            if validar_archivo_tsp(archivo_especificado):
                menu_principal_con_archivo(archivo_especificado)
            else:
                print("\nError: No se pudo cargar el archivo especificado.")
                print("Use 'python main.py --help' para ver la ayuda.")
    else:
        # No se especificó archivo, mostrar error y ayuda
        print("Error: Debe especificar la ruta del archivo TSP como argumento.")
        print("\nUso: python main.py <ruta_archivo>")
        print("Ejemplo: python main.py data/wi29.tsp")
        print("\nPara más información, use: python main.py --help")