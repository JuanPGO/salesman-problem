import pprint as pp
from leerInformacion import cargarCaso
from leerTour import cargarTour



def distanciaEu(caso:dict)->list:

    distancias = []
    todasLasDistancias = [] 

    for i in range(10):
        for j in range(10):
            if i != j:
                distancias.append(round((caso["coordenadas"][j]["latitud"] - caso["coordenadas"][i]["latitud"])**2 + (caso["coordenadas"][j]["longitud"] - caso["coordenadas"][i]["longitud"])**2)**0.5)
        todasLasDistancias.append(distancias)
        distancias = []
    
    return todasLasDistancias

caso = cargarCaso("data/eg7146.tsp")
distancias = distanciaEu(caso)
pp.pprint(distancias)


tour = cargarTour("data/eg7146.tour.txt")


def distanciaTour(caso:dict,tour:list) -> float:
    distanciaTour = []
    for i in range(len(tour['tour'])):
        indiceI = tour['tour'][i]
        indiceJ = tour['tour'][i+1]
        if indiceI == 1:
            indiceI = 0
            distanciaTour.append(distancias[indiceI][indiceJ])
        elif indiceJ == 1:
            indiceJ = 0
            distanciaTour.append(distancias[indiceI][indiceJ])
        elif indiceI == 1 and indiceJ == 1:
            indiceI = 0
            indiceJ = 0
            distanciaTour.append(distancias[indiceI][indiceJ])
        else:
            distanciaTour.append(distancias[indiceI][indiceJ])
    
    return sum(distanciaTour)

distanciaTourEgipto = distanciaTour(caso,tour)
print("La distancia total del tour es: ",distanciaTourEgipto)
