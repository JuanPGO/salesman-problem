# Librerías
import time
import random
import pprint as pp
from typing import List, Dict
from copy import copy, deepcopy

# Añadir un diccionario global para almacenar distancias pre-calculadas
distancias_cache = {}

# Limpiar el caché si necesitamos liberar memoria
def limpiar_cache_distancias():
    global distancias_cache
    distancias_cache.clear()

# Cómo decodificarla:
"""
s_0 -> |heurística best_fit| -> fo (número de contenedores) 
"""


######### FUNCIONES VECINDARIOS #########

#Vecindarios intercambiando elementos adyacentes
def swap1(s_i:list)->List[list]:
    #Inicializar vecindario
    vecindario = []
    for i in range(len(s_i)-1):
        # Copia desligada del vecino
        nuevo_vecino = copy(s_i)

        #intercambiar elemento actual por su adyacente
        indice_auxiliar = nuevo_vecino[i]
        nuevo_vecino[i] = nuevo_vecino[i+1]
        nuevo_vecino[i+1] = indice_auxiliar

        #agregar el nuevo vecino
        vecindario.append(nuevo_vecino)
    return vecindario



def insert_derecha(s_i:list)->List[list]:
    
    #Inicializar vecindario
    vecindario = []
    
    for i in range(len(s_i)):
        for j in range(i+1,len(s_i)):
                
            # Copia desligada del vecino
            nuevo_vecino = copy(s_i)
            
            # Contenido que se va a moover (subíndice de un ítem)
            subindice_item = s_i[i]
            
            # Marcamos el que se pierde
            nuevo_vecino[i] = None
            
            # Realizamos la inserción
            nuevo_vecino.insert(j,subindice_item)
            
            # Filtrar la marca de movimiento
            nuevo_vecino = list(
                filter(
                    lambda x:x is not None,
                    nuevo_vecino
                )
            )
            
            # Incorporar el nuevo vecino en el vecindario evitando repeticiones (búsquedas)
            if nuevo_vecino not in vecindario and nuevo_vecino != s_i:
                vecindario.append(nuevo_vecino)
    
    # Retornar vecindario construido y sin repeticione
    return vecindario




def insert_izquierda(s_i:list)->List[list]:
    
    #Inicializar vecindario
    vecindario = []
    
    for i in range(len(s_i)):
        for j in range(0,i):
                
            # Copia desligada del vecino
            nuevo_vecino = copy(s_i)
            
            # Contenido que se va a moover (subíndice de un ítem)
            subindice_item = s_i[i]
            
            # Marcamos el que se pierde
            nuevo_vecino[i] = None
            
            # Realizamos la inserción
            nuevo_vecino.insert(j,subindice_item)
            
            # Filtrar la marca de movimiento
            nuevo_vecino = list(
                filter(
                    lambda x:x is not None,
                    nuevo_vecino
                )
            )
            
            # Incorporar el nuevo vecino en el vecindario evitando repeticiones (búsquedas)
            if nuevo_vecino not in vecindario and nuevo_vecino != s_i:
                vecindario.append(nuevo_vecino)
    
    # Retornar vecindario construido y sin repeticione
    return vecindario



# Primer vecindario -> swap 2
def swap2(s_i:list)->List[list]:    
    
    #Inicializar vecindario
    vecindario = []
    
    for i in range(len(s_i)):
        for j in range(len(s_i)):
            
            # Primer filtro de repeticiones en el vecindario
            if i != j:
                
                # Copia desligada del vecino
                nuevo_vecino = copy(s_i)
                
                # Intercambiar los elementos
                indice_auxiliar = nuevo_vecino[i]
                nuevo_vecino[i] = nuevo_vecino[j]
                nuevo_vecino[j] = indice_auxiliar
                
                # Incorporar el nuevo vecino en el vecindario
                if nuevo_vecino not in vecindario:
                    vecindario.append(nuevo_vecino)
    
    # Retornar vecindario construido y sin repeticione
    return vecindario



def two_opt(s_i:list)->List[list]:
    """
    Implementación eficiente del vecindario 2-opt.
    Invierte segmentos del tour para eliminar cruces.
    
    Args:
        s_i: Lista de índices que representa el tour actual
        
    Returns:
        Lista de tours vecinos generados mediante 2-opt
    """
    n = len(s_i)
    vecindario = []
    
    # Generar un número limitado de vecinos para instancias grandes
    if n > 100:
        # Para instancias muy grandes, muestrear aleatoriamente
        posiciones = list(range(1, n - 2))
        random.shuffle(posiciones)
        posiciones = posiciones[:min(len(posiciones), 50)]  # Limitar a 50 posiciones
        
        for i in posiciones:
            for j in range(i + 1, min(i + 20, n - 1)):  # Limitar el rango de j
                nuevo_vecino = copy(s_i)
                nuevo_vecino[i:j+1] = reversed(nuevo_vecino[i:j+1])
                
                if nuevo_vecino not in vecindario and nuevo_vecino != s_i:
                    vecindario.append(nuevo_vecino)
    else:
        # Para instancias pequeñas o medianas, generar todos los vecinos
        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                nuevo_vecino = copy(s_i)
                nuevo_vecino[i:j+1] = reversed(nuevo_vecino[i:j+1])
                
                if nuevo_vecino not in vecindario and nuevo_vecino != s_i:
                    vecindario.append(nuevo_vecino)
    
    return vecindario



######### FUNCIONES UTILITARIAS #########

def comparar_vecindarios(vec1, vec2):
    set1 = set(tuple(x) for x in vec1)
    set2 = set(tuple(x) for x in vec2)
    return set1 == set2

# Ampliar el vecindario / calcular la función objetivo o la calidad de cada vecino
def ampliar_vencindario(vecindario:List[list], distancias:list):
    vecindario_Ampliado = []
    for vecino in vecindario:
        vecindario_Ampliado.append({
            's_i': vecino,
            'fo': distanciaTourVecino(vecino, distancias)
        })
    return vecindario_Ampliado

def calcular_clave_tour(tour):
    """
    Genera una clave única para un tour para usarla en el caché de distancias
    """
    # Convertir lista a tupla para que sea hashable
    return tuple(tour)

def distanciaTourVecino(tour:list, distancias:list) -> int:
    """
    Calcula la distancia total de un tour dado usando la matriz de distancias.
    Usa un caché para evitar recalcular distancias ya calculadas.
    """
    global distancias_cache
    
    # Crear clave única para el tour
    clave_tour = calcular_clave_tour(tour)
    
    # Si ya tenemos este tour en caché, retornar la distancia guardada
    if clave_tour in distancias_cache:
        return distancias_cache[clave_tour]
    
    longitud_tour = 0
    
    # Recorrer el tour y sumar las distancias
    for i in range(len(tour)-1):
        # Restar uno para ajustar con los índices que comienzan en 0
        indiceA = tour[i] - 1
        indiceB = tour[i+1] - 1
        
        longitud_tour += distancias[indiceA][indiceB]
    
    # Agregar la distancia de retorno al punto inicial (cerrar el ciclo)
    indiceNodoFinal = tour[-1] - 1
    indiceNodoInicial = tour[0] - 1
    
    longitud_tour += distancias[indiceNodoFinal][indiceNodoInicial]
    
    # Guardar en caché para uso futuro (solo si el caché no es muy grande)
    if len(distancias_cache) < 10000:  # Limitar el tamaño del caché
        distancias_cache[clave_tour] = longitud_tour
    
    return longitud_tour

        

    

