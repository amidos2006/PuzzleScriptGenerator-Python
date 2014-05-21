import random
import copy

class Engine(object):
    actionArray = ["left", "right", "up", "down", "action"]
    
    def __init__(self, objectLines = [], legendLines = [], layerLines = [], ruleLines = [], winLines = [], levelLines = []):
        self.objects = []
        self.legends = []
        self.layers = []
        self.rules = []
        self.winConditions = []
        self.levels = []
        
        tempLines = []
        for ol in objectLines:
            ol = ol.strip().lower()
            if ol != "":
                tempLines.append(ol)
            else:
                self.objects.append(GameObject(tempLines))
                tempLines = [] 
        if len(tempLines) > 0:
            self.objects.append(GameObject(tempLines))
        
        tempLines = []
        for ll in legendLines:
            ll = ll.strip().lower()
            if ll != "":
                self.legends.append(Legend(ll, self.objects))
                
        tempLines = []
        for ll in layerLines:
            ll = ll.strip().lower()
            if ll != "":
                self.layers.append(CollisionLayer(ll, self.objects))
                
        tempLines = []
        for rl in ruleLines:
            rl = rl.strip().lower()
            if rl != "":
                rg = GroupRule(rl, self.objects, self.layers)
                if(rg.add):
                    if len(self.rules) > 0:
                        self.rules[-1].rules = self.rules[-1].rules + rg.rules
                    else:
                        print "Can't have first rule as added rule"
                else: 
                    self.rules.append(rg)
        
        tempLines = []
        for wl in winLines:
            wl = wl.strip().lower()
            if wl != "":
                self.winConditions.append(WinCondition(wl, self.objects))
                
        tempLines = []
        for ll in levelLines:
            ll = ll.strip().lower()
            if ll != "":
                tempLines.append(ll)
            else:
                self.levels.append(Level(tempLines, self.legends, self.layers))
                tempLines = []
        if len(tempLines) > 0:
            self.levels.append(Level(tempLines, self.legends, self.layers))
        
        Level.directionMap = {"left":Point(-1, 0), "right":Point(1, 0), "up":Point(0, -1), "down":Point(0, 1), "action":Point(0, 0)}
    
    def ProcessInput(self, action, levelIndex):
        playerIndex = Helper.GetLayerNumber("player", self.layers)
        playerPositions = self.levels[levelIndex].GetIndexFromObjectID("player")
        print "Adding the action to player"
        for p in playerPositions:
            self.levels[levelIndex].map[p.y][p.x].actions[playerIndex] = action.strip().lower()
            
        print "Applying Rules"
        for gr in self.rules:
            if not gr.late:
                gr.ApplyRule(self.levels[levelIndex])
        
        print "Make Movements"
        self.levels[levelIndex].MakeMovements()
        
        print "Applying late Rules"
        for gr in self.rules:
            if gr.late:
                gr.ApplyRule(self.levels[levelIndex])
                
        print "Check win Condition"
        winResult = False
        for wc in self.winConditions:
            winResult = winResult or wc.CheckWinCondition(self.levels[levelIndex])
            
        self.levels[levelIndex].FixLegends(self.legends)
        return winResult    
        

class GroupRule(object):
    maxWidth = 30
    maxLoopNumber = 200
    
    def __init__(self, ruleLine, objects, layers):
        print "####################"
        print "### Group Rule"
        print "####################"
        
        ruleLine = ruleLine.strip()
        
        self.add = False
        if ruleLine[0] == "+":
            self.add = True
            ruleLine = ruleLine[1:].strip()
        
        self.random = False
        self.late = False
        outsideKeywords = ruleLine.split("[")[0].strip().split(" ")
        if "random" in outsideKeywords:
            if self.add:
                print "Random keyword must be at the first rule of the group"
            else:
                self.random = True
        elif "late" in outsideKeywords:
            if self.add:
                print "late keyword must be at the first rule of the group"
            else:
                self.late = True
        
        tempRuleLines = []
        if "..." in ruleLine:
            tempString = " "
            for _ in range(self.maxWidth):
                tempRuleLines.append(ruleLine.replace("...", tempString))
                tempString = tempString + "| "
            
            tempLines = ruleLine.split("|")
            tempString = ""
            for l in tempLines:
                if l.strip() != "...":
                    tempString = tempString + l + "|"
            
            tempString = tempString[:-1]
            tempRuleLines = [tempString] + tempRuleLines
        else:
            tempRuleLines.append(ruleLine)
        
        self.rules = []
        for r in tempRuleLines:
            self.rules.append(Rule(r, objects, layers))
    
    def ApplyRule(self, level):
        arrayOfIndeces = range(len(self.rules))
        if self.random:
            random.shuffle(arrayOfIndeces)
        
        for i in arrayOfIndeces:
            if self.rules[i].ApplyRule(level):
                if self.random:
                    break
    
    def __str__(self):
        tempString = ""
        if self.late:
            tempString = tempString + "late "
        if self.random:
            tempString = tempString + "random "
        
        for r in self.rules:
            tempString = tempString + r.__str__() + "\n"
        
        return tempString

