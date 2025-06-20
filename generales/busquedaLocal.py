"""
Implementación de algoritmos de búsqueda local para el TSP
utilizando diferentes tipos de vecindarios.
"""

from typing import List, Dict, Callable
import random
from copy import deepcopy
import time
from .codificacionVecindarios import swap2, insert_izquierda, insert_derecha, distanciaTourVecino
from .matrizDistancias import matrizEuclidiana, distanciaTour


def busqueda_local_mejor_mejora(tour_inicial: list, matriz_distancias: list, 
                               funciones_vecindario: List[Callable], max_iter: int = 100) -> dict:
    """
    Algoritmo de búsqueda local utilizando la estrategia de mejor mejora.
    
    Args:
        tour_inicial: Lista de índices de ciudades que representa el tour inicial
        matriz_distancias: Matriz de distancias entre ciudades
        funciones_vecindario: Lista de funciones para generar vecindarios
        max_iter: Número máximo de iteraciones sin mejora
    
    Returns:
        Diccionario con el mejor tour encontrado y su distancia
    """
    mejor_solucion = tour_inicial.copy()
    mejor_distancia = distanciaTourVecino(mejor_solucion, matriz_distancias)
    
    iteraciones_sin_mejora = 0
    iteracion_actual = 0
    
    while iteraciones_sin_mejora < max_iter:
        iteracion_actual += 1
        mejora_encontrada = False
        
        # Para cada tipo de vecindario
        for funcion_vecindario in funciones_vecindario:
            # Generar vecinos según el tipo de vecindario
            vecinos = funcion_vecindario(mejor_solucion)
            
            # Evaluar cada vecino
            for vecino in vecinos:
                distancia_vecino = distanciaTourVecino(vecino, matriz_distancias)
                
                # Si es mejor, actualizamos
                if distancia_vecino < mejor_distancia:
                    mejor_solucion = vecino.copy()
                    mejor_distancia = distancia_vecino
                    mejora_encontrada = True
            
            # Si encontramos mejora con este vecindario, no probamos los demás
            if mejora_encontrada:
                break
        
        # Si no hubo mejora en esta iteración
        if not mejora_encontrada:
            iteraciones_sin_mejora += 1
        else:
            iteraciones_sin_mejora = 0
    
    return {
        'tour': mejor_solucion,
        'distancia': mejor_distancia,
        'iteraciones': iteracion_actual
    }

def busqueda_local_primera_mejora(tour_inicial: list, matriz_distancias: list, 
                                 funciones_vecindario: List[Callable], max_iter: int = 100) -> dict:
    """
    Algoritmo de búsqueda local utilizando la estrategia de primera mejora.
    
    Args:
        tour_inicial: Lista de índices de ciudades que representa el tour inicial
        matriz_distancias: Matriz de distancias entre ciudades
        funciones_vecindario: Lista de funciones para generar vecindarios
        max_iter: Número máximo de iteraciones sin mejora
    
    Returns:
        Diccionario con el mejor tour encontrado y su distancia
    """
    mejor_solucion = tour_inicial.copy()
    mejor_distancia = distanciaTourVecino(mejor_solucion, matriz_distancias)
    
    iteraciones_sin_mejora = 0
    iteracion_actual = 0
    
    while iteraciones_sin_mejora < max_iter:
        iteracion_actual += 1
        mejora_encontrada = False
        
        # Para cada tipo de vecindario
        for funcion_vecindario in funciones_vecindario:
            # Generar vecinos según el tipo de vecindario
            vecinos = funcion_vecindario(mejor_solucion)
            random.shuffle(vecinos)  # Aleatorizar el orden de exploración
            
            # Evaluar cada vecino hasta encontrar una mejora
            for vecino in vecinos:
                distancia_vecino = distanciaTourVecino(vecino, matriz_distancias)
                
                # Si es mejor, actualizamos y detenemos la búsqueda en este vecindario
                if distancia_vecino < mejor_distancia:
                    mejor_solucion = vecino.copy()
                    mejor_distancia = distancia_vecino
                    mejora_encontrada = True
                    break
            
            # Si encontramos mejora con este vecindario, no probamos los demás
            if mejora_encontrada:
                break
        
        # Si no hubo mejora en esta iteración
        if not mejora_encontrada:
            iteraciones_sin_mejora += 1
        else:
            iteraciones_sin_mejora = 0
    
    return {
        'tour': mejor_solucion,
        'distancia': mejor_distancia,
        'iteraciones': iteracion_actual
    }

# Función auxiliar para probar los algoritmos
def ejecutar_busqueda_local(caso, matriz_distancias, heuristica_constructor, vecindarios=None):
    """
    Ejecuta un algoritmo de búsqueda local sobre una solución inicial
    """
    if vecindarios is None:
        vecindarios = [swap2, insert_izquierda, insert_derecha]
    
    # Generar solución inicial con la heurística constructiva
    tour_inicial = heuristica_constructor(caso, matriz_distancias)
    
    print(f"Tour inicial (heurística): {tour_inicial['tour']}")
    distancia_inicial = distanciaTour(tour_inicial, matriz_distancias)
    print(f"Distancia inicial: {distancia_inicial}")
    
    # Ejecutar búsqueda local con mejor mejora
    inicio = time.time()
    resultado_mejor_mejora = busqueda_local_mejor_mejora(
        tour_inicial['tour'], 
        matriz_distancias, 
        vecindarios
    )
    tiempo_mejor_mejora = time.time() - inicio
    
    print("\nResultados con estrategia de mejor mejora:")
    print(f"Distancia final: {resultado_mejor_mejora['distancia']}")
    print(f"Mejora: {distancia_inicial - resultado_mejor_mejora['distancia']}")
    print(f"Tiempo: {tiempo_mejor_mejora:.2f} segundos")
    
    # Ejecutar búsqueda local con primera mejora
    inicio = time.time()
    resultado_primera_mejora = busqueda_local_primera_mejora(
        tour_inicial['tour'], 
        matriz_distancias, 
        vecindarios
    )
    tiempo_primera_mejora = time.time() - inicio
    
    print("\nResultados con estrategia de primera mejora:")
    print(f"Distancia final: {resultado_primera_mejora['distancia']}")
    print(f"Mejora: {distancia_inicial - resultado_primera_mejora['distancia']}")
    print(f"Tiempo: {tiempo_primera_mejora:.2f} segundos")
    
    return {
        'mejor_mejora': resultado_mejor_mejora,
        'primera_mejora': resultado_primera_mejora,
        'distancia_inicial': distancia_inicial
    }
