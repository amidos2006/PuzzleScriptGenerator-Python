# PuzzleScriptGenerator-Python

Same puzzle script engine written in python with another engine to solve puzzles then generate level then generate rules

<b>Latest version:</b> v0.25

### How to run action
- Make object from Class Engine
- Call ProcessInput and give it action you want ("left", "right", "up", "down", "action") and which level you want to play it from levels array
- You can print the level and see the effect (Check __init__.py script)

### Target
- Puzzle Script Engine working in Python
- Engine to solve any level and detects its difficulty
- Engine generating levels for any rules increasing in difficulty
- Engine generating game rules suitable and playable with each other

### Version v0.25
- Puzzle Script Engine Working in Python
- Only basic operation the parser don't translate relative stuff
- Late rule is a group rule so either the whole group is late or not
- Random rule is a group rule so either choose a random rule to apply or not
- No undo supported