class Rule(object):
    outsideKeywords = ["right", "down"]
    reversedKeywords = ["left", "up"]
    
    def __init__(self, ruleLine, objects, layers):
        tempSides = ruleLine.strip().split("->")
        if len(tempSides) != 2:
            print "There must be only two sides lhs and rhs"
        
        tempTuples = tempSides[0].strip().split(']')
        tempTuples = filter(None, tempTuples)
        #Detecting late and direction of the rule
        tempWords = tempTuples[0].split('[')[0].split(" ")
        tempWords = filter(None, tempWords)
        tempReversed = False
        for line in tempWords:
            line = line.strip().lower()
            if line in self.outsideKeywords:
                self.ruleDirection = line
            if line in self.reversedKeywords:
                self.ruleDirection = self.outsideKeywords[self.reversedKeywords.index(line)]
                tempReversed = True
        
        print "----LHS----"
        #Handling the LHS
        self.lhs = []
        for t in tempTuples:
            tempPart = filter(None, t.split("["))[-1].strip().lower()
            self.lhs.append(Tuple(tempPart, tempReversed, objects, layers))
         
        tempTuples = tempSides[1].strip().split(']')
        tempTuples = filter(None, tempTuples)
        
        print "----RHS----"
        #Handling the RHS
        self.rhs = []
        for t in tempTuples:
            tempPart = filter(None, t.split("["))[-1].strip().lower()
            self.rhs.append(Tuple(tempPart, tempReversed, objects, layers))
       
    def ApplyRule(self, level):
        matchingTuplesPoints = []
        
        for t in self.lhs:
            matchingTuplesPoints.append(t.GetAMatchingPosition(self.ruleDirection, level))

        if None in matchingTuplesPoints:
            return False
        
        #Apply Rule itself
        xDir = 0
        yDir = 0
        if self.ruleDirection == "right":
            xDir = 1
        elif self.ruleDirection == "down":
            yDir = 1
        
        for i in range(len(matchingTuplesPoints)):
            for s in range(len(self.lhs[i].layers)):
                mapLayer = level.map[matchingTuplesPoints[i].y + yDir * s][matchingTuplesPoints[i].x + xDir * s]
                finalLayer = copy.deepcopy(self.rhs[i].layers[s])
                
                for l in range(len(mapLayer.objects)):
                    if finalLayer.actions[l] == "no":
                        finalLayer.objects[l] = None
                    elif finalLayer.actions[l] == "randomdir":
                        finalLayer.actions[l] = Tuple.actions[random.randint(0, 3)]
                    elif finalLayer.actions[l] == "stationary":
                        finalLayer.actions[l] = None
                    
                    if mapLayer.objects[l] != "background":
                        mapLayer.objects[l] = finalLayer.objects[l]
                        mapLayer.actions[l] = finalLayer.actions[l]
                    
        return True
    
    def __str__(self):
        tempString = ""
        tempString = tempString + self.ruleDirection
        
        for t in self.lhs:
            tempString = tempString + "[" + t.__str__() + "]"
        tempString = tempString + "->"
        
        for t in self.rhs:
            tempString = tempString + "[" + t.__str__() + "]"
        
        return  tempString

