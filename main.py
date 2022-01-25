"""
@authors	Kardelen Erdal	Berfin Şimşek
Student IDS	2018400024		2018400009

Compiling Status:	Compiling
Working Status:		Working
"""

from mpi4py import MPI
import sys

# initialization of mpi environment
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()


# Tower object which has shape, health, attack point and isAlive fields.
class Tower:
    def __init__(self, shape, health, attack, isAlive):
        self.shape = shape
        self.isalive = isAlive
        if shape == 'o':
            self.health = 6
            self.attack = 1
        elif shape == '+':
            self.health = 8
            self.attack = 2
        else:
            self.health = -1
            self.attack = -1


# prints the shapes of the towers in the matrix


# updates the dead towers in a matrix
def died(data):
    for i in data:
        for k in i:
            if k.health <= 0:
                k.shape = '.'
                k.isalive = False
                k.attack = 0




# updates the main matrix according to the matrices of worker processors
def updatematrix(data, matrix, rank, size, mapsize):
    x = int(mapsize / (size - 1))
    formatrix = x * rank - x

    for i in range(0, x):
        for k in range(0, mapsize):
            matrix[formatrix][k].health = data[i][k].health
            matrix[formatrix][k].isalive = data[i][k].isalive
            matrix[formatrix][k].shape = data[i][k].shape
            matrix[formatrix][k].attack = data[i][k].attack
        formatrix = formatrix + 1


# decreases the health points of towers according to the rules
def attack(data, fromabove=[], frombelow=[]):
    for rows in range(0, len(data)):
        for i in range(len(data[rows])):
            if (data[rows][i].shape == 'o'):
                if (i != len(data[rows]) - 1 and data[rows][i + 1].shape == '+'):
                    data[rows][i].health = data[rows][i].health - 2
                if (i != 0 and data[rows][i - 1].shape == '+'):
                    data[rows][i].health = data[rows][i].health - 2
                if (rows != len(data) - 1 and data[rows + 1][i].shape == '+'):
                    data[rows][i].health = data[rows][i].health - 2
                if (rows != 0 and data[rows - 1][i].shape == '+'):
                    data[rows][i].health = data[rows][i].health - 2
            if (data[rows][i].shape == '+'):
                if (i != len(data[rows]) - 1 and data[rows][i + 1].shape == 'o'):
                    data[rows][i].health = data[rows][i].health - 1
                if (i != 0 and data[rows][i - 1].shape == 'o'):
                    data[rows][i].health = data[rows][i].health - 1
                if (rows != len(data) - 1 and data[rows + 1][i].shape == 'o'):
                    data[rows][i].health = data[rows][i].health - 1
                if (rows != 0 and data[rows - 1][i].shape == 'o'):
                    data[rows][i].health = data[rows][i].health - 1
                if (rows != 0 and i != 0 and data[rows - 1][i - 1].shape == 'o'):
                    data[rows][i].health = data[rows][i].health - 1
                if (i != len(data[rows]) - 1 and rows != 0 and data[rows - 1][i + 1].shape == 'o'):
                    data[rows][i].health = data[rows][i].health - 1
                if (rows != len(data) - 1 and i != 0 and data[rows + 1][i - 1].shape == 'o'):
                    data[rows][i].health = data[rows][i].health - 1
                if (rows != len(data) - 1 and i != len(data[rows]) - 1 and data[rows + 1][
                    i + 1].shape == 'o'):
                    data[rows][i].health = data[rows][i].health - 1
    if (len(fromabove) > 0):
        for i in range(len(data[0])):
            if (data[0][i].shape == '+'):
                if (fromabove[i].shape == 'o'):
                    data[0][i].health = data[0][i].health - 1
                if (i != len(fromabove) - 1 and fromabove[i + 1].shape == 'o'):
                    data[0][i].health = data[0][i].health - 1
                if (i != 0 and fromabove[i - 1].shape == 'o'):
                    data[0][i].health = data[0][i].health - 1
            if (data[0][i].shape == 'o'):
                if (fromabove[i].shape == '+'):
                    data[0][i].health = data[0][i].health - 2

    if (len(frombelow) > 0):
        for i in range(len(data[len(data) - 1])):
            if (data[len(data) - 1][i].shape == '+'):
                if (frombelow[i].shape == 'o'):
                    data[len(data) - 1][i].health = data[len(data) - 1][i].health - 1
                if (i != len(frombelow) - 1 and frombelow[i + 1].shape == 'o'):
                    data[len(data) - 1][i].health = data[len(data) - 1][i].health - 1
                if (i != 0 and frombelow[i - 1].shape == 'o'):
                    data[len(data) - 1][i].health = data[len(data) - 1][i].health - 1
            if (data[len(data) - 1][i].shape == 'o'):
                if (frombelow[i].shape == '+'):
                    data[len(data) - 1][i].health = data[len(data) - 1][i].health - 2


