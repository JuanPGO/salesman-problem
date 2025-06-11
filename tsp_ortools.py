"""
Modelo del Traveling Salesman Problem (TSP) usando OR-Tools.
Implementación simple basada en metaheurísticas.
"""

from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import time
from typing import Dict
from leerInformacion import cargarCaso
from matrizDistancias import matrizEuclidiana, distanciaTour

def resolver_tsp_metaheuristicas(
    archivo_instancia,
    metaheuristica,
    nombre_metaheuristica,
    tiempo_limite=10
):
    """
    Resuelve el TSP usando OR-Tools con la metaheurística especificada.
    
    Args:
        archivo_instancia: Ruta al archivo de la instancia TSP
        metaheuristica: Metaheurística de OR-Tools a usar
        nombre_metaheuristica: Nombre descriptivo de la metaheurística
        tiempo_limite: Tiempo límite en segundos
    """
    
    # Cargar datos y preprocesar
    caso = cargarCaso(archivo_instancia)
    matriz_distancias = matrizEuclidiana(caso)
    num_ciudades = caso['dimension']
    
    print(f"\n----- Resolviendo TSP con: {nombre_metaheuristica} -----")
    print(f"Número de ciudades: {num_ciudades}")
    
    inicio_tiempo = time.time()
    
    # 1. Crear el manager del routing
    manager = pywrapcp.RoutingIndexManager(
        num_ciudades,  # Número de nodos (ciudades)
        1,             # Número de vehículos (solo uno para TSP)
        0              # Depósito (ciudad inicial, índice 0)
    )
    
    # 2. Crear el modelo de routing
    routing = pywrapcp.RoutingModel(manager)
    
    # 3. Definir la función de callback para los costos (distancias)
    def callback_distancia(desde_indice, hasta_indice):
        """Retorna la distancia entre dos nodos."""
        desde_nodo = manager.IndexToNode(desde_indice)
        hasta_nodo = manager.IndexToNode(hasta_indice)
        return int(matriz_distancias[desde_nodo][hasta_nodo])
    
    # Registrar el callback de distancia
    indice_callback_distancia = routing.RegisterTransitCallback(callback_distancia)
    
    # 4. Definir el costo de los arcos
    routing.SetArcCostEvaluatorOfAllVehicles(indice_callback_distancia)
    
    # 5. Configurar los parámetros de búsqueda
    parametros_busqueda = pywrapcp.DefaultRoutingSearchParameters()
    parametros_busqueda.time_limit.seconds = tiempo_limite
    parametros_busqueda.log_search = True
    parametros_busqueda.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    parametros_busqueda.local_search_metaheuristic = metaheuristica
    
    # 6. Resolver el problema
    solucion = routing.SolveWithParameters(parametros_busqueda)
    
    tiempo_ejecucion = time.time() - inicio_tiempo
    
    # 7. Decodificar y procesar la solución
    if solucion:
        print(f"\n¡Solución encontrada con {nombre_metaheuristica}!")
        
        # Extraer el tour de la solución
        tour = []
        indice = routing.Start(0)  # Comenzar desde el depósito del vehículo 0
        
        print("Tour:")
        while not routing.IsEnd(indice):
            nodo = manager.IndexToNode(indice)
            tour.append(nodo + 1)  # +1 para ajustar al formato original (ciudades 1-n)
            print(f"Ciudad {nodo + 1}")
            indice = solucion.Value(routing.NextVar(indice))
        
        # Calcular la distancia total
        tour_dict = {'tour': tour}
        distancia_total = distanciaTour(tour_dict, matriz_distancias)
        
        print(f"\nDistancia total: {distancia_total}")
        print(f"Tiempo de ejecución: {tiempo_ejecucion:.4f} segundos")
        print("*" * 50)
        
        return {
            'exito': True,
            'tour': tour,
            'distancia': distancia_total,
            'tiempo': tiempo_ejecucion,
            'metaheuristica': nombre_metaheuristica
        }
    
    else:
        print(f"\n----- SIN Solución con {nombre_metaheuristica} -----")
        print(f"Tiempo de ejecución: {tiempo_ejecucion:.4f} segundos")
        print("*" * 50)
        
        return {
            'exito': False,
            'tour': [],
            'distancia': float('inf'),
            'tiempo': tiempo_ejecucion,
            'metaheuristica': nombre_metaheuristica
        }

def ejecutar_tsp_ortools(archivo_instancia: str) -> Dict:
    """
    Ejecuta TSP con OR-Tools probando diferentes metaheurísticas.
    
    Args:
        archivo_instancia: Ruta al archivo de la instancia TSP
        
    Returns:
        Diccionario con el mejor resultado encontrado
    """
    
    print("=" * 60)
    print("TSP CON OR-TOOLS - METAHEURÍSTICAS")
    print("=" * 60)
    
    # Definir las metaheurísticas a probar
    metaheuristicas = {
        "GREEDY_DESCENT": routing_enums_pb2.LocalSearchMetaheuristic.GREEDY_DESCENT,
        "GUIDED_LOCAL_SEARCH": routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH,
        "TABU_SEARCH": routing_enums_pb2.LocalSearchMetaheuristic.TABU_SEARCH,
        "SIMULATED_ANNEALING": routing_enums_pb2.LocalSearchMetaheuristic.SIMULATED_ANNEALING,
    }
    
    resultados = {}
    mejor_resultado = None
    mejor_distancia = float('inf')
    
    # Probar cada metaheurística
    for nombre, metodo in metaheuristicas.items():
        try:
            resultado = resolver_tsp_metaheuristicas(
                archivo_instancia,
                metodo,
                nombre,
                10  # 10 segundos por metaheurística
            )
            
            resultados[nombre] = resultado
            
            # Actualizar mejor resultado
            if resultado['exito'] and resultado['distancia'] < mejor_distancia:
                mejor_distancia = resultado['distancia']
                mejor_resultado = resultado.copy()
                
        except Exception as e:
            print(f"Error ejecutando {nombre}: {e}")
            resultados[nombre] = {
                'exito': False,
                'error': str(e),
                'metaheuristica': nombre
            }
    
    # Mostrar resumen de resultados
    print("\n" + "=" * 60)
    print("RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    # Filtrar resultados exitosos y ordenar por distancia
    resultados_exitosos = {k: v for k, v in resultados.items() if v.get('exito', False)}
    
    if resultados_exitosos:
        resultados_ordenados = sorted(
            resultados_exitosos.items(), 
            key=lambda x: x[1]['distancia']
        )
        
        print(f"{'Rank':<4} {'Metaheurística':<20} {'Distancia':<12} {'Tiempo':<10}")
        print("-" * 50)
        
        for i, (nombre, resultado) in enumerate(resultados_ordenados, 1):
            print(f"{i:<4} {nombre:<20} {resultado['distancia']:<12} {resultado['tiempo']:<10.4f}")
        
        if mejor_resultado:
            print(f"\n🏆 MEJOR RESULTADO:")
            print(f"   Metaheurística: {mejor_resultado['metaheuristica']}")
            print(f"   Distancia: {mejor_resultado['distancia']}")
            print(f"   Tiempo: {mejor_resultado['tiempo']:.4f} segundos")
    else:
        print("No se encontraron soluciones exitosas.")
    
    # Agregar todos los resultados al mejor resultado para las gráficas
    resultado_final = mejor_resultado.copy() if mejor_resultado else {
        'exito': False,
        'distancia': float('inf'),
        'tiempo': 0,
        'metaheuristica': 'Ninguna'
    }
    
    # Incluir todos los resultados para las gráficas
    resultado_final['todos_resultados'] = resultados
    
    return resultado_final 