class Tuple(object):
    actions = ["left", "right", "up", "down", "randomdir", "action", "no", "stationary"]
    
    def __init__(self, ruleLine, isReversed, objects, layers):
        tempLines = ruleLine.split('|');
        if isReversed:
            tempLines.reverse()
        self.layers = [None] * len(tempLines)
        for i in range(len(tempLines)):
            tempParts = tempLines[i].strip().split(" ")
            self.layers[i] = MapLayer(layers)
            tempLayerNum = -1
            for part in reversed(tempParts):
                part = part.strip().lower()
                if part in self.actions:
                    if tempLayerNum != -1:
                        self.layers[i].actions[tempLayerNum] = part
                    else:
                        print "you must have object after " + part
                    tempLayerNum = -1
                else:
                    tempLayerNum = Helper.GetLayerNumber(part.strip().lower(), layers)
                    if tempLayerNum != -1:
                        if self.layers[i].objects[tempLayerNum] is None:
                            self.layers[i].objects[tempLayerNum] = part
                        else:
                            print "Can't have " + part + " at same layer with " + self.layers[i].objects[tempLayerNum]
                    else:
                        if len(part.strip().lower()) > 0:
                            print "you must define " + part + " in collision layer"
    
    def GetAMatchingPosition(self, ruleDirection, level):
        matchingPoints = []
             
        if ruleDirection == "right":
            if len(self.layers) > level.width:
                return None
            for x in range(level.width - len(self.layers)):
                for y in range(level.height):
                    if self.CheckMatch(x, y, ruleDirection, level):
                        matchingPoints.append(Point(x, y))
        elif ruleDirection == "down":
            if len(self.layers) > level.height:
                return None
            for x in range(level.width - len(self.layers)):
                for y in range(level.height - len(self.layers)):
                    if self.CheckMatch(x, y, ruleDirection, level):
                        matchingPoints.append(Point(x, y))
        
        if len(matchingPoints) > 0:
            randomIndex = random.randint(0, len(matchingPoints) - 1)
            return matchingPoints[randomIndex]
        else:
            return None
    
    def CheckMatch(self, x, y, ruleDirection, level):
        tempMatch = True;
        xM = 0
        yM = 0
        if ruleDirection == "right":
            xM = 1
        elif ruleDirection == "down":
            yM = 1
        
        for s in range(len(self.layers)):
            for o in range(len(self.layers[0].objects)):
                if self.layers[s].objects[o] is not None:
                    currentAction = self.layers[s].actions[o]
                    if currentAction != "no":
                        if self.layers[s].objects[o] == level.map[y + s * yM][x + s * xM].objects[o]:
                            if currentAction == "randomdir":
                                currentAction = self.actions[random.randint(0, 3)]
                            if currentAction == "stationary":
                                tempMatch = tempMatch and level.map[y + s * yM][x + s * xM].actions[o] is None
                            elif currentAction is None:
                                tempMatch = tempMatch
                            else:
                                tempMatch = tempMatch and currentAction == level.map[y + s * yM][x + s * xM].actions[o]
                        else:
                            return False
                    else:
                        tempMatch = tempMatch and self.layers[s].objects[o] != level.map[y + s * yM][x + s * xM].objects[o]
        return tempMatch
    
    def __str__(self):
        tempString = ""
        for i in range(len(self.layers)):
            if(len(tempString) > 0):
                tempString = tempString + " |"
            for o in range(len(self.layers[i].objects)):
                if(self.layers[i].actions[o] is not None or self.layers[i].objects[o] != "background"):
                    if(self.layers[i].actions[o] is not None):
                        tempString = tempString + self.layers[i].actions[o]
                    if(self.layers[i].objects[o] is not None):
                        tempString = tempString + " " + self.layers[i].objects[o] + " "
                else:
                    tempString = tempString + " "
        return tempString

class CollisionLayer(object):
    def __init__(self, collisionLine, objects):
        print "####################"
        print "### Collision Layer"
        print "####################"
        #removing any spaces
        collisionLine = collisionLine.replace(" ", "")
        #get the objects id in the line
        self.objects = collisionLine.split(",")
        self.objects = filter(None, self.objects)
        for i in range(len(self.objects)):
            self.objects[i] = self.objects[i].lower()
        #Background should be on separate layer
        if "background" in self.objects and len(self.objects) > 1:
            print "Background should be on separate layer"
        #Checking for errors
        for colObjID in self.objects:
            if not Helper.CheckObjectExist(colObjID, objects):
                print colObjID + " is not defined in Object Section"
    
    def CheckCollision(self, testObjectsID):
        tempNames = []
        for testObjID in testObjectsID:
            if testObjID in self.objects:
                tempNames.append(testObjID)
        return len(tempNames) > 1
    
    def __str__(self):
        tempString = self.objects[0]
        for i in range(1, len(self.objects)):
            tempString = tempString + ", " + self.objects[i]
        return tempString

