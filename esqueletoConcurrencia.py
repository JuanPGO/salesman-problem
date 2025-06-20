import random 
import time
from time import perf_counter
import multiprocessing as mp
from generales.codificacionVecindarios import *
import pprint

#¡ trabajar dos funciones y que se ejecuten a la vez
def computo1(lista_compartida,parametro):

    #?Simular carga de cómputo
    tiempo_computo = random.randint(1,5)
    time.sleep(tiempo_computo)
    numeroGenerado = random.randint(1,1000)

    #¡ No es la mejor idea realizar salidas en pantalla cuando de realiza concurrencia

    #? Reportar desde la heurística
    print(f"Carga Computacional -> {tiempo_computo}, NGenerado -> {numeroGenerado}")

    #? Escribir en una memoria común (resultado obtenido)
    lista_compartida.append(('Computo1',numeroGenerado))


def computo2(lista_compartida,parametro):

    #?Simular carga de cómputo
    tiempo_computo = random.randint(1,5)
    time.sleep(tiempo_computo)
    numeroGenerado = random.randint(1,1000)

    #¡ No es la mejor idea realizar salidas en pantalla cuando de realiza concurrencia

    #? Reportar desde la heurística
    print(f"Carga Computacional -> {tiempo_computo}, NGenerado -> {numeroGenerado}")

    #? Escribir en una memoria común (resultado obtenido)
    lista_compartida.append(('Computo2',numeroGenerado))

def estrategia_paralelo():

    #? Instanciar el administrador de procesos
    manager = mp.Manager()
    #? Creamos una o varias memorias compartidas
    lista_compartida = manager.list()

    #? Colección de procesos
    procesos = [
        mp.Process(target=computo1,args=(lista_compartida,1)),
        mp.Process(target=computo2,args=(lista_compartida,2))
    ]

    tiempo_inicial = perf_counter()

    #? Generar los hilos
    for proceso in procesos:
        proceso.start()

    #? Reunir los hilos
    for proceso in procesos:
        proceso.join()

    tiempo_final = perf_counter()
    tiempo_total = tiempo_final - tiempo_inicial

    print(f"Tiempo total transcurrido -> {tiempo_total}")
    
    return list(lista_compartida)    


########### VENCINDARIOS ###########

def generar_vecindario_swap(lista_compartida, s_i):
    vecinos = swap1(s_i)
    vecindario_Ampliado = ampliar_vencindario(vecinos)
    vecindario_Ampliado.sort(key=lambda v:v['fo'])

    lista_compartida.append(('swap', vecindario_Ampliado[0]))

def generar_vecindario_insert_derecha(lista_compartida, s_i):
    vecinos = insert_derecha(s_i)
    vecindario_Ampliado = ampliar_vencindario(vecinos)
    vecindario_Ampliado.sort(key=lambda v:v['fo'])

    lista_compartida.append(('insert_derecha', vecindario_Ampliado[0]))

def generar_vecindario_insert_izquierda(lista_compartida, s_i):
    vecinos = insert_izquierda(s_i)
    vecindario_Ampliado = ampliar_vencindario(vecinos)
    vecindario_Ampliado.sort(key=lambda v:v['fo'])
    lista_compartida.append(('insert_izquierda', vecindario_Ampliado[0]))    

def generar_vecindario_2opt(lista_compartida, s_i):
    vecinos = two_opt(s_i)
    vecindario_Ampliado = ampliar_vencindario(vecinos)
    vecindario_Ampliado.sort(key=lambda v:v['fo'])
    lista_compartida.append(('2opt', vecindario_Ampliado[0]))


def vecinos_concurrentes(s_i:list):

    #? Instanciar el administrador de procesos
    manager = mp.Manager()
    #? Creamos una o varias memorias compartidas
    lista_compartida = manager.list()

    #? Colección de procesos
    procesos = [
        mp.Process(target=generar_vecindario_swap,args=(lista_compartida,s_i)),
        mp.Process(target=generar_vecindario_insert_derecha,args=(lista_compartida,s_i)),
        mp.Process(target=generar_vecindario_insert_izquierda,args=(lista_compartida,s_i)),
        mp.Process(target=generar_vecindario_2opt,args=(lista_compartida,s_i)),
    ]

    tiempo_inicio = perf_counter()

    for p in procesos:
        p.start()# inicia cada proceso

    for p in procesos:
        p.join() # espera a que cada proceso termine para continuar la ejecucion general

    tiempo_fin = perf_counter()

    tiempo_ejecucion = tiempo_fin-tiempo_inicio

    print(f"Tiempo total transcurrido -> {tiempo_ejecucion}")

    return list(lista_compartida)

########### SECCION PRINCIPAL ###########

# if __name__ == '__main__':
#     #resultado = estrategia_paralelo()
#     resultado = vecinos_concurrentes(s_0)
#     print("-----------------------")
#     for operacion, datos in resultado:
#         print(f"Operación: {operacion}")
#         print(f"  fo: {datos['fo']}")
#         print(f"  s_i: {datos['s_i']}")
#         print("-----------------------\n")