from leerInformacion import cargarCaso
from matrizDistancias import matrizEuclidiana, distanciaTour
from codificacionVecindarios import *
import math
import networkx as nx
import numpy as np

caso = cargarCaso("data/wi29.tsp")
matriz = matrizEuclidiana(caso)

def heuristicaVecinoMasCercano(caso:dict, matriz:list) -> dict:
    # Inicializar el resultado en formato similar a cargarTour
    resultado = {
        'dimension': caso['dimension'],
        'tour': []
    }
    
    # Ciudad inicial (podemos empezar desde cualquier ciudad, usaré la 0)
    ciudad_inicial = 0
    ciudad_actual = ciudad_inicial
    
    # Conjunto de ciudades ya visitadas
    visitadas = set([ciudad_actual])
    
    # Agregar la primera ciudad al tour (los IDs en el tour comienzan en 1, no en 0)
    resultado['tour'].append(caso['coordenadas'][ciudad_actual]['id'])
    
    # Mientras no hayamos visitado todas las ciudades
    while len(visitadas) < caso['dimension']:
        distancia_minima = float('inf')
        siguiente_ciudad = -1
        
        # Buscar la ciudad no visitada más cercana
        for j in range(caso['dimension']):
            if j not in visitadas and matriz[ciudad_actual][j] < distancia_minima:
                distancia_minima = matriz[ciudad_actual][j]
                siguiente_ciudad = j
        
        # Actualizar la ciudad actual y marcarla como visitada
        ciudad_actual = siguiente_ciudad
        visitadas.add(ciudad_actual)
        
        # Agregar la ciudad al tour
        resultado['tour'].append(caso['coordenadas'][ciudad_actual]['id'])
    
    return resultado

# resultado = heuristicaVecinoMasCercano(caso, matriz)
# distancia = distanciaTour(resultado, matriz)
# print(resultado)
# print(distancia)


def heuristicaInsercionMasCercana(caso:dict, matriz:list) -> dict:
   # Inicializar el resultado
    resultado = {
        'dimension': caso['dimension'],
        'tour': []
    }
    
    # Si no hay ciudades, devolver un tour vacío
    if caso['dimension'] == 0:
        return resultado
    
    # Encontrar las dos ciudades iniciales más cercanas entre sí
    min_dist = float('inf')
    ciudad1, ciudad2 = 0, 1
    
    for i in range(caso['dimension']):
        for j in range(i+1, caso['dimension']):
            if matriz[i][j] < min_dist:
                min_dist = matriz[i][j]
                ciudad1, ciudad2 = i, j
    
    # Iniciar con un subtour de dos ciudades
    subtour = [ciudad1, ciudad2]
    ciudades_restantes = set(range(caso['dimension'])) - set(subtour)
    
    # Mientras queden ciudades por insertar
    while ciudades_restantes:
        # Encontrar la ciudad fuera del tour más cercana a cualquier ciudad del tour
        min_dist = float('inf')
        ciudad_mas_cercana = -1
        ciudad_en_tour = -1
        
        for ciudad_tour in subtour:
            for ciudad_fuera in ciudades_restantes:
                if matriz[ciudad_tour][ciudad_fuera] < min_dist:
                    min_dist = matriz[ciudad_tour][ciudad_fuera]
                    ciudad_mas_cercana = ciudad_fuera
                    ciudad_en_tour = ciudad_tour
        
        # Encontrar la mejor posición para insertar la nueva ciudad
        mejor_posicion = 0
        menor_incremento = float('inf')
        
        for i in range(len(subtour)):
            # Posición de inserción después de subtour[i]
            j = (i + 1) % len(subtour)
            
            # Calcular incremento de distancia al insertar entre i y j
            incremento = matriz[subtour[i]][ciudad_mas_cercana] + matriz[ciudad_mas_cercana][subtour[j]] - matriz[subtour[i]][subtour[j]]
            
            if incremento < menor_incremento:
                menor_incremento = incremento
                mejor_posicion = i + 1
        
        # Insertar la ciudad en la mejor posición
        subtour.insert(mejor_posicion, ciudad_mas_cercana)
        ciudades_restantes.remove(ciudad_mas_cercana)
    
    # Convertir índices de ciudades a IDs reales
    for ciudad in subtour:
        resultado['tour'].append(caso['coordenadas'][ciudad]['id'])
    
    return resultado

# resultado = heuristicaInsercionMasCercana(caso, matriz)
# distancia = distanciaTour(resultado, matriz)
# print(resultado)
# print(distancia)

# vecindario1 = two_opt(resultado['tour'])  
# vecindario1A = ampliar_vencindario(vecindario1,matriz)
# vecindario1A.sort(key=lambda v:v['fo'])
# print(vecindario1A[0])

