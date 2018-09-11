import os
from multiprocessing import Process, Pipe
from random import random
import time


def filozof(send_pipes, recv_pipes, numb):
    name = "Filozof-{}".format(numb)
    vrijeme = 0

    #  obradi i posalji odgovore za ulazak u KO
    while True:
        time.sleep(random()/2)
        queue = []
        for i in range(len(send_pipes)):
            send_pipes[i].send(("Zahtjev", name, vrijeme))
            broj = i if i < numb else i + 1
            print ('{0} salje zahtjev {1} za ulazak u KO'.format(name, 'Filozof-{}'.format(broj)))
        queue.append((name, vrijeme))


        for i in range(len(recv_pipes)):
            (msg, ime, t) = recv_pipes[i].recv()
            if msg.startswith('Zahtjev'):
                print ("{0} prihvaca zahtjev: {1} od {2} za ulazak u KO".format(name, (ime, t), ime))
                send_pipes[i].send(('Odgovor', name, vrijeme))
                print ("{0} salje odgovor: {1}: {2} ".format(name, ime, (name,vrijeme)))
                if len([x for x in queue if x[0]==ime])==0:
                    queue.append((ime, t))

        for i in range(len(recv_pipes)):
            (msg, ime, t) = recv_pipes[i].recv()
            if msg.startswith('Odgovor'):
                print ("{0} prima odgovor: {1} od {2}".format(name, (ime, t), ime))
                if len([x for x in queue if x[0]==ime])==0:
                    queue.append((ime, t))
                    vrijeme = max(vrijeme, t) + 1

        time.sleep(1.0)
        queue = sorted(queue, key=lambda x: (x[1], x[0]))

        indexes_before = []
        indexes_after = []
        before = True
        for x in queue:
            if (x[0] == name):
                before = False
                continue
            broj =int(x[0].split('-')[1])
            broj = broj if broj < numb else broj - 1
            if before:
                indexes_before.append(broj)
            else:
                indexes_after.append(broj)

        # print ("Indeksi prije {0} - {1}".format(name, indexes_before))
        # print ("Indeksi after {0} - {1}".format(name, indexes_after))

        for i in indexes_before:
            (msg, ime, t) = recv_pipes[i].recv()
            if msg.startswith('Izlazak'):
                queue = [x for x in queue if x[0] != ime]
                print ("{0} primio obavijest o izlasku iz KO od {1}".format(name, ime))
                vrijeme = max(vrijeme, t) + 1

        print ("-------{0} sjeda za stol i filozofira, jede-------".format(name))
        #KO
        pristupi()
        print ("--------{0} je gotov s KO i salje obavijest --------".format(name))

        for x in send_pipes:
            x.send(("Izlazak", name, vrijeme))

        queue = [x for x in queue if x[0] != name]

        for i in indexes_after:
            (msg, ime, t) = recv_pipes[i].recv()
            if msg.startswith('Izlazak'):
                queue = [x for x in queue if x[0] != ime]
                print ("{0} primio obavijest o izlasku iz KO od {1}".format(name, ime))
                vrijeme = max(vrijeme, t) + 1

        print ("{0} gotov".format(name))


    print ('Izasao')

#KO
def pristupi():
    time.sleep(3)

def glavni(broj_filozofa):
    pipes = {}

    for i in range(broj_filozofa):

        for j in range(broj_filozofa):
            if i == j:
                continue
            recv, sender = Pipe()
            pipes[(i, j)] = (recv, sender)
            pipes[(j, i)] = (sender, recv)

    for i in range(broj_filozofa):

        send_pipes = [pipes[(x, i)][1] for x in range(broj_filozofa) if x != i]
        recv_pipe = [pipes[(i, x)][0] for x in range(broj_filozofa) if x != i]

        fil = Process(target=filozof, args=(send_pipes, recv_pipe, i))
        fil.daemon = True
        fil.start()

    while True:
        #do nothing
        a = 1

if __name__ == '__main__':
    filozofi = int(input("Unesi broj filozofa (vise od 2): "))

    if filozofi < 2:
        print ("Potrebno unijeti vise od 2 filozofa!!")
    else:
        glavni(filozofi)
