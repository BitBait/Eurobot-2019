import collections
from math import pi, sin, cos, floor, sqrt
import pygame
from pygame.locals import *

# Initialise the pygame window
pygame.init()
w, h = 500, 500
screen = pygame.display.set_mode((w, h))

# A whole bunch of colours, represented in the form (R, G, B)
COL_BLACK = (0, 0, 0)
COL_GREY = (150, 150, 150)
COL_WHITE = (255, 255, 255)
COL_RED = (255, 0, 0)
COL_GREEN = (0, 255, 0)
COL_BLUE = (0, 0, 255)

# A really short function that converts tuple coordinates to the node name format
nodename = lambda coords: "Node x = %s y = %s" % coords


# The node class, used for storing points
class Node:
    def __init__(self, Name, Position):
        self.Name = Name
        self.Position = Position
        self.Wall = False


# The graph class which defines where nodes are, who they are connected to and how far away they are from another node
class Graph:
    def __init__(self):
        self.edges = {}
        self.weights = {}

    def Neighbors(self, id):
        return self.edges[id]

    def Weight(self, Node1, Node2):
        Cost = sqrt(((Node1.Position[0] - Node2.Position[0])**2) + ((Node1.Position[1] - Node2.Position[0])**2))
        return self.weights.get(Node2, Cost)


# An example class to allow for testing of the pathfinding
class ExampleGraph:
    def __init__(self):
        self.A = Node("Node A", (1, 1))
        self.B = Node("Node B", (3, 3))
        self.C = Node("Node C", (4, 4))
        self.D = Node("Node D", (3, 5))
        self.E = Node("Node E", (5, 5))
        self.F = Node("Node F", (1, 2))
        self.G = Node("Node G", (4, 5))

        self.ExampleGraphBetterName = Graph()
        self.ExampleGraphBetterName.edges = {
            self.A: [self.B],
            self.B: [self.A, self.C, self.D],
            self.C: [self.A],
            self.D: [self.E, self.A],
            self.E: [self.B],
            self.F: [self.A, self.E],
            self.G: [self.A, self.B, self.C, self.D, self.E, self.F]
        }

class Grid:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.NodeList = {}
        self.GraphGrid = Graph()

    def CreateNodeGrid(self):
        while self.y < 101:
            if self.x < 101:
                self.NodeList["Node x = " + str(self.x) + " y = " + str(self.y)] = Node(str("Node x = " + str(self.x) + " y = " + str(self.y)), (self.x, self.y))
                self.x += 1
            else:
                self.x = 0  # Not 1, because otherwise the first column doesn't exist
                self.y += 1

class GeneralGrid:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.NodeList = {}
        self.weights = {}
        self.GraphGrid = Graph()

    def CreateNodeGrid(self, SizeX, SizeY):
        # Maybe this could be done with two nested for loops? (i.e. for x in range(SizeX):
        #                                                               for y in range(SizeY):
        #                                                                   self.NodeLis.......... )
        while self.y < SizeY:
            if self.x < SizeX:
                self.NodeList["Node x = " + str(self.x) + " y = " + str(self.y)] = Node(str("Node x = " + str(self.x) + " y = " + str(self.y)), (self.x, self.y))
                self.x += 1
            else:
                self.x = 0  # Not 1, because otherwise the first column doesn't exist
                self.y += 1

    def Neighbors(self, id):
        Results = []
        Pos = id.Position
        NeighborLeft = self.NodeList.get("Node x = " + str((Pos[0] - 1)) + " y = " + str(Pos[1]))
        NeighborRight = self.NodeList.get("Node x = " + str((Pos[0] + 1)) + " y = " + str(Pos[1]))
        NeighborBelow = self.NodeList.get("Node x = " + str(Pos[0]) + " y = " + str(Pos[1] - 1))
        NeighborAbove = self.NodeList.get("Node x = " + str(Pos[0]) + " y = " + str(Pos[1] + 1))
        if isinstance(NeighborLeft, Node):
            Results.append(NeighborLeft)
        if isinstance(NeighborRight, Node):
            Results.append(NeighborRight)
        if isinstance(NeighborBelow, Node):
            Results.append(NeighborBelow)
        if isinstance(NeighborAbove, Node):
            Results.append(NeighborAbove)
        return Results

    def Weight(self, Node1, Node2):
        Cost = sqrt(((Node1.Position[0] - Node2.Position[0])**2) + ((Node1.Position[1] - Node2.Position[0])**2))
        return self.weights.get(Node2, Cost)

    def Wall(self, Node):
        Node.wall = True


