import copy
from engine import Engine

class AutoSolver(object):
    verboseLogging = True
    
    def __init__(self):
        self.actions = Engine.actionArray
       
    def GetLevelRepresentation(self, level):
        representation = ""
        for x in range(level.width):
            for y in range(level.height):
                for obj in level.map[y][x].objects:
                    if obj != None and obj != "background" :
                        representation = representation + obj + Helper.Get2DigitForm(x) + Helper.Get2DigitForm(y)
        return representation
     
    def GetSolutions(self, engine, levelIndex, numberOfSolutions = 0):
        engine.disableUndo = True
        intialValueForDisableLegendFix = engine.disableLegendFix
        engine.disableLegendFix = not self.verboseLogging
        solutionNodes = []
        visitedNodes = {}
        startingRep = self.GetLevelRepresentation(engine.levels[levelIndex])
        visitedNodes[startingRep] = StateNode(None, None, copy.deepcopy(engine.levels[levelIndex]))
        stateNodesQueue = [visitedNodes[startingRep]]
        
        while len(stateNodesQueue) > 0:
            currentState = stateNodesQueue[0]
            stateNodesQueue.pop(0)
            for action in self.actions:
                engine.levels[levelIndex] = copy.deepcopy(currentState.level)
                solved = engine.ProcessInput(action, levelIndex)
                newStateNode = StateNode(currentState, action, engine.levels[levelIndex])
                newState = True
                if visitedNodes.has_key(self.GetLevelRepresentation(engine.levels[levelIndex])):
                    newState = False
                if newState:
                    visitedNodes[self.GetLevelRepresentation(newStateNode.level)] = newStateNode
                    if not solved:
                        stateNodesQueue.append(newStateNode)
                if solved:
                    solutionNodes.append(newStateNode)
                    
            if self.verboseLogging:
                print currentState.level
            if len(solutionNodes) >= numberOfSolutions and numberOfSolutions > 0:
                break
        
        solutions = []
        for node in solutionNodes:
            currentSolution = []
            while node.parent != None:
                currentSolution.append(node.action)
                node = node.parent
            currentSolution.reverse()
            solutions.append(currentSolution)
        
        engine.disableLegendFix = intialValueForDisableLegendFix
        return solutions

class StateNode(object):
    def __init__(self, parent, action, level):
        self.level = level
        self.parent = parent
        self.action = action
        
class Helper(object):
    @staticmethod
    def Get2DigitForm(number):
        string = number.__str__()
        if number < 10:
            string = "0" + string
        return string
        