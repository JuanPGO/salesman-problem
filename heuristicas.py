from leerInformacion import cargarCaso
from matrizDistancias import matrizEuclidiana, distanciaTour
from codificacionVecindarios import *

caso = cargarCaso("data/gr9882.tsp")
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

resultado = heuristicaInsercionMasCercana(caso, matriz)
distancia = distanciaTour(resultado, matriz)
print(resultado)
print(distancia)

vecindario1 = two_opt(resultado['tour'])  
vecindario1A = ampliar_vencindario(vecindario1,matriz)
vecindario1A.sort(key=lambda v:v['fo'])
print(vecindario1A[0])
