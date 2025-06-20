import random
import time
import pprint as pp

calcularDistanciaEUC2D = lambda puntoA, puntoB : round(((puntoA[0]-puntoB[0])**2 + (puntoA[1]-puntoB[1])**2)**(0.5))

def leerInstancia(ruta:str)->dict:
    
    instancia = {
        'nombre': str(),
        'dimension': int(),
        'coordenadas': []
    }
    
    
    with open(ruta,"r") as f:
        
        for i,linea in enumerate(f.readlines()):
            
            if i==0:
                instancia['nombre'] = linea.strip().split(":")[1]
            elif i==4:
                instancia['dimension'] = int(linea.strip().split(":")[1])   
            elif i>=7 and i <= instancia['dimension'] + 6:
                instancia['coordenadas'].append(
                    {
                        'id':int(linea.strip().split(" ")[0]),
                        'x':float(linea.strip().split(" ")[1]),
                        'y':float(linea.strip().split(" ")[2])
                            
                    }
                )    
    return instancia

def leerTour(rutaTour:str)->dict:
    tour = {
        'nombre': str(),
        'dimension': int(),
        'tour': []
    }
    
    
    with open(rutaTour,"r") as f:
        
        for i,linea in enumerate(f.readlines()):
            
            if i==0:
                tour['nombre'] = linea.strip().split(":")[1]
            elif i==3:
                tour['dimension'] = int(linea.strip().split(":")[1])   
            elif i>=5 and i <= tour['dimension'] + 4:
                tour['tour'].append(
                    int(linea.strip().split(" ")[0])
                )
    return tour

def calcularFO_Tour(caso:dict,tour:dict)->int:
    longitud_tour = 0
    
    for i in range(len(tour['tour'])-1):
        
        # Restar uno para ajustar con la colección del diccionario caso
        indiceA = tour['tour'][i] - 1
        indiceB = tour['tour'][i+1] - 1
        
        tuplaPunto = lambda indice,caso:(caso['coordenadas'][indice]['x'],caso['coordenadas'][indice]['y'])
        
        distanciaConexion = calcularDistanciaEUC2D(
            tuplaPunto(indiceA,caso),
            tuplaPunto(indiceB,caso),
        )
        longitud_tour += distanciaConexion
    
    # Agregar el retorno al primer nodo
    indiceNodoFinal = tour['tour'][-1] - 1
    indiceNodoInicial = tour['tour'][0] - 1
    
    # # Salida de diagnóstico
    # print(f"Indice nodo final: {indiceNodoFinal}")
    # print(f"Su info en el caso: {caso['coordenadas'][indiceNodoFinal]}")    
    # print(f"Indice nodo inicial: {0}")
    # print(f"Su info en el caso: {caso['coordenadas'][indiceNodoInicial]}")
    
    distanciaRetorno = calcularDistanciaEUC2D(        
            tuplaPunto(indiceNodoFinal,caso),
            tuplaPunto(indiceNodoInicial,caso),
        )   
    longitud_tour += distanciaRetorno    
    
    # Retornar la longitud
    return longitud_tour
    