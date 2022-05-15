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
from time import sleep

longMax = 10   #Aquí puede escribir el número máximo de valores producidos por los 
              #productores que desee
NPROD = 5     #Aquí puede escribir el número máximo de productores que desee


def delay(factor = 3):
    sleep(3/factor)

#FUNCIÓN AUXILIAR PARA EL PRODUCTOR
def anadir_almacen(almacen, pid, valor, mutex):
    mutex.acquire()
    try:
        almacen[pid] = valor
        delay(30)
    finally:
        mutex.release()

#################################  FUNCIÓN PRODUCTOR  #################################
def productor(pid, almacen, empty, nonEmpty, long, mutex):
    valor = 0
    for i in range(long):
        valor += random.randint(0,20)
        empty.acquire()
        anadir_almacen(almacen, pid, valor, mutex)
        print (f"El {current_process().name} ha producido un {valor}")
        nonEmpty.release()                                                           
    empty.acquire()
    anadir_almacen(almacen, pid, -1, mutex)
    nonEmpty.release()

#FUNCIÓN AUXILIAR PARA EL CONSUMIDOR: Determina la posición que ocupa el mínimo de
#los valores que se encuentran en el almacén
def posicion_del_minimo(almacen, mutex):
    mutex.acquire()
    try:
        minimo = 1000000
        pos_min = 0
        pos_aux = 0
        for num in almacen:
            if (num < minimo) and (num != -1):
                minimo = num
                pos_min = pos_aux
            pos_aux += 1
    finally:
        mutex.release()
    return pos_min

def anadir_valor_almacen(resultado, almacen, posicion, mutex):
    mutex.acquire()
    try:
        resultado.append(almacen[posicion])
    finally:
        mutex.release()        

#################################  FUNCIÓN CONSUMIDOR  #################################
def consumidor(resultado, almacen, empty, nonEmpty, mutex):
    for sem in nonEmpty:
        sem.acquire()
    while True:
        pos_min = posicion_del_minimo(almacen, mutex)
        if almacen[pos_min] != -1:
            anadir_valor_almacen(resultado, almacen, pos_min, mutex)
            empty[pos_min].release()
            #print(resultado[:])
            nonEmpty[pos_min].acquire()
            delay()
        else:
            break
    print("La lista ordenada es:", resultado[:])

def main():
    almacen = Array('i', NPROD)
    for i in range(NPROD):
        almacen[i] = -1
        
    longitudes = []
    for i in range(NPROD):
        long = random.randint(1, longMax)
        longitudes.append(long)

    empty = []
    nonEmpty = []
    for i in range(NPROD):
        empty.append(Semaphore())
        nonEmpty.append(Semaphore())

    mutex = Lock()
    
    prodlst = [Process(target = productor,
                       name = f'productor {i}',
                       args = (i, almacen, empty[i], nonEmpty[i], longitudes[i] , mutex))
               for i in range(NPROD)]

    cons = [Process(target = consumidor,
                    name = "consumidor",
                    args = ([], almacen, empty, nonEmpty, mutex))]
    
    for p in prodlst + cons:
        p.start()

    for p in prodlst + cons:
        p.join()
    
if __name__ == '__main__':
    main()
    