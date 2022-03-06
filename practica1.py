########################################################################################
########################################################################################
###############            PRÁCTICA 1 - PROGRAMACIÓN PARALELA            ###############
###############                   Claudia Viñas Jáñez                    ###############
########################################################################################
########################################################################################

from multiprocessing import Process
from multiprocessing import Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
import random

longMax = 4   #Aquí puede escribir el número máximo de valores producidos por los 
              #productores que desee
NPROD = 3     #Aquí puede escribir el número máximo de productores que desee

#FUNCIÓN AUXILIAR PARA EL PRODUCTOR
def anadir_almacen(almacen, pid, valor, mutex):
    mutex.acquire()
    try:
        almacen[pid] = valor 
    finally:
        mutex.release()

#################################  FUNCIÓN PRODUCTOR  #################################
def productor(pid, almacen, empty, nonEmpty, long, mutex):
    valor = 0
    for i in range(long):
        empty.acquire()
        valor += random.randint(0,5)
        print (f"El {current_process().name} ha producido un {valor}")
        anadir_almacen(almacen, pid, valor, mutex)   
        nonEmpty.release()                                                           
    empty.acquire()
    almacen[pid] = -1
    nonEmpty.release()

#FUNCIÓN AUXILIAR PARA EL CONSUMIDOR: Determina la posición que ocupa el mínimo de
#los valores que se encuentran en el almacen
def posicion_del_minimo(almacen, mutex):
    mutex.acquire()
    try:
        pos_min = 0
        minimo = almacen[0]   
        i = 1
        while i < len(almacen):
            if minimo < 0:
                minimo = almacen[i]
                pos_min = i
            i += 1   
        j = 0
        while j < len(almacen):
            if (almacen[j] > -1 and almacen[j] < minimo):
                minimo = almacen[j]
                pos_min = j
            j += 1
    finally:
        mutex.release()
    return pos_min

#FUNCIÓN AUXILIAR PARA EL CONSUMIDOR: Añade un valor a la lista resultado
def anadir_numero(resultado, almacen, pos, indice, numero, mutex):
    mutex.acquire()
    try:
        resultado[indice.value] = numero
        indice.value = indice.value + 1
        almacen[pos] = -3
    finally:
        mutex.release()
    
#################################  FUNCIÓN CONSUMIDOR  #################################
def consumidor(resultado, indice, almacen, empty, nonEmpty, mutex):
    while (-2 in almacen):
        for i in range(NPROD):
            nonEmpty[i].acquire()
    while (-10 in resultado):
        while (-3 in almacen):
            for i in range(NPROD):
                nonEmpty[i].acquire()
        pos_min = posicion_del_minimo(almacen, mutex)
        anadir_numero(resultado, almacen, pos_min, indice, almacen[pos_min], mutex)
        #print("lista:", resultado[:], "almacen", almacen[:])
        empty[pos_min].release()
        nonEmpty[pos_min].acquire()
    print("La lista ordenada es:", resultado[:])

#FUNCIÓN AUXILIAR: Hace el sumatorio de los elementos de un array
def sumatorio(array):
    sumat = 0
    i = 0
    while i < len(array):
        sumat += array[i]
        i += 1
    return sumat

def main():
    almacen = Array('i', NPROD)
    indice = Value('i', 0)
    long = Array('i', NPROD)
    for i in range(NPROD):
        long[i] = random.randint(1, longMax)
        almacen[i] = -2
        
    K = sumatorio(long)
    resultado = Array('i', K)
    
    for i in range(K):
        resultado[i] = -10

    empty = []
    nonEmpty = []
    for i in range(NPROD):
        empty.append(Semaphore())
        nonEmpty.append(Semaphore())
        
    mutex = Lock()
    
    prodlst = [Process(target = productor,
                        name = f'productor {i}',
                        args = (i, almacen, empty[i], nonEmpty[i], long[i], mutex))
                for i in range(NPROD)]

    cons = [Process(target = consumidor,
                      name = "consumidor",
                      args = (resultado, indice, almacen, empty, nonEmpty, mutex))]
    
    for p in prodlst + cons:
        p.start()

    for p in prodlst + cons:
        p.join()
    
if __name__ == '__main__':
    main()