# presentado por Juan Camilo Garcia y Juan Pablo Gómez

"""
Script principal para ejecutar el algoritmo genético de Chu-Beasley para el TSP.
"""

import time
import os
import sys
import matplotlib.pyplot as plt
from typing import Dict

# Agregar la carpeta padre al path para importar desde shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos compartidos
from generales.leerInformacion import cargarCaso
from generales.matrizDistancias import matrizEuclidiana, distanciaTour
from generales.heuristicas import heuristicaVecinoMasCercano, heuristicaInsercionMasCercana, heuristicaInsercionMasLejana, heuristicaSavings, heuristicaChristofides
from geneticos import algoritmo_genetico_chu_beasley

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
    Muestra la información de ayuda sobre cómo usar el programa de algoritmo genético.
    """
    print("=== AYUDA DEL ALGORITMO GENÉTICO ===")
    print("\nUso:")
    print("  python main.py <ruta_archivo>     - Ejecuta el algoritmo genético con el archivo especificado")
    print("  python main.py --help            - Muestra esta ayuda")
    print("\nEjemplos:")
    print("  python main.py ../data/wi29.tsp")
    print("  python main.py \"C:\\ruta\\archivo\\tsp\\wi29.tsp\"")
    print("\nNota: Es OBLIGATORIO especificar la ruta del archivo TSP como argumento.")

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
    print(f"\nEjecutando Algoritmo Genético...")
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
    graficas_dir = os.path.join('..', 'graficas')
    if not os.path.exists(graficas_dir):
        os.makedirs(graficas_dir)
    
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
    plt.savefig(os.path.join(graficas_dir, f'{nombre_instancia}_convergencia_ga.png'))
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
    plt.savefig(os.path.join(graficas_dir, f'{nombre_instancia}_calidad_ga.png'))
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
    plt.savefig(os.path.join(graficas_dir, f'{nombre_instancia}_tiempos_ga.png'))
    plt.close()
    
    print(f"Gráficas guardadas en directorio '../graficas/':")
    print(f"  - {nombre_instancia}_convergencia_ga.png (Convergencia)")
    print(f"  - {nombre_instancia}_calidad_ga.png (Comparativa de calidad)")
    print(f"  - {nombre_instancia}_tiempos_ga.png (Comparativa de tiempos)")

if __name__ == "__main__":
    print("=== ALGORITMO GENÉTICO PARA TSP ===")
    
    # Verificar si se pasaron argumentos de línea de comandos
    if len(sys.argv) > 1:
        # Si el primer argumento es --help, mostrar ayuda
        if sys.argv[1] in ["--help", "-h", "help"]:
            mostrar_ayuda()
        else:
            # Validar y usar el archivo especificado
            archivo_especificado = sys.argv[1]
            if validar_archivo_tsp(archivo_especificado):
                ejecutar_algoritmo_genetico(archivo_especificado)
            else:
                print("\nError: No se pudo cargar el archivo especificado.")
                print("Use 'python main.py --help' para ver la ayuda.")
    else:
        # No se especificó archivo, mostrar error y ayuda
        print("Error: Debe especificar la ruta del archivo TSP como argumento.")
        print("\nUso: python main.py <ruta_archivo>")
        print("Ejemplo: python main.py ../data/wi29.tsp")
        print("\nPara más información, use: python main.py --help") 