class Level(object):
    directionMap = {}
    
    def __init__(self, levelLines, legends, layers):
        print "####################"
        print "### Level"
        print "####################"
        levelLines = filter(None, levelLines)
        self.width = len(levelLines[0].strip())
        self.height = len(levelLines)
        #Initializing the map
        self.map = [[None for _ in range(self.width)] for _ in range(self.height)]
        for x in range(self.width):
            for y in range(self.height):
                character = levelLines[y][x].lower()
                self.map[y][x] = MapLayer(layers)
                self.map[y][x].id = character
                tempObjects = Helper.GetObjectsIDFromLegend(character, legends)
                for objID in tempObjects:
                    tempLayerNumber = Helper.GetLayerNumber(objID, layers)
                    if tempLayerNumber != -1:
                        self.map[y][x].objects[tempLayerNumber] = objID
                    else:
                        print objID + " doesn't exist in collision layer"
    
    def GetIndexFromObjectID(self, objectID):
        indeces = []
        for x in range(self.width):
            for y in range(self.height):
                if objectID in self.map[y][x].objects:
                    indeces.append(Point(x, y))
        return indeces
    
    def MakeMovements(self):
        stillAction = True
        while stillAction:
            stillAction = False
            for x in range(self.width):
                for y in range(self.height):
                    for i in range(len(self.map[y][x].objects)):
                        if self.map[y][x].actions[i] is not None:
                            stillAction = stillAction or self.ApplyAction(x, y, i)
        
        #Clearing the Actions Left
        for x in range(self.width):
            for y in range(self.height):
                for i in range(len(self.map[y][x].actions)):
                    self.map[y][x].actions[i] = None
                        
    def ApplyAction(self, x, y, index):
        movingTuple = self.directionMap[self.map[y][x].actions[index]]
        newLocation = Point(x + movingTuple.x, y + movingTuple.y)
        #Check Boundaries
        if newLocation.x < 0:
            newLocation.x = 0
        if newLocation.x > self.width - 1:
            newLocation.x = self.width - 1
        if newLocation.y < 0:
            newLocation.y = 0
        if newLocation.y > self.height - 1:
            newLocation.y = self.height - 1
        #CheckNewLocationForCollision
        if self.map[newLocation.y][newLocation.x].objects[index] is not None:
            return False
        
        self.map[newLocation.y][newLocation.x].objects[index] = self.map[y][x].objects[index]
        self.map[y][x].objects[index] = None
        self.map[y][x].actions[index] = None
        return True
        
    
    def FixLegends(self, legends):
        for x in range(self.width):
            for y in range(self.height):
                character = Helper.GetIdObjectsFromLegend(self.map[y][x].objects, legends)
                self.map[y][x].id = character
    
    def __str__(self):
        tempString = "";
        for y in range(self.height):
            for x in range(self.width):
                tempString = tempString + self.map[y][x].__str__()
            tempString = tempString + "\n"
        return tempString
        
class MapLayer(object):
    def __init__(self, layers):
        self.id = ""
        self.objects = [None] * len(layers);
        self.actions = [None] * len(layers);
        tempLayerNumber = Helper.GetLayerNumber("background", layers)
        if tempLayerNumber != -1:
            self.objects[tempLayerNumber] = "background"
        else:
            print "Background doesn't exist in collision layer"
    
    def __str__(self):
        return self.id

class WinCondition(object):
    winCodes = ["no", "some", "all"]
    
    def __init__(self, winLine, objects):
        print "####################"
        print "### Win Condition"
        print "####################"
        tempObjects = filter(None, winLine.split(" "))
        if len(tempObjects) <= 1:
            print "Missing object to operate on"
            return
        #Adding Operand
        if tempObjects[0].lower() in self.winCodes:
            self.operand = tempObjects[0].lower()
        else:
            print tempObjects[0].lower() + " is not a valid operand"
        #Adding Objects
        self.objects = []
        self.objects.append(tempObjects[1].lower())
        if len(tempObjects) > 3:
            if "on" == tempObjects[2].lower():
                self.objects.append(tempObjects[3].lower())
            else:
                print "on is not exist in correct position"
        else:
            print "missing 3rd Object"
        #Checking all objects are defined in Objects
        for objID in self.objects:
            if not Helper.CheckObjectExist(objID, objects):
                print objID + " is not defined in object section"
        
    def CheckWinCondition(self, level):
        gameWin = False
        for x in range(level.width):
            for y in range(level.height):
                firstObjectIndex = Helper.SearchObjectsArray(self.objects[0], level.map[y][x].objects)
                secondObjectIndex = -9
                if len(self.objects) > 1:
                    secondObjectIndex = Helper.SearchObjectsArray(self.objects[1], level.map[y][x].objects)
                if self.operand == "no":
                    gameWin = True
                    if firstObjectIndex != -1:
                        if secondObjectIndex == -9:
                            return False
                        if secondObjectIndex >= 0:
                            return False
                elif self.operand == "some":
                    gameWin = False
                    if firstObjectIndex != -1:
                        if secondObjectIndex == -9:
                            return True
                        elif secondObjectIndex >= 0:
                            return True
                elif self.operand == "all":
                    gameWin = True
                    if firstObjectIndex != -1:
                        if secondObjectIndex == -1:
                            return False
        return gameWin
        
    def __str__(self):
        tempString = self.operand + " " +self.objects[0]
        if len(self.objects) > 1:
            tempString = tempString + " on " + self.objects[1]
        return tempString

