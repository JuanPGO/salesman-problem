# presentado por Juan Camilo Garcia y Juan Pablo Gómez

"""
Script principal para ejecutar el algoritmo ILS (Iterated Local Search) para el TSP.
"""

import time
import os
import sys
import matplotlib.pyplot as plt
from typing import Dict

# Agregar la carpeta padre al path para importar desde shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos compartidos
from shared.leerInformacion import cargarCaso
from shared.matrizDistancias import matrizEuclidiana, distanciaTour
from shared.heuristicas import heuristicaVecinoMasCercano, heuristicaInsercionMasCercana, heuristicaInsercionMasLejana, heuristicaSavings, heuristicaChristofides
from shared.codificacionVecindarios import two_opt
from shared.busquedaLocal import busqueda_local_mejor_mejora, busqueda_local_primera_mejora
from shared.perturbacion import perturbacion_3opt
from ils import ils_algorithm

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
    Muestra la información de ayuda sobre cómo usar el programa ILS.
    """
    print("=== AYUDA DEL ALGORITMO ILS ===")
    print("\nUso:")
    print("  python main_ils.py <ruta_archivo>     - Ejecuta ILS con el archivo especificado")
    print("  python main_ils.py --help            - Muestra esta ayuda")
    print("\nEjemplos:")
    print("  python main_ils.py ../data/wi29.tsp")
    print("  python main_ils.py \"C:\\ruta\\archivo\\tsp\\wi29.tsp\"")
    print("\nNota: Es OBLIGATORIO especificar la ruta del archivo TSP como argumento.")

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

def generar_graficas_comparativas(resultados: Dict, nombre_instancia: str):
    """
    Genera gráficas comparativas de los algoritmos.
    
    Args:
        resultados: Diccionario con los resultados de todos los algoritmos
        nombre_instancia: Nombre de la instancia para los títulos
    """
    # Crear directorio para gráficas si no existe
    graficas_dir = os.path.join('..', 'graficas')
    if not os.path.exists(graficas_dir):
        os.makedirs(graficas_dir)
    
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
    plt.savefig(os.path.join(graficas_dir, f'{nombre_instancia}_calidad.png'))
    
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
    plt.savefig(os.path.join(graficas_dir, f'{nombre_instancia}_tiempos.png'))
    
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
        plt.savefig(os.path.join(graficas_dir, f'{nombre_instancia}_convergencia_ils.png'))
    
    plt.close('all')
    print(f"Gráficas guardadas en directorio '../graficas/'")

if __name__ == "__main__":
    print("=== ALGORITMO ILS PARA TSP ===")
    
    # Verificar si se pasaron argumentos de línea de comandos
    if len(sys.argv) > 1:
        # Si el primer argumento es --help, mostrar ayuda
        if sys.argv[1] in ["--help", "-h", "help"]:
            mostrar_ayuda()
        else:
            # Validar y usar el archivo especificado
            archivo_especificado = sys.argv[1]
            if validar_archivo_tsp(archivo_especificado):
                ejecutar_algoritmo_ils(archivo_especificado)
            else:
                print("\nError: No se pudo cargar el archivo especificado.")
                print("Use 'python main_ils.py --help' para ver la ayuda.")
    else:
        # No se especificó archivo, mostrar error y ayuda
        print("Error: Debe especificar la ruta del archivo TSP como argumento.")
        print("\nUso: python main_ils.py <ruta_archivo>")
        print("Ejemplo: python main_ils.py ../data/wi29.tsp")
        print("\nPara más información, use: python main_ils.py --help") 