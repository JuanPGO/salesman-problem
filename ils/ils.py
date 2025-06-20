"""
Implementación del algoritmo Iterated Local Search (ILS) para TSP.
Integra las fases de construcción, búsqueda local (explotación) y perturbación (exploración).
"""

import time
import random
import os
from typing import List, Dict, Callable, Tuple

# Importar módulos necesarios
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generales.leerInformacion import cargarCaso
from generales.matrizDistancias import matrizEuclidiana, distanciaTour
from generales.heuristicas import heuristicaVecinoMasCercano, heuristicaInsercionMasCercana
from generales.codificacionVecindarios import two_opt, distanciaTourVecino
from generales.busquedaLocal import busqueda_local_mejor_mejora, busqueda_local_primera_mejora
from generales.perturbacion import perturbacion_3opt, perturbacion_parcial

def ils_algorithm(caso: dict, matriz_distancias: list, 
                  heuristica_constructor: Callable,
                  busqueda_local_fn: Callable,
                  perturbacion_fn: Callable,
                  vecindarios: List[Callable] = None,
                  max_iteraciones: int = 100,
                  max_sin_mejora: int = 20,
                  tiempo_limite: int = 60) -> dict:
    """
    Algoritmo Iterated Local Search para el TSP.
    
    Args:
        caso: Diccionario con la información del problema
        matriz_distancias: Matriz de distancias entre ciudades
        heuristica_constructor: Función constructiva para generar solución inicial
        busqueda_local_fn: Función de búsqueda local a utilizar
        perturbacion_fn: Función de perturbación a utilizar
        vecindarios: Lista de funciones generadoras de vecindarios
        max_iteraciones: Número máximo de iteraciones totales
        max_sin_mejora: Número máximo de iteraciones sin mejora
        tiempo_limite: Tiempo límite en segundos
        
    Returns:
        Diccionario con la mejor solución encontrada y estadísticas
    """
    if vecindarios is None:
        vecindarios = [two_opt]
    
    # Generar solución inicial con la heurística constructiva
    inicio_tiempo = time.time()
    solucion_inicial = heuristica_constructor(caso, matriz_distancias)
    
    # Aplicar búsqueda local a la solución inicial
    resultado_bl = busqueda_local_fn(solucion_inicial['tour'], matriz_distancias, vecindarios)
    
    # La mejor solución hasta el momento es el resultado de la búsqueda local inicial
    mejor_solucion = resultado_bl['tour']
    mejor_distancia = resultado_bl['distancia']
    
    # Inicializar variables de control
    iteracion_actual = 0
    iteraciones_sin_mejora = 0
    mejoras_totales = 0
    
    historial_mejoras = [(0, mejor_distancia)]  # (iteración, distancia)
    
    # Ejecutar el algoritmo ILS
    while (iteracion_actual < max_iteraciones and 
           iteraciones_sin_mejora < max_sin_mejora and 
           (time.time() - inicio_tiempo) < tiempo_limite):
        
        iteracion_actual += 1
        
        # FASE DE PERTURBACIÓN: Perturbar la mejor solución actual
        solucion_perturbada = perturbacion_fn(mejor_solucion)
        
        # FASE DE BÚSQUEDA LOCAL: Mejorar la solución perturbada
        resultado_bl = busqueda_local_fn(solucion_perturbada, matriz_distancias, vecindarios, max_iter=20)
        nueva_solucion = resultado_bl['tour']
        nueva_distancia = resultado_bl['distancia']
        
        # Criterio de aceptación: Si la nueva solución es mejor, la aceptamos
        if nueva_distancia < mejor_distancia:
            mejor_solucion = nueva_solucion
            mejor_distancia = nueva_distancia
            iteraciones_sin_mejora = 0
            mejoras_totales += 1
            historial_mejoras.append((iteracion_actual, mejor_distancia))
        else:
            iteraciones_sin_mejora += 1
        
        # Imprimir progreso cada 5 iteraciones
        if iteracion_actual % 5 == 0:
            tiempo_transcurrido = time.time() - inicio_tiempo
            print(f"Iteración {iteracion_actual}, Mejor distancia: {mejor_distancia}, "
                  f"Tiempo: {tiempo_transcurrido:.2f}s")
    
    tiempo_total = time.time() - inicio_tiempo
    
    # Construir resultado final
    resultado = {
        'tour': mejor_solucion,
        'distancia': mejor_distancia,
        'iteraciones_totales': iteracion_actual,
        'mejoras_encontradas': mejoras_totales,
        'tiempo_total': tiempo_total,
        'historial_mejoras': historial_mejoras
    }
    
    return resultado