# A queue class which allows us to store where we have been
class Queue:
        def __init__(self):
            self.elements = collections.deque()

        def empty(self):
            return len(self.elements) == 0

        def put(self, x):
            self.elements.append(x)

        def get(self):
            return self.elements.popleft()


# The a star pathfinding algorithm
def AStartSearch(Graph , Start, Goal):
    frontier = Queue()
    frontier.put(Start)
    CameFrom = {}
    CameFrom[Start] = None
    CostSoFar = 0
    Visited = {}
    Visited[Start] = True

    while not frontier.empty():
        Current = frontier.get()

        if Current == Goal:
            break

        for Next in Graph.Neighbors(Current):
            if Next.Wall == False:
                NewCost = CostSoFar + Graph.Weight(Current, Next)
                if Next not in CameFrom or NewCost < CostSoFar:
                    CostSoFar += NewCost
                    frontier.put(Next)
                    CameFrom[Next] = Current
                    print("Visiting %r" % Current.Name)

    return CameFrom

TestGraph = ExampleGraph()
Testing = AStartSearch(TestGraph.ExampleGraphBetterName, TestGraph.A, TestGraph.E)


# A function that takes in the path from the pathfinding and reconstructs it
def ReconstructPath(CameFrom, Start, Goal):
    current = Goal
    path = []
    while current != Start:
        path.append(current)
        try:
            current = CameFrom[current]
        except KeyError:
            raise Exception("No Possible Path")
    path.append(Start)
    path.reverse()
    return path


# A function that takes in the reconstructed path and tells the robot where to move
def TellRobot(Path):
    NodeCounter = 0
    CurrentPos = list(Path[NodeCounter].Position)
    ListOfThingsToDo = []
    while tuple(CurrentPos) != Path[-1].Position:
        NextPos = Path[NodeCounter + 1].Position
        if tuple(CurrentPos) == Path[NodeCounter].Position:
            NodeCounter += 1
        if CurrentPos[0] < NextPos[0]:
            ListOfThingsToDo.append("R")
            CurrentPos[0] += 1
        elif CurrentPos[0] > NextPos[0]:
            ListOfThingsToDo.append("L")
            CurrentPos[0] -= 1
        elif CurrentPos[1] < NextPos[1]:
            ListOfThingsToDo.append("F")
            CurrentPos[1] += 1
        elif CurrentPos[1] > NextPos[1]:
            ListOfThingsToDo.append("B")
            CurrentPos[1] -= 1

    return ListOfThingsToDo


def ToggleWall(Graph):
    MouseX = pygame.mouse.get_pos()[0]
    MouseY = pygame.mouse.get_pos()[1]

    FloorX = floor(MouseX)
    FloorY = floor(MouseY)

    while FloorX % 50 != 0:
        FloorX -= 1
        if FloorX == 0:
            break

    while FloorY % 50 != 0:
        FloorY -= 1
        if FloorY == 0:
            break

    FloorX = FloorX/50
    FloorY = FloorY/50

    FloorX = int(FloorX)
    FloorY = int(FloorY)

    NodePos = (FloorX, FloorY)
    print(NodePos)

    x = Graph.NodeList.get(nodename(NodePos))
    x.Wall = not x.Wall
    print(x.Name)


def drawarrow(surface, node, thing):
    ang = "RFLB".find(thing) * (pi / 2)
    nodepos = node.Position
    pygame.draw.line(surface, COL_WHITE,
                     ((nodepos[0] + 0.5 - cos(ang) * 0.4) * squaresidelength,
                      (nodepos[1] + 0.5 - sin(ang) * 0.4) * squaresidelength),
                     ((nodepos[0] + 0.5) * squaresidelength,
                      (nodepos[1] + 0.5) * squaresidelength),
                     10)
    pygame.draw.polygon(surface, COL_WHITE,
                        [((nodepos[0] + 0.5 + sin(ang) * 0.4) * squaresidelength,
                          (nodepos[1] + 0.5 - cos(ang) * 0.4) * squaresidelength),
                         ((nodepos[0] + 0.5 + cos(ang) * 0.4) * squaresidelength,
                          (nodepos[1] + 0.5 + sin(ang) * 0.4) * squaresidelength),
                         ((nodepos[0] + 0.5 - sin(ang) * 0.4) * squaresidelength,
                          (nodepos[1] + 0.5 + cos(ang) * 0.4) * squaresidelength)])


