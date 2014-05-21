from engine import *

objectLines = ["Background", "GREEN", " ", "Target", "DarkBlue", "", "Wall", "BROWN", "    ", "Player", "Blue", " ", "Crate", "Orange"]
legendLines = [". = Background", "# = Wall", "P = Player", "* = Crate", "@ = Crate and Target", "O = Target"]
layerLines = ["Background", "Target", "Player, Wall, Crate"]
ruleLines = [" down[down Player | Crate] -> [down Player | down Crate ]", "+up[UP Player | Crate] -> [UP Player | UP Crate]", "+left[left Player | Crate] -> [left Player | left Crate]", "+right[right Player | Crate] -> [right Player | right Crate]"]
winLines = ["All Crate on Target"]
levelLines = ["#########", "#.......#", "#.....@.#", "#.P.*.O.#", "#.......#", "#.......#", "#########"]

e = Engine(objectLines, legendLines, layerLines, ruleLines, winLines, levelLines)

print " "
print "----------------------"
print "--- Testing"
print "----------------------"
print e.levels[0]

print e.ProcessInput("right", 0)
print e.levels[0]

print e.ProcessInput("right", 0)
print e.levels[0]

print e.ProcessInput("right", 0)
print e.levels[0]