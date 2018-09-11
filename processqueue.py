import os
from multiprocessing import Process, Queue
from threading import Thread
from random import random
import time

def timer():
    time.sleep(4)

def shuffler(shuffle_list, shuffle_queue, shuffle_response):
    i = 0;
    while i<len(shuffle_list):

        shuffle_queue.put(shuffle_list[i])

        while True:

            res = shuffle_response.get()
            if res is not None and res == shuffle_list[i]:
                break

        time.sleep(0.5)
        i += 1
        if i == len(shuffle_list):
            i = 0

    # end function

def worker(name, numb, shuffle_queue, shuffle_response, queue, info):
    location = 0
    ime = "-".join([name,str(numb)])
    while True:

        red = shuffle_queue.get()

        if red is not None:

            if red != ime:
                shuffle_queue.put(red)
                time.sleep(0.5)
                continue

            shuffle_response.put(ime)
            print ("Proces {0} ima znacku!".format(ime))
            msg = info.get()
            if msg is not None:
                print ("Proces {0} prima poruku {1}".format(ime, msg))
                if "-".join([name, str(location)]) != msg:
                    print ("Proces {0} vraca poruku nazad u red poruka".format(ime))
                    info.put(msg)
                    time.sleep(random()/2)
                    continue

                queue.put(ime)
                location = 1 - location
                time.sleep(1)
                continue
            else:
                time.sleep(random()/2)
                continue
        else:
            time.sleep(random()/3)
            continue

def get_passenger(queue, info, name):
    info.put(name)

    passenger = ''

    while True:
        passenger = queue.get()
        if passenger is not None:
            break
        else:
            time.sleep(0.01)
            continue

    print ("Proces {} ulazi u brod".format(passenger))
    return passenger

def boat(k, m):
    print ("Stvoren proces camac")
    print ("------------------------------------------------")
    print ("Pocetna lokacija je lijeva obala")
    print ("------------------------------------------------")
    workers = {0:{'kanibal':[],'misionar':[]}, 1:{'kanibal':[],'misionar':[]}}
    info = Queue()
    queue = Queue()
    shuffle_queue = Queue()
    shuffle_response = Queue()
    shuffle_list = []
    location = 0

    for i in range(k):
        name = "kanibal-{0}".format(i)
        work = Process(target=worker, args=("kanibal", i, shuffle_queue, shuffle_response, queue, info))
        work.daemon = True
        work.start()
        workers[0]["kanibal"].append(name)
        shuffle_list.append(name)
        print("Proces camac stvara proces {0}".format(name))

    for i in range(m):
        name = "misionar-{0}".format(i)
        work = Process(target=worker, args=("misionar", i, shuffle_queue, shuffle_response, queue, info))
        work.daemon = True
        work.start()
        workers[0]["misionar"].append(name)
        shuffle_list.append(name)
        print("Proces camac stvara proces {0}".format(name))

    #start shuffler
    shuff = Process(target=shuffler, args=(shuffle_list, shuffle_queue, shuffle_response))
    shuff.daemon = True
    shuff.start()

    while True:
        passengers = []
        tp = Thread(target=timer)
        tp.daemon = True
        tp.start()
        if location == 0:
            name = get_passenger(queue, info, "kanibal-0")
            passengers.append(name)
            workers[0]['kanibal'].remove(name)

            if len(workers[0]['kanibal'])>0:
                for i in range(min(2, len(workers[0]['kanibal']))):
                    name = get_passenger(queue, info, "kanibal-0")
                    passengers.append(name)
                    workers[0]['kanibal'].remove(name)
            else:
                for i in range(min(2, len(workers[0]['misionar']))):
                    name = get_passenger(queue, info, "misionar-0")
                    passengers.append(name)
                    workers[0]['misionar'].remove(name)
        else:
            if len(workers[0]['kanibal']) != 0 or len(workers[0]['misionar']) != 0:
                name = get_passenger(queue, info, "kanibal-1")
                workers[1]['kanibal'].remove(name)
                passengers.append(name)
        if (len(passengers) == 3):
            print ("Brod je pun")

        tp.join()
        if len(passengers) == 0:
            print ("Nitko se nije ukrcao na brod nakon 4 sekunde, proces brod se zaustavlja")
            break

        print ("------------------------------------------------")
        print ("Rijeku prelaze: {0}".format(', '.join(passengers)))
        print ("------------------------------------------------")
        location = 1 - location
        lokacija = 'desna obala' if location == 1 else 'lijeva obala'
        print ("Nova lokacija je {0}".format(lokacija))
        print ("------------------------------------------------")
        for x in passengers:
            if x.startswith('misionar'):
                workers[location]["misionar"].append(x)
            else:
                workers[location]["kanibal"].append(x)


if __name__=='__main__':

    kanibal = int(input("Unesi broj kanibala: "))
    misionar = int(input ("Unesi broj misionara: "))

    p = Process(target=boat, args=(kanibal, misionar))

    p.start()
    p.join()