def ejecutar_ils_completo(caso: dict, matriz_distancias: list) -> dict:
    """
    Ejecuta el algoritmo ILS con diferentes configuraciones y devuelve el mejor resultado.
    
    Args:
        caso: Diccionario con la información del problema
        matriz_distancias: Matriz de distancias entre ciudades
        
    Returns:
        Diccionario con el mejor resultado encontrado
    """
    # Obtener el nombre de la instancia si está disponible en los datos del problema
    nombre_instancia = os.path.basename(caso.get('archivo', 'instancia_desconocida')).split('.')[0]
    
    print("="*50)
    print(f"Ejecutando ILS para instancia: {nombre_instancia}")
    print(f"Dimensión: {caso['dimension']}")
    print("="*50)
    
    # Configuraciones para probar
    heuristicas = [
        ("Vecino más cercano", heuristicaVecinoMasCercano),
        ("Inserción más cercana", heuristicaInsercionMasCercana)
    ]
    
    busquedas_locales = [
        ("Mejor mejora", busqueda_local_mejor_mejora),
        ("Primera mejora", busqueda_local_primera_mejora)
    ]
    
    perturbaciones = [
        ("3-Opt", perturbacion_3opt),
        ("Parcial (60%)", perturbacion_parcial)
    ]
    
    # Configurar vecindario (solo two_opt)
    vecindarios = [two_opt]
    
    # Almacenar todos los resultados
    resultados = []
    
    # Probar diferentes combinaciones
    for nombre_h, heuristica in heuristicas:
        for nombre_bl, busqueda_local in busquedas_locales:
            for nombre_p, perturbacion in perturbaciones:
                print(f"\nProbando: {nombre_h} + {nombre_bl} + {nombre_p}")
                
                # Ejecutar ILS con esta configuración
                resultado = ils_algorithm(
                    caso, 
                    matriz_distancias, 
                    heuristica, 
                    busqueda_local, 
                    perturbacion,
                    vecindarios=vecindarios,
                    max_iteraciones=15,
                    max_sin_mejora=8,
                    tiempo_limite=15  # Limitar a 15 segundos por combinación
                )
                
                # Agregar información de configuración
                resultado['configuracion'] = {
                    'heuristica': nombre_h,
                    'busqueda_local': nombre_bl,
                    'perturbacion': nombre_p
                }
                
                print(f"Distancia: {resultado['distancia']}")
                print(f"Tiempo: {resultado['tiempo_total']:.2f}s")
                
                resultados.append(resultado)
    
    # Ordenar resultados por distancia (menor a mayor)
    resultados.sort(key=lambda x: x['distancia'])
    
    # Mostrar resultados
    print("\n" + "="*50)
    print("RESUMEN DE RESULTADOS:")
    print("="*50)
    
    for i, res in enumerate(resultados[:5]):  # Top 5
        config = res['configuracion']
        print(f"{i+1}. Distancia: {res['distancia']}, Tiempo: {res['tiempo_total']:.2f}s")
        print(f"   Config: {config['heuristica']} + {config['busqueda_local']} + {config['perturbacion']}")
    
    return resultados[0]  # Devolver el mejor resultado

# Ejemplo de uso
if __name__ == "__main__":
    # Cargar datos
    caso = cargarCaso("data/wi29.tsp")
    matriz = matrizEuclidiana(caso)
    
    # Ejecutar ILS con una configuración específica
    print("Ejecutando ILS con configuración estándar:")
    resultado_ils = ils_algorithm(
        caso,
        matriz,
        heuristicaInsercionMasCercana,
        busqueda_local_mejor_mejora,
        perturbacion_3opt,
        vecindarios=[two_opt],
        max_iteraciones=20,
        max_sin_mejora=10,
        tiempo_limite=30
    )
    
    print("\nMejor distancia encontrada:", resultado_ils['distancia'])
    print("Iteraciones totales:", resultado_ils['iteraciones_totales'])
    print("Tiempo total:", resultado_ils['tiempo_total'])
    
    # Para un análisis más completo, descomentar la siguiente línea:
    # mejor_resultado = ejecutar_ils_completo(caso, matriz) 