def heuristicaInsercionMasLejana(caso:dict, matriz:list) -> dict:
    # Inicializar el resultado
    resultado = {
        'dimension': caso['dimension'],
        'tour': []
    }
    
    # Si no hay ciudades, devolver un tour vacío
    if caso['dimension'] == 0:
        return resultado
    
    # Encontrar las dos ciudades iniciales más lejanas entre sí
    max_dist = 0
    ciudad1, ciudad2 = 0, 0
    
    for i in range(caso['dimension']):
        for j in range(caso['dimension']):
            if i != j and matriz[i][j] > max_dist:
                max_dist = matriz[i][j]
                ciudad1, ciudad2 = i, j
    
    # Iniciar con un subtour de dos ciudades
    subtour = [ciudad1, ciudad2]
    ciudades_restantes = set(range(caso['dimension'])) - set(subtour)
    
    # Mientras queden ciudades por insertar
    while ciudades_restantes:
        # Encontrar la ciudad fuera del tour más lejana a cualquier ciudad del tour
        max_dist_min = -1  # Mínima distancia máxima
        ciudad_mas_lejana = -1
        
        for ciudad_fuera in ciudades_restantes:
            # Encontrar la ciudad del tour más cercana a esta ciudad externa
            min_dist = float('inf')
            for ciudad_tour in subtour:
                if matriz[ciudad_tour][ciudad_fuera] < min_dist:
                    min_dist = matriz[ciudad_tour][ciudad_fuera]
            
            # Si esta ciudad es más lejana que las anteriores, la seleccionamos
            if min_dist > max_dist_min:
                max_dist_min = min_dist
                ciudad_mas_lejana = ciudad_fuera
        
        # Encontrar la mejor posición para insertar la nueva ciudad
        mejor_posicion = 0
        menor_incremento = float('inf')
        
        for i in range(len(subtour)):
            # Posición de inserción después de subtour[i]
            j = (i + 1) % len(subtour)
            
            # Calcular incremento de distancia al insertar entre i y j
            incremento = matriz[subtour[i]][ciudad_mas_lejana] + matriz[ciudad_mas_lejana][subtour[j]] - matriz[subtour[i]][subtour[j]]
            
            if incremento < menor_incremento:
                menor_incremento = incremento
                mejor_posicion = i + 1
        
        # Insertar la ciudad en la mejor posición
        subtour.insert(mejor_posicion, ciudad_mas_lejana)
        ciudades_restantes.remove(ciudad_mas_lejana)
    
    # Convertir índices de ciudades a IDs reales
    for ciudad in subtour:
        resultado['tour'].append(caso['coordenadas'][ciudad]['id'])
    
    return resultado

def heuristicaSavings(caso:dict, matriz:list) -> dict:
    """
    Implementa la heurística de ahorros (Clarke & Wright Savings Algorithm)
    para resolver el problema del viajante de comercio.
    """
    # Inicializar el resultado
    resultado = {
        'dimension': caso['dimension'],
        'tour': []
    }
    
    n = caso['dimension']
    if n <= 1:
        if n == 1:
            resultado['tour'] = [caso['coordenadas'][0]['id']]
        return resultado
    
    # Elegir un depósito (nodo de referencia), usualmente se elige el nodo 0
    deposito = 0
    
    # Inicializar rutas desde el depósito a cada ciudad y de vuelta
    rutas = []
    for i in range(n):
        if i != deposito:
            # Ruta: deposito -> ciudad i -> deposito
            rutas.append([deposito, i, deposito])
    
    # Calcular ahorros para cada par de ciudades
    ahorros = []
    for i in range(n):
        if i != deposito:
            for j in range(i+1, n):
                if j != deposito:
                    # Ahorro = dist(deposito,i) + dist(j,deposito) - dist(i,j)
                    ahorro = matriz[deposito][i] + matriz[j][deposito] - matriz[i][j]
                    ahorros.append((ahorro, i, j))
    
    # Ordenar ahorros de mayor a menor
    ahorros.sort(reverse=True)
    
    # Proceso de unión de rutas
    for ahorro, i, j in ahorros:
        # Buscar las rutas que contienen las ciudades i y j
        ruta_i = None
        ruta_j = None
        indice_i = -1
        indice_j = -1
        
        for idx, ruta in enumerate(rutas):
            if i in ruta:
                ruta_i = ruta
                indice_i = idx
            if j in ruta:
                ruta_j = ruta
                indice_j = idx
        
        # Si ambas rutas existen y son diferentes
        if ruta_i and ruta_j and indice_i != indice_j:
            # Comprobar si i es extremo en su ruta (no es el depósito ni está en medio)
            if ruta_i[1] == i and len(ruta_i) > 3:  # i está al inicio
                ruta_i.pop(0)  # Eliminar depósito del inicio
            elif ruta_i[-2] == i and len(ruta_i) > 3:  # i está al final
                ruta_i.pop(-1)  # Eliminar depósito del final
            else:
                continue  # i está en medio, no se puede unir
            
            # Comprobar si j es extremo en su ruta
            if ruta_j[1] == j and len(ruta_j) > 3:  # j está al inicio
                ruta_j.pop(0)
                nueva_ruta = [deposito] + ruta_j + ruta_i[1:]
            elif ruta_j[-2] == j and len(ruta_j) > 3:  # j está al final
                ruta_j.pop(-1)
                nueva_ruta = [deposito] + ruta_i[1:] + ruta_j[1:]
            else:
                continue  # j está en medio, no se puede unir
            
            # Eliminar rutas originales y agregar la nueva
            rutas.pop(max(indice_i, indice_j))
            rutas.pop(min(indice_i, indice_j))
            rutas.append(nueva_ruta)
    
    # Si quedan múltiples rutas, las unimos de alguna forma simple
    while len(rutas) > 1:
        # Unir las dos primeras rutas
        ruta1 = rutas.pop(0)
        ruta2 = rutas.pop(0)
        # Eliminar depósitos redundantes
        if len(ruta1) > 3:
            ruta1.pop(-1)  # Eliminar depósito del final
        if len(ruta2) > 3:
            ruta2.pop(0)  # Eliminar depósito del inicio
        # Combinar rutas
        nueva_ruta = ruta1 + ruta2[1:]
        rutas.insert(0, nueva_ruta)
    
    # Construir el tour final
    if rutas:
        # Eliminar depósitos redundantes (sólo debe aparecer una vez al inicio)
        tour = rutas[0][:-1]  # Eliminar el último depósito
        
        # Convertir índices de ciudades a IDs reales
        for ciudad in tour:
            if ciudad < len(caso['coordenadas']):
                resultado['tour'].append(caso['coordenadas'][ciudad]['id'])
    
    return resultado

