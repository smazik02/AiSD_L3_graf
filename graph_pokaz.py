from copy import deepcopy
import sys
from timeit import default_timer as timer
from tabulate import tabulate


class Graph:
    def __init__(self):
        self.data = []

    def printArrayForm(self):
        print(self.data)
    
    def printArrayFormNice(self):
        print(tabulate(self.data, tablefmt="fancy_grid"))


class AdjacencyGraph(Graph):
    def newGraph(self, edges):
        nodes_count = edges[0][0]
        self.data = [[0]*nodes_count for _ in range(nodes_count)]
        del edges[0]
        for line in edges:
            self.data[line[0]-1][line[1]-1] = 1
            self.data[line[1]-1][line[0]-1] = -1

    def newGraphFromFile(self, filename):
        with open(filename, "r") as file:
            self.newGraph([[int(x) for x in line.split()] for line in file])

    def removeEdge(self, edge):
        self.data[edge[0]][edge[1]] = 0
        self.data[edge[1]][edge[0]] = 0

    def DFS(self):
        global colors, L, S, cycle
        colors = [0]*len(self.data)
        L, S = [], []
        independent = [i+1 for i, u in enumerate(self.data) if not -1 in u]
        cycle = False
        if not independent:
            print("Graf zawiera cykl. Sortowanie niemożliwe.")
            return []
        for u in independent:
            if colors[u-1] == 0:
                self._dfsTraverse(u-1)
            if cycle:
                print("Graf zawiera cykl. Sortowanie niemożliwe.")
                return []
            if not 0 in colors and not 1 in colors:
                while S:
                    L.append(S.pop())
                break
        return L

    def _dfsTraverse(self, u):
        global cycle
        colors[u] = 1
        neighbors = [i for i in range(len(self.data)) if self.data[u][i] == 1]
        for i in neighbors:
            if colors[i] == 1:
                cycle = True
                return
        for i in neighbors:
            if colors[i] == 0:
                self._dfsTraverse(i)
        if cycle:
            return
        colors[u] = 2
        S.append(u+1)

    def DEL(self):
        nodes = deepcopy(self.data)
        noinnodes = [i+1 for i in range(len(nodes)) if not -1 in nodes[i]]
        if not noinnodes:
            print("Graf zawiera cykl. Sortowanie niemożliwe.")
            return []
        result = []
        while noinnodes:
            n = noinnodes.pop(0)
            result.append(n)
            for m in range(1, len(nodes)+1):
                if nodes[n-1][m-1] == 0:
                    continue
                nodes[n-1][m-1] = 0
                nodes[m-1][n-1] = 0
                if not -1 in nodes[m-1]:
                    noinnodes.append(m)
            noinnodes.sort()
        for node in nodes:
            if 1 in node or -1 in node:
                print("Graf zawiera cykl. Sortowanie niemożliwe.")
                return []
        return result
    
    def DFSPrint(self):
        tmp = self.DFS()
        if tmp != []:
            print(tmp)

    def DELPrint(self):
        tmp = self.DEL()
        if tmp != []:
            print(tmp)