# opens the input file
file = open(sys.argv[1], "r")
firstline = file.readline()
first = firstline.split()

# gets the information from the input file
sizeOfMap = int(first[0])
nOfWaves = int(first[1])
nOfTowers = int(first[2])

# the map
matrix = []

# map is empty at the beginning
for r in range(0, sizeOfMap):
    matrix.append([Tower('.', 0, 0, False) for c in range(0, sizeOfMap)])

wave = 0

# the main loop of waves
while (wave < nOfWaves):
    rounds = 0

    # manager process
    if rank == 0:
        lineofo = file.readline()
        lineofp = file.readline()
        otowers = lineofo.split(',')
        otowers[-1] = otowers[-1].strip()
        ptowers = lineofp.split(',')
        ptowers[-1] = ptowers[-1].strip()

        # putting new towers
        for i in otowers:
            coordinates = i.split()
            if (matrix[int(coordinates[0])][int(coordinates[1])].shape == '.'):
                t = Tower('o', 6, 1, True)
                matrix[int(coordinates[0])][int(coordinates[1])] = t
        for i in ptowers:
            coordinates = i.split()
            if (matrix[int(coordinates[0])][int(coordinates[1])].shape == '.'):
                t = Tower('+', 8, 2, True)
                matrix[int(coordinates[0])][int(coordinates[1])] = t
        x = sizeOfMap / (size - 1)

        # sends the appropriate towers to the worker processors
        for i in range(1, size):
            data = matrix[int((i - 1) * x):int((i - 1) * x + x)]
            comm.send(data, dest=i, tag=11)

    # worker processors receive towers
    if rank != 0:
        data = comm.recv(source=0, tag=11)

    # rounds loop in each wave
    while (rounds < 8):
        rounds = rounds + 1
        if rank == 0:
            continue

        # even number processors
        # sends the first and last row to the upper and lower processors and attacks
        if rank % 2 == 0 and rank != 0:
            fromabove = []
            frombelow = []

            if rank != size - 1:
                lastrow = data[-1]
                comm.send(lastrow, dest=rank + 1, tag=12)

            fromabove = comm.recv(source=rank - 1, tag=13)

            firstrow = data[0]
            comm.send(firstrow, dest=rank - 1, tag=14)

            if rank != size - 1:
                frombelow = comm.recv(source=rank + 1, tag=15)

            attack(data, fromabove, frombelow)

        # odd number processors
        # sends the first and last row to the upper and lower processors and attacks
        if rank % 2 == 1:
            fromabove = []
            frombelow = []

            if rank != 1:
                fromabove = comm.recv(source=rank - 1, tag=12)

            lastrow = data[-1]
            if rank != size - 1:
                comm.send(lastrow, dest=rank + 1, tag=13)

            if rank != size - 1:
                frombelow = comm.recv(source=rank + 1, tag=14)

            firstrow = data[0]
            if rank != 1:
                comm.send(firstrow, dest=rank - 1, tag=15)

            attack(data, fromabove, frombelow)

        if rank != 0:
            died(data)

    # worker processors sends the data to the manager processor
    if rank != 0:
        comm.send(data, dest=0, tag=25)

    # manager processor updates the map
    if rank == 0:
        for i in range(1, size):
            receivedata = comm.recv(source=i, tag=25)
            updatematrix(receivedata, matrix, i, size, sizeOfMap)

    wave = wave + 1

# printing the map at the end
output = open(sys.argv[2], "w")

if rank == 0:
	for i in range(0, len(matrix)):
		for j in range(0, len(matrix[i])):
			if j != len(matrix[i]) - 1:
				output.write(matrix[i][j].shape + " ")
			else:
				if i == len(matrix)-1:
					output.write(matrix[i][j].shape)
				else:
					output.write(matrix[i][j].shape + "\n")