griddimensions = (10, 10)
squaresidelength = int(min(w, h) / max(griddimensions))

startnodepos = (0, 0)
goalnodepos = (7, 7)
print(startnodepos, goalnodepos)

# Path = ReconstructPath(Testing, TestGraph.A, TestGraph.E)
# print(Path)
# ListOfThings = TellRobot(Path)
# print(ListOfThings)

TBT = GeneralGrid()
TBT.CreateNodeGrid(*griddimensions)
#print(len(list((TBT.NodeList.values()))))
TBTTest = AStartSearch(TBT, TBT.NodeList[nodename(startnodepos)], TBT.NodeList[nodename(goalnodepos)])
PathTBT = ReconstructPath(TBTTest, TBT.NodeList[nodename(startnodepos)], TBT.NodeList[nodename(goalnodepos)])
#print(PathTBT)
ListOfThings3 = TellRobot(PathTBT)
print(ListOfThings3)

#print(len(TBT.NodeList))

while True:
    # Colour in window white
    screen.fill(COL_WHITE)
    # Colour in each square, and draw arrows where necessary
    for node in TBT.NodeList.values():
        if node.Wall:
            # If it's a wall, colour it grey
            pygame.draw.rect(screen, COL_GREY,
                             (node.Position[0] * squaresidelength, node.Position[1] * squaresidelength,
                              squaresidelength, squaresidelength))
        if node in PathTBT:
            # If it's in the path...
            i = PathTBT.index(node)
            if i < len(PathTBT) - 1:
                # ... and if it's not the goal node...
                if i == 0:
                    # ... and if it is the start node, colour it red
                    pygame.draw.rect(screen, COL_RED,
                                     (node.Position[0] * squaresidelength,
                                      node.Position[1] * squaresidelength,
                                      squaresidelength, squaresidelength))
                else:
                    # ... otherwise colour it black
                    pygame.draw.rect(screen, COL_BLACK,
                                     (node.Position[0] * squaresidelength, node.Position[1] * squaresidelength,
                                      squaresidelength, squaresidelength))
                # ... draw an arrow on the node
                drawarrow(screen, node, ListOfThings3[i])
            else:
                # ... otherwise it is the goal node. Colour it green
                pygame.draw.rect(screen, COL_GREEN,
                                 (node.Position[0] * squaresidelength, node.Position[1] * squaresidelength,
                                 squaresidelength, squaresidelength))
    # Draw the vertical red grid lines, then the horizontal ones
    for x in range(1, griddimensions[0]):
        pygame.draw.line(screen, COL_RED,
                         (x * squaresidelength, 0),
                         (x * squaresidelength, griddimensions[1] * squaresidelength))
    for y in range(1, griddimensions[1]):
        pygame.draw.line(screen, COL_RED,
                         (0, y * squaresidelength),
                         (griddimensions[0] * squaresidelength, y * squaresidelength))
    # Display the newly coloured window
    pygame.display.flip()
    # Event handling
    for e in pygame.event.get():
        if e.type == QUIT:
            # Quit if the x on the window is pressed
            quit()
        elif e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                # Quit if escape is pressed
                quit()
        elif e.type == MOUSEBUTTONDOWN:
            # Change state of a grid square that's clicked on from wall <-> not wall
            ToggleWall(TBT)
            # And then recalculate pathfinding accordingly
            TBTTest = AStartSearch(TBT, TBT.NodeList[nodename(startnodepos)], TBT.NodeList[nodename(goalnodepos)])
            PathTBT = ReconstructPath(TBTTest, TBT.NodeList[nodename(startnodepos)], TBT.NodeList[nodename(goalnodepos)])
            ListOfThings3 = TellRobot(PathTBT)
            print(ListOfThings3)
