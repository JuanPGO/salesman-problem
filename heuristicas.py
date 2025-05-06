from leerInformacion import cargarCaso
from matrizDistancias import matrizEuclidiana

caso = cargarCaso("data/wi29.tsp")
matriz = matrizEuclidiana(caso)

def heuristicaVecinoMasCercano(caso:dict, matriz:list) -> dict:
    tour = []
    for i in range(caso['dimension']):
        # Inicializar el tour con la primera ciudad
        # Obtener la ciudad actual
        tour.append(caso['coordenadas'][i]['id'])
        for j in range(caso['dimension']-1):
            # Obtener la ciudad más cercana
            distancia_minima = min(matriz[i][j])
            


