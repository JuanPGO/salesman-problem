"""
Script principal para ejecutar y comparar todos los algoritmos del TSP implementados.
"""

import time
import os
import matplotlib.pyplot as plt
from typing import List, Dict

# Importar todos los módulos necesarios
from leerInformacion import cargarCaso
from matrizDistancias import matrizEuclidiana, distanciaTour
from heuristicas import heuristicaVecinoMasCercano, heuristicaInsercionMasCercana
from codificacionVecindarios import two_opt
from busquedaLocal import busqueda_local_mejor_mejora, busqueda_local_primera_mejora, ejecutar_busqueda_local
from perturbacion import perturbacion_3opt, perturbacion_parcial
from ils import ils_algorithm, ejecutar_ils_completo

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

if __name__ == "__main__":
    # Mostrar instancias disponibles
    instancias = [f for f in os.listdir('data') if f.endswith('.tsp')]
    
    print("Instancias disponibles:")
    for i, instancia in enumerate(instancias):
        print(f"{i+1}. {instancia}")
    
    # Solicitar selección
    seleccion = int(input("\nSeleccione una instancia (número): ")) - 1
    
    if 0 <= seleccion < len(instancias):
        archivo_instancia = os.path.join('data', instancias[seleccion])
        resultados = ejecutar_comparativa_completa(archivo_instancia)
    else:
        print("Selección inválida.")