class GraphMatrix(Graph):
    def newGraph(self, edges):
        nodes = edges[0][0]
        self.data = [[0]*(nodes+3) for _ in range(nodes)]
        del edges[0]
        successor = {int(x): [] for x in range(1, nodes+1)}
        predecessor = {int(x): [] for x in range(1, nodes+1)}
        rest = {int(x): [] for x in range(1, nodes+1)}
        # Tworzenie list następników i poprzedników
        for line in edges:
            successor[line[0]].append(line[1])
            predecessor[line[1]].append(line[0])
        #Tworzenie listy nieincydentnych
        for i in range(1, nodes+1):
            for j in range(1, nodes+1):
                if j not in successor[i] and j not in predecessor[i]:
                    rest[i].append(j)
        for i in range(1, nodes+1):
            for j in successor[i]:
                self.data[i-1][j-1] = successor[i][len(successor[i])-1]
            if successor[i] == []:
                self.data[i-1][nodes] = 0
            else:
                self.data[i-1][nodes] = successor[i][0]
            for j in predecessor[i]:
                self.data[i-1][j -
                               1] = predecessor[i][len(predecessor[i])-1] + nodes
            if predecessor[i] == []:
                self.data[i-1][nodes+1] = 0
            else:
                self.data[i-1][nodes+1] = predecessor[i][0]
            for j in rest[i]:
                self.data[i-1][j-1] = rest[i][len(rest[i])-1] * (-1)
            if rest[i] == []:
                self.data[i-1][nodes+2] = 0
            else:
                self.data[i-1][nodes+2] = rest[i][0]

    def newGraphFromFile(self, filename):
        with open(filename, "r") as file:
            self.newGraph([[int(x) for x in line.split()] for line in file])

    def removeEdge(self, edge):
        # Jeżeli łuk nie istnieje, nic nie robimy
        if self.data[edge[0]-1][edge[1]-1] not in range(0, len(self.data)+1):
            print("Łuk nie istnieje")
            return
        # Jeżeli usuwamy łuk do pierwszego następnika
        if edge[1] == self.data[edge[0]-1][len(self.data)]:
            found = False
            # Szukamy pierwszego następnika który nie jest tym, który chcemy usunąć
            for i in range(edge[1], len(self.data)):
                # Jeżeli znaleźliśmy pierwszy następnik, wpisujemy jego indeks do komórki z wartością pier. nast.
                if self.data[edge[0]-1][i] in range(len(self.data)+1):
                    found = True
                    self.data[edge[0]-1][len(self.data)] = i+1
                    break
            # Jeżeli nie znaleźliśmy i usuwamy jedyny następnik, wpisujemy zero
            if not found:
                self.data[edge[0]-1][len(self.data)] = 0
        else:
            # Sprawdzamy wartość ostatniego następnika
            last = 0
            for i in range(len(self.data)):
                if self.data[edge[0]-1][i] in range(len(self.data)+1):
                    last = self.data[edge[0]-1][i]
                    break
            # Jeżeli usuwamy łuk do ostatniego następnika
            if edge[1] == last:
                # Szukamy przedostatniego następnika i zastępujemy wszystkie komórki następnika jego indeksem
                # Nie musimy obsługiwać przypadku usunięcia jedynego następnika, jest on przetwarzany wcześniej
                tmp = 0
                for i in range(edge[1]-2, -1, -1):
                    if self.data[edge[0]-1][i] in range(len(self.data)+1):
                        tmp = i+1
                        break
                for i in range(len(self.data)):
                    if self.data[edge[0]-1][i] in range(len(self.data)+1):
                        self.data[edge[0]-1][i] = tmp
            # Jeżeli usuwamy następnik "środkowy" - nie zmienia się nic poza komórką, która zmieni się w następnej części

        # Jeżeli nie było nieincydentnych węzłów, to dodajemy nowy
        if self.data[edge[0]-1][len(self.data)+2] == 0:
            self.data[edge[0]-1][len(self.data)+2] = edge[1]
            self.data[edge[0]-1][edge[1]-1] = -edge[1]
        # Jeżeli pierwszy nieindycentny węzeł jest większy od właśnie usuniętego następnika,
        # to wtedy go nadpisujemy w ostatniej komórce
        elif self.data[edge[0]-1][len(self.data)+2] > edge[1]:
            self.data[edge[0]-1][len(self.data)+2] = edge[1]
            # Następnie szukamy wartości ostatniego następnika i wpisujemy do komórki usuniętego węzła
            for i in range(len(self.data)):
                if self.data[edge[0]-1][i] < 0:
                    self.data[edge[0]-1][edge[1]-1] = self.data[edge[0]-1][i]
                    break
        else:
            tmp = 0
            for i in self.data[edge[0]-1]:
                if i < 0:
                    tmp = -i
                    break
            # Jeżeli ostatni nieincydentny węzeł jest mniejszy od właśnie usuniętego następnika,
            # to nadpisujemy wszystkie nieincydentne komórki z nową wartością
            if tmp < edge[1]:
                self.data[edge[0]-1][edge[1]-1] = -edge[1]
                for i in range(len(self.data)-1):
                    if self.data[edge[0]-1][i] < 0:
                        self.data[edge[0]-1][i] = -edge[1]
            else:
                # Jeżeli dodajemy nieincydentny węzeł "do środka"
                # to zmieniamy tylko jedną komórkę
                self.data[edge[0]-1][edge[1]-1] = -tmp

        # Jeżeli usuwamy łuk do pierwszego poprzednika
        if edge[0] == self.data[edge[1]-1][len(self.data)+1]:
            found = False
            # Szukamy pierwszego poprzednika który nie jest tym, który chcemy usunąć
            for i in range(edge[0], len(self.data)):
                # Jeżeli znaleźliśmy pierwszy poprzednik, wpisujemy jego indeks do komórki z wartością pier. poprz.
                if self.data[edge[1]-1][i] in range(len(self.data)+2, 2*len(self.data)+1):
                    found = True
                    self.data[edge[1]-1][len(self.data)+1] = i+1
                    break
            # Jeżeli nie znaleźliśmy i usuwamy jedyny następnik, wpisujemy zero
            if not found:
                self.data[edge[1]-1][len(self.data)+1] = 0
        else:
            # Sprawdzamy wartość ostatniego poprzednika
            last = 0
            for i in range(len(self.data)):
                if self.data[edge[1]-1][i] in range(len(self.data)+2, 2*len(self.data)+1):
                    last = self.data[edge[1]-1][i] - len(self.data)
                    break
            # Jeżeli usuwamy łuk od ostatniego poprzednika
            if edge[0] == last:
                # Szukamy przedostatniego poprzednika i zastępujemy wszystkie komórki poprzednika jego indeksem + liczba węzłów
                # Nie musimy obsługiwać przypadku usunięcia jedynego poprzednika, jest on przetwarzany wcześniej
                tmp = 0
                edges = len(self.data)
                for i in range(edge[0]-2, -1, -1):
                    if self.data[edge[1]-1][i] in range(len(self.data)+2, 2*len(self.data)+1):
                        tmp = i+edges+1
                        break
                for i in range(len(self.data)):
                    if self.data[edge[1]-1][i] in range(len(self.data)+2, 2*len(self.data)+1):
                        self.data[edge[1]-1][i] = tmp
            # Jeżeli usuwamy poprzednik "środkowy" - nie zmienia się nic poza komórką, która zmieni się w następnej części
        
        # Jeżeli nie było nieincydentnych węzłów, to dodajemy nowy
        if self.data[edge[1]-1][len(self.data)+2] == 0:
            self.data[edge[1]-1][len(self.data)+2] = edge[0]
            self.data[edge[1]-1][edge[0]-1] = -edge[0]
        # Jeżeli pierwszy nieindycentny węzeł jest większy od właśnie usuniętego poprzednika,
        # to wtedy go nadpisujemy w ostatniej komórce
        elif self.data[edge[1]-1][len(self.data)+2] > edge[0]:
            self.data[edge[1]-1][len(self.data)+2] = edge[0]
            # Następnie szukamy wartości ostatniego poprzednika i wpisujemy do komórki usuniętego węzła
            for i in range(len(self.data)):
                if self.data[edge[1]-1][i] < 0:
                    self.data[edge[1]-1][edge[0]-1] = self.data[edge[1]-1][i]
                    break
        else:
            tmp = 0
            for i in self.data[edge[1]-1]:
                if i < 0:
                    tmp = -i
                    break
            # Jeżeli ostatni nieincydentny węzeł jest mniejszy od właśnie usuniętego poprzednika,
            # to nadpisujemy wszystkie nieincydentne komórki z nową wartością
            if tmp < edge[0]:
                self.data[edge[1]-1][edge[0]-1] = -edge[0]
                for i in range(len(self.data)-1):
                    if self.data[edge[1]-1][i] < 0:
                        self.data[edge[1]-1][i] = -edge[0]
            else:
                # Jeżeli dodajemy nieincydentny węzeł "do środka"
                # to zmieniamy tylko jedną komórkę
                self.data[edge[1]-1][edge[0]-1] = -tmp

    def _removeEdgeArr(self, Arr, edge):
        if Arr[edge[0]-1][edge[1]-1] not in range(0, len(Arr)+1):
            return
        if edge[1] == Arr[edge[0]-1][len(Arr)]:
            found = False
            for i in range(edge[1], len(Arr)):
                if Arr[edge[0]-1][i] in range(len(Arr)+1):
                    found = True
                    Arr[edge[0]-1][len(Arr)] = i+1
                    break
            if not found:
                Arr[edge[0]-1][len(Arr)] = 0
        else:
            last = 0
            for i in range(len(Arr)):
                if Arr[edge[0]-1][i] in range(len(Arr)+1):
                    last = Arr[edge[0]-1][i]
                    break
            if edge[1] == last:
                tmp = 0
                for i in range(edge[1]-2, -1, -1):
                    if Arr[edge[0]-1][i] in range(len(Arr)+1):
                        tmp = i+1
                        break
                for i in range(len(Arr)):
                    if Arr[edge[0]-1][i] in range(len(Arr)+1):
                        Arr[edge[0]-1][i] = tmp

        if Arr[edge[0]-1][len(Arr)+2] == 0:
            Arr[edge[0]-1][len(Arr)+2] = edge[1]
            Arr[edge[0]-1][edge[1]-1] = -edge[1]
        elif Arr[edge[0]-1][len(Arr)+2] > edge[1]:
            Arr[edge[0]-1][len(Arr)+2] = edge[1]
            for i in range(len(Arr)):
                if Arr[edge[0]-1][i] < 0:
                    Arr[edge[0]-1][edge[1]-1] = Arr[edge[0]-1][i]
                    break
        else:
            tmp = 0
            for i in Arr[edge[0]-1]:
                if i < 0:
                    tmp = -i
                    break
            if tmp < edge[1]:
                Arr[edge[0]-1][edge[1]-1] = -edge[1]
                for i in range(len(Arr)-1):
                    if Arr[edge[0]-1][i] < 0:
                        Arr[edge[0]-1][i] = -edge[1]
            else:
                Arr[edge[0]-1][edge[1]-1] = -tmp

        if edge[0] == Arr[edge[1]-1][len(Arr)+1]:
            found = False
            for i in range(edge[0], len(Arr)):
                if Arr[edge[1]-1][i] in range(len(Arr)+2, 2*len(Arr)+1):
                    found = True
                    Arr[edge[1]-1][len(Arr)+1] = i+1
                    break
            if not found:
                Arr[edge[1]-1][len(Arr)+1] = 0
        else:
            last = 0
            for i in range(len(Arr)):
                if Arr[edge[1]-1][i] in range(len(Arr)+2, 2*len(Arr)+1):
                    last = Arr[edge[1]-1][i] - len(Arr)
                    break
            if edge[0] == last:
                tmp = 0
                edges = len(Arr)
                for i in range(edge[0]-2, -1, -1):
                    if Arr[edge[1]-1][i] in range(len(Arr)+2, 2*len(Arr)+1):
                        tmp = i+edges+1
                        break
                for i in range(len(Arr)):
                    if Arr[edge[1]-1][i] in range(len(Arr)+2, 2*len(Arr)+1):
                        Arr[edge[1]-1][i] = tmp
        
        if Arr[edge[1]-1][len(Arr)+2] == 0:
            Arr[edge[1]-1][len(Arr)+2] = edge[0]
            Arr[edge[1]-1][edge[0]-1] = -edge[0]
        elif Arr[edge[1]-1][len(Arr)+2] > edge[0]:
            Arr[edge[1]-1][len(Arr)+2] = edge[0]
            for i in range(len(Arr)):
                if Arr[edge[1]-1][i] < 0:
                    Arr[edge[1]-1][edge[0]-1] = Arr[edge[1]-1][i]
                    break
        else:
            tmp = 0
            for i in Arr[edge[1]-1]:
                if i < 0:
                    tmp = -i
                    break
            if tmp < edge[0]:
                Arr[edge[1]-1][edge[0]-1] = -edge[0]
                for i in range(len(Arr)-1):
                    if Arr[edge[1]-1][i] < 0:
                        Arr[edge[1]-1][i] = -edge[0]
            else:
                Arr[edge[1]-1][edge[0]-1] = -tmp

    def DFS(self):
        global colors, L, S, cycle
        colors = [0]*len(self.data)
        L, S = [], []
        independent = [i+1 for i, u in enumerate(self.data) if u[len(self.data)+1] == 0]
        cycle = False
        if not independent:
            print("Graf zawiera cykl. Sortowanie niemożliwe.")
            return []
        for u in independent:
            if colors[u-1] == 0:
                self._dfsTraverse(u-1)
            if cycle:
                print("Graf zawiera cykl. Sortowanie niemożliwe.")
                return []
            if not 0 in colors and not 1 in colors:
                while S:
                    L.append(S.pop())
                break
        return L

    def _dfsTraverse(self, u):
        global cycle
        colors[u] = 1
        neighbors = [i for i in range(len(self.data)) if self.data[u][i] in range(len(self.data)+1)]
        for i in neighbors:
            if colors[i] == 1:
                cycle = True
                return
        for i in neighbors:
            if colors[i] == 0:
                self._dfsTraverse(i)
        if cycle:
            return
        colors[u] = 2
        S.append(u+1)

    def DEL(self):
        nodes = deepcopy(self.data)
        noinnodes = [i+1 for i in range(len(nodes)) if nodes[i][len(nodes)+1] == 0]
        if not noinnodes:
            print("Graf zawiera cykl. Sortowanie niemożliwe.")
            return []
        result = []
        while noinnodes:
            n = noinnodes.pop(0)
            result.append(n)
            for m in range(1, len(nodes)+1):
                if nodes[n-1][m-1] < 0:
                    continue
                self._removeEdgeArr(nodes, [n, m])
                if nodes[m-1][len(nodes)+1] == 0:
                    noinnodes.append(m)
            noinnodes.sort()
        for i in range(len(nodes)):
            if nodes[i][len(nodes)] != 0 or nodes[i][len(nodes)+1] != 0:
                print("Graf zawiera cykl. Sortowanie niemożliwe.")
                return []
        return result
    
    def DFSPrint(self):
        tmp = self.DFS()
        if tmp != []:
            print(tmp)

    def DELPrint(self):
        tmp = self.DEL()
        if tmp != []:
            print(tmp)

tmp1 = input("Porównanie - DFS [Y/n] > ")
tmp2 = input("Porównanie - DEL [Y/n] > ")

filename = sys.argv[1]
graph1 = AdjacencyGraph()
graph2 = GraphMatrix()
graph1.newGraphFromFile(filename)
graph2.newGraphFromFile(filename)

if (tmp := input("Pokaż grafy w formie macierzy [Y/n] > ")).upper() == "Y":
    print("\nMacierz sąsiedztwa")
    graph1.printArrayForm()
    print("\nMacierz grafu")
    graph2.printArrayForm()

if tmp1.upper() == "Y":
    print("\nG1 DFS")
    graph1.DFSPrint()
    print("\nG2 DFS")
    graph2.DFSPrint()
    
if tmp2.upper() == "Y":
    print("\nG1 DEL")
    graph1.DELPrint()
    print("\nG2 DEL")
    graph2.DELPrint()
