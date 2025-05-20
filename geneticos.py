from leerInformacion import cargarCaso
from matrizDistancias import matrizEuclidiana, distanciaTour
from codificacionVecindarios import *
from heuristicas import *
from esqueletoConcurrencia import *
from pprint import pprint

caso = cargarCaso("data/uy734.tsp")
matrizCaso = matrizEuclidiana(caso)

def generarPoblacion(caso:dict, matriz:list) -> dict:

    poblacion = []
    
    vecinoMasCercano = heuristicaVecinoMasCercano(caso, matriz)
    InsercionMasCercana = heuristicaInsercionMasCercana(caso, matriz)

    individuo1={
        'tour': vecinoMasCercano['tour'],
        'fo' : distanciaTour(vecinoMasCercano,matriz)
    }
    
    individuo2={
            'tour': InsercionMasCercana['tour'],
            'fo' : distanciaTour(InsercionMasCercana,matriz)
        }

    poblacion.append(individuo1)  
    poblacion.append(individuo2)


    vecindarioMasCercano = vecinos_concurrentes(individuo1['tour'],matriz)
    for operacion, datos in vecindarioMasCercano:
        # print(f"vecindario {operacion}")
        # print(datos)
        individuo = {
            'tour': datos['s_i'],
            'fo': datos['fo']
        }
        poblacion.append(individuo)

    vecindarioMasCercano = vecinos_concurrentes(individuo2['tour'],matriz)
    for operacion, datos in vecindarioMasCercano:
        # print(f"vecindario {operacion}")
        # print(datos)
        individuo = {
            'tour': datos['s_i'],
            'fo': datos['fo']
        }
        poblacion.append(individuo)


    return poblacion

if __name__ == "__main__":
    poblacion = generarPoblacion(caso, matrizCaso)

    print("POBLACION")
    for individuo in poblacion:
        print(f"FO: {individuo['fo']}")
        print(f"Tour: {individuo['tour']}")

    



