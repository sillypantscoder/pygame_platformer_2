import math
import random
import json

BOARDSIZE = [30, 30]

WORLD = [[0 for x in range(BOARDSIZE[1])] for x in range(BOARDSIZE[0])]

logicalHeight = math.floor(BOARDSIZE[1] / 2)
height = math.floor(BOARDSIZE[1] / 2)
logicalBedrockHeight = math.floor(BOARDSIZE[1] / 6)
bedrockHeight = math.floor(BOARDSIZE[1] / 6)

for x in range(BOARDSIZE[0]):
    # Height
    height += random.choice([-1, 0, 1])
    if height < logicalHeight: height += random.choice([0, 0, 1])
    else: height -= random.choice([0, 0, 1])
    for i in range(height):
        WORLD[x][(BOARDSIZE[1] - 1) - i] = random.choices([1, 2], weights=[10, 1], k=1)[0]
    # Bedrock Height
    bedrockHeight += random.choice([-1, 0, 1])
    if bedrockHeight < logicalBedrockHeight: bedrockHeight += random.choice([0, 0, 1])
    else: bedrockHeight -= random.choice([0, 0, 1])
    for i in range(bedrockHeight):
        WORLD[x][(BOARDSIZE[1] - 1) - i] = 3

f = open("world.json", "w")
f.write(json.dumps(WORLD).replace("], [", "],\n ["))
f.close()
