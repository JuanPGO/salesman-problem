from leerInformacion import cargarCaso
def distanciaEu(caso:dict)->list:
    distancia = round((caso["coordenadas"][1]["latitud"] - caso["coordenadas"][0]["latitud"])**2 + (caso["coordenadas"][1]["longitud"] - caso["coordenadas"][0]["longitud"])**2)**0.5
    return distancia

caso = cargarCaso("data/wi29.tsp")

distancia = distanciaEu(caso)
print(distancia)