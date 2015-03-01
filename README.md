# PuzzleScriptGenerator-Python
This project is shifted towards https://github.com/amidos2006/PuzzleScript-PCG where it utilise the main engine of PuzzleScript as it is proved that it is faster than this one and have more capabilities.

Same puzzle script engine written in python with another engine to solve puzzles then generate level then generate rules

<b>Latest version:</b> v0.25

### How to run action
- Make object from Class Engine
- Call ProcessInput and give it action you want ("left", "right", "up", "down", "action") and which level you want to play it from levels array
- You can print the level and see the effect (Check init.py script)

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

### Version v0.3
- Puzzle Script Engine now supports undo and can be disabled
- Puzzle Script Engine logging while solving can be disabled
- Puzzle Script Engine fixing legends can be disabled
- Fixing bug with Puzzle Script Engine in Applying Rules in Rule class
- Auto solver module added
- Auto solver gets all possible unique solutions