#Handling Map Legends

class Legend(object):
    def __init__(self, legendLine, objects):
        print "####################"
        print "### Legend"
        print "####################"
        splitted = legendLine.split("=")
        #Check only one = operator per line
        if len(splitted) > 2:
            print "Only one = operator per legend"
        self.id = splitted[0].replace(" ", "").lower()
        if len(self.id) > 1:
            print "Only one letter for lhs of legend, replacing " + self.id + " by " + self.id[0]
            self.id = self.id[0]
        #Now making the rhs of the legend
        tempObjects = filter(None, splitted[1].split(" "))
        self.objects = []
        if len(tempObjects) % 2 == 1:
            for i in range(len(tempObjects)):
                if i % 2 == 1 and not "and" in tempObjects[i]:
                    print "Error instead of an and there is " + tempObjects[i]
                elif i % 2 == 0:
                    if not "and" == tempObjects[i]:
                        self.objects.append(tempObjects[i].lower())
                    else:
                        print "There is an and instead of name"
        else:
            print "Wrong number of ands"
        #Checking the rhs is in objects
        for objID in self.objects:
            if not Helper.CheckObjectExist(objID, objects):
                print objID + " doesn't exist in the object layer"
    
    def __str(self):
        tempString = self.id + " = " + self.objects[0]
        for i in range(1, len(self.objects)):
            tempString = tempString + " and " + self.objects[i]
        return tempString

class GameObject(object):
    def __init__(self, objectLines):
        print "####################"
        print "### Game Object"
        print "####################"
        self.id = objectLines[0].strip().lower()
        #will be replaced by actual color from an Color Enum based on graphical library
        self.color = objectLines[1].strip().lower()
    
    def __str(self):
        return self.id + " is " + self.color
    
class Point(object):
    def __init__(self, x = 0, y = 0):
        self.x = x;
        self.y = y;
    
    def __str__(self):
        return "(" + self.x.__str__() + ", " + self.y.__str__() + ")"
       
class Helper(object):
    @staticmethod
    def CheckObjectExist(testObjID, objects):
        for obj in objects:
            if testObjID == obj.id:
                return True
        return False
    
    @staticmethod
    def CheckLegendExist(testLegendID, legends):
        for leg in legends:
            if testLegendID == leg.id:
                return True
        return False
    
    @staticmethod
    def GetObjectsIDFromLegend(testLegendID, legends):
        for leg in legends:
            if testLegendID == leg.id:
                return leg.objects
        return []
    
    @staticmethod
    def GetIdObjectsFromLegend(objects, legends):
        returnID = ""
        numberOfMatching = 0
        
        for leg in legends:
            allFound = True
            for o in leg.objects:
                if o not in objects:
                    allFound = False
                    break
            if allFound:
                if len(leg.objects) >= numberOfMatching:
                    returnID = leg.id
                    numberOfMatching = len(leg.objects)
        
        return returnID
                
    @staticmethod
    def SearchObjectsArray(objectID, objects):
        for i in range(len(objects)):
            if objectID == objects[i]:
                return i
        return -1                
    
    @staticmethod
    def GetLayerNumber(objectID, layers):
        for i in range(len(layers)):
            if objectID in layers[i].objects:
                return i
        return -1
    
    @staticmethod
    def CheckUniqueLegends(legends):
        for leg in legends:
            if Helper.CheckLegendExist(leg.id, legends):
                return False
        return True
    
    @staticmethod
    def CheckUniqueObjects(objects):
        for obj in objects:
            if Helper.CheckObjectExist(obj.id, objects):
                return False
        return True
        