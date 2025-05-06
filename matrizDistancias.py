import pprint as pp
from leerInformacion import cargarCaso
from leerTour import cargarTour

def matrizEuclidiana(caso:dict)->list:
    """
    Calcula la matriz de distancias euclidianas entre todas las ciudades.
    Según la especificación TSPLIB para EUC_2D:
    1. Las distancias se calculan en el espacio euclidiano 2D
    2. Se redondea al entero más cercano (nint)
    """
    todasLasDistancias = []
    for i in range(caso["dimension"]):
        distancias = []
        for j in range(caso["dimension"]):
            if i != j:
                # Cálculo de distancia euclidiana según EUC_2D de TSPLIB
                dx = caso["coordenadas"][i]["x"] - caso["coordenadas"][j]["x"]
                dy = caso["coordenadas"][i]["y"] - caso["coordenadas"][j]["y"]
                distancia = round(((dx*dx) + (dy*dy))**0.5)
                distancias.append(distancia)
            else:
                distancias.append(0)  # Distancia a sí mismo es 0
        todasLasDistancias.append(distancias)
    
    return todasLasDistancias

def distanciaTour(tour:dict, distancias:list) -> int:
    """
    Calcula la distancia total de un tour dado usando la matriz de distancias.
    """
    longitud_tour = 0
    
    # Recorrer el tour y sumar las distancias
    for i in range(len(tour['tour'])-1):
        # Restar uno para ajustar con los índices que comienzan en 0
        indiceA = tour['tour'][i] - 1
        indiceB = tour['tour'][i+1] - 1
        
        longitud_tour += distancias[indiceA][indiceB]
    
    # Agregar la distancia de retorno al punto inicial (cerrar el ciclo)
    indiceNodoFinal = tour['tour'][-1] - 1
    indiceNodoInicial = tour['tour'][0] - 1
    
    longitud_tour += distancias[indiceNodoFinal][indiceNodoInicial]
    
    return longitud_tour

# Cargar el caso de prueba
# caso = cargarCaso("data/wi29.tsp")
# Calcular la matriz de distancias
# distancias = matrizEuclidiana(caso)
# Cargar el tour de referencia
# tour = cargarTour("data/wi29.tour.txt")

# Imprimir información para depuración
# print(f"Dimensión del caso: {caso['dimension']}")
# print(f"Tour dimension: {tour['dimension']}")
# print(f"Longitud del tour: {len(tour['tour'])}")

# Calcular la distancia total del tour
# distanciaTourEgipto = distanciaTour(tour, distancias)
# print("Usando la matriz de distancias")
# print("La distancia total del tour es:", distanciaTourEgipto)



