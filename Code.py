testFile1 = "test1.txt"
testFile2 = "test2.txt"

def readInput(testFile) :
    file = open(testFile, 'r+')
    fileList = file.readlines()
    fileList = [s.replace('\n', '') for s in fileList]
    
    [days, doctors] = [int(i) for i in fileList[0].split()]
    maxCapacity = int(fileList[1])
    
    allShifts = []
    for i in range(2, days + 2):
        dayRequirements = fileList[i].split()
        morningReqs = [int(i) for i in dayRequirements[0].split(",")]
        eveningReqs = [int(i) for i in dayRequirements[1].split(",")]
        nightReqs = [int(i) for i in dayRequirements[2].split(",")]
        
        allShifts.append((morningReqs, eveningReqs, nightReqs))

    file.close()
    return [days, list(range(doctors)), maxCapacity, allShifts]


class JobScheduler:
    def __init__(self, fileInfo):
        self.days = fileInfo[0]
        self.doctors = len(fileInfo[1])
        self.doctorsIds = fileInfo[1]
        self.maxCapacity = fileInfo[2]
        self.allShifts = fileInfo[3]
        self.popSize = 300
        self.chromosomes = self.generateInitialPopulation()
        
        # self.crossOverPoints = (relative to number of days)
        self.elitismPercentage = 16 #(move x% best of parents directly to the new population)
        self.pc = 0.65 #(crossover probability)
        self.pm = 0.4  #(mutation probability)
        
        
    def generateInitialPopulation(self):
        chromosomes = []
        for _ in range(self.popSize):
            new_array = np.random.randint(2, size=(self.doctors,self.days*3))
            chromosomes.append([new_array,self.calculateFitness(new_array)])
        return chromosomes
        
    
    def crossOver(self, chromosome1, chromosome2):
        child_chromosome = []
        for gp1, gp2 in zip(chromosome1[0], chromosome2[0]):
            prob = random.random()
            if prob < self.pc:
                child_chromosome.append(gp1)
            else:
                child_chromosome.append(gp2)
        child_chromosome = np.reshape(child_chromosome, (-1,self.days*3))
        return [child_chromosome,self.calculateFitness(child_chromosome)]
        
                
    def mutate(self, chromosome):
        Dno = random.randrange(0,self.doctors)
        shiNo = random.randrange(0,self.days*3)
        if chromosome[0][Dno][shiNo] == 0:
            chromosome[0][Dno][shiNo] = 1
        else: chromosome[0][Dno][shiNo] = 0
        chromosome[1] = self.calculateFitness(chromosome[0])
        return chromosome

        
        
    def calculateFitness(self, chromosome):
        fitness = 0

        #condition number 3
        count = np.count_nonzero(chromosome == 1, axis=1)
        for i in count:
            if i > self.maxCapacity :
                fitness += abs(i-self.maxCapacity)

        # condition number 1
        count = np.count_nonzero(chromosome == 1, axis=0)
        for i in range(len(count)):
            if count[i] < self.allShifts[int(i/3)][i%3][0] :
                fitness += self.allShifts[int(i/3)][i%3][0] - count[i]
            elif count[i] > self.allShifts[int(i/3)][i%3][1]:
                fitness += count[i] - self.allShifts[int(i/3)][i%3][1]

        # condition nuber 2
        a = 0
        for row in chromosome:
            for i in range(2,len(row)-1, 3):
                if row[i] == 1:
                    a += 1
                    if row[i+1]==1:
                        fitness += 1
                    if row[i+2]==1:
                        fitness += 1
                    if a == 3:
                        fitness +=1
                        a -= 1
                else: a = 0

        return fitness
    
    
    def generateNewPopulation(self):
        new_generation = []

        s = int((self.elitismPercentage*self.popSize)/100)
        for i in range(s):
            mute = random.choices([0,1], weights=((1-self.pm)*100, self.pm*100))
            child = self.chromosomes[i]
            if mute[0] == 1:
                child = self.mutate(child)
            new_generation.append(child)

        s = self.popSize - s
        for _ in range(s):
            parent1 = random.choice(self.chromosomes[:int(self.pc*self.popSize)])
            parent2 = random.choice(self.chromosomes[:int(self.pc*self.popSize)])
            child = self.crossOver(parent1, parent2)
            mute = random.choices([0,1], weights=((1-self.pm)*100, self.pm*100))
            if mute[0] == 1:
                child = self.mutate(child)
            new_generation.append(child)

        self.chromosomes = new_generation
        return
    
    
    def schedule(self): 
        found = False
        while not found:
            self.chromosomes = sorted(self.chromosomes, key = lambda x:x[1])
            if self.chromosomes[0][1] <= 0:
                found = True
                break

            self.generateNewPopulation()
        return self.chromosomes[0][0],self.doctors,self.days


def writeOutput(filename, result, doctors, days):
    file1 = open(filename, 'w')
    s = ""
    for j in range(days*3):
        for i in range(doctors):
            if result[i][j] == 1:
                s += str(i)
                s += ','
        if j%3 == 2:
            s = s[:-1]
            s += '\n'
            file1.write(s)
            s = ""
        else: 
            s = s[:-1]
            s += ' '



import time
import numpy as np
import random

fileInfo1 = readInput(testFile1)

start = time.time()

scheduler = JobScheduler(fileInfo1)
result, doctors, days = scheduler.schedule()

end = time.time()

print("test 1: ", '%.2f'%(end - start), 'sec')

writeOutput("output1.txt", result, doctors, days)

fileInfo2 = readInput(testFile2)

start = time.time()

scheduler = JobScheduler(fileInfo2)
result, doctors, days = scheduler.schedule()

end = time.time()

print("Test 2: ", '%.2f'%(end - start), 'sec')
writeOutput("output2.txt", result, doctors, days)