def heuristicaChristofides(caso:dict, matriz:list) -> dict:
    """
    Implementa la heurística de Christofides para resolver el TSP.
    Esta heurística garantiza un tour a lo sumo 1.5 veces el óptimo para instancias métricas.
    """
    # Inicializar el resultado
    resultado = {
        'dimension': caso['dimension'],
        'tour': []
    }
    
    n = caso['dimension']
    if n <= 1:
        if n == 1:
            resultado['tour'] = [caso['coordenadas'][0]['id']]
        return resultado
    
    # 1. Crear un grafo completo donde los nodos son las ciudades y los pesos de las aristas son las distancias
    G = nx.Graph()
    for i in range(n):
        for j in range(i+1, n):
            G.add_edge(i, j, weight=matriz[i][j])
    
    # 2. Encontrar un árbol de expansión mínima (MST)
    mst = nx.minimum_spanning_tree(G, algorithm='kruskal')
    
    # 3. Encontrar nodos de grado impar en el MST
    nodos_impares = [node for node, degree in mst.degree() if degree % 2 == 1]
    
    # 4. Encontrar emparejamiento perfecto de costo mínimo en el subgrafo inducido por los nodos impares
    # Crear un subgrafo completo con los nodos impares
    H = nx.Graph()
    for i in range(len(nodos_impares)):
        for j in range(i+1, len(nodos_impares)):
            u, v = nodos_impares[i], nodos_impares[j]
            H.add_edge(u, v, weight=-matriz[u][v])  # Negativo porque nx.max_weight_matching maximiza
    
    # Encontrar el emparejamiento de peso máximo (que corresponde al de costo mínimo por el negativo)
    emparejamiento = nx.algorithms.matching.max_weight_matching(H, maxcardinality=True)
    
    # 5. Combinar el MST con el emparejamiento para formar un grafo donde todos los nodos tienen grado par
    multigraph = nx.MultiGraph(mst)
    for u, v in emparejamiento:
        multigraph.add_edge(u, v, weight=matriz[u][v])
    
    # 6. Encontrar un circuito euleriano en el multigrafo
    circuito_euleriano = list(nx.eulerian_circuit(multigraph, source=0))
    
    # 7. Transformar el circuito euleriano en un tour hamiltoniano (eliminando visitas repetidas)
    tour = []
    visitados = set()
    
    for u, v in circuito_euleriano:
        if u not in visitados:
            tour.append(u)
            visitados.add(u)
    
    # Añadir el nodo final si es necesario para completar el ciclo
    if tour[0] != tour[-1]:
        tour.append(tour[0])
    
    # Convertir índices de ciudades a IDs reales (los IDs en el tour comienzan en 1)
    for ciudad in tour:
        resultado['tour'].append(caso['coordenadas'][ciudad]['id'])
    
    return resultado
