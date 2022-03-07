# pygame_platformer_2

The second pygame platformer!

In this version:
- You can't go through walls
- You can climb up walls [(but you sometimes teleport to the bottom?)](https://github.com/sillypantscoder/pygame_platformer_2/issues/3)
- TNT and explosions!
- Danger items!
- Allays and water!

## Read this first before playing the game:

To play the game, run "python3 main.py" in the terminal. Then click on "Go" and click on "default.py". You will appear in a randomly generated world.

1. You are the red square. You can walk around with the arrow keys, and up to jump.
2. Walking into red TNT blocks will explode them. A big danger icon will appear whenever there is an explosion.
3. Occasionally, explosions will drop danger items. These are small items that fall to the ground. You can pick them up by walking on them
4. There is a minimap in the top left corner. You can try to use that to get around.
5. To the right of the minimap is some text showing how many danger items you have collected.
6. Occasionally, spawners will spawn around the map. These look just like you, but they are blue instead of red. The spawners will spawn lots of monsters, which are green, and exploding monsters, which are light green.
7. Normal monsters will drop lots of danger items when they despawn, which shouldn't take very long. Exploding monsters will explode when they despawn, producing a big danger icon and possibly a danger item. Exploding monsters also drop score items, which you can use to increase your score.
8. (New!) Water blocks are blue, and flowing water is light blue. Water flows down, left, and right. You (and Allays) can swim.

### Danger items
- If you have 10 or more danger items, you can press space at any time to cause an explosions at your space. The explosion is just like any other explosion and will create a big danger icon and possibly another danger item.
- If you have 15 or more danger items, you can click anywhere on the screen to immediately spawn a spawner there. This is a good way to get danger items and score items.
- If you press Z, you can use 5 danger items to randomly create a spawner somewhere across the map.

### Allays
- Press the W key to create an Allay Spawner. The Allay Spawner will spawn lots of Allays.
- Allays try to get to the nearest Item and pick it up for you.

## Zombie Apocalypse Mode
Ok, maybe I should explain "zombieapocalypse.py".

- To run the game in Zombie Apocalypse Mode, run "python3 zombieapocalypse.py" instead of "python3 main.py".
- New "Auto Apocalypse" option: When enabled, a bot plays the game instead of you.
- Always uses its own customized generator, similar to the "Grid" generator.
- There are no Danger or Score items, just Gem items. Explosions drop Gem items instead of danger items.
- Monsters spawn frequently around the map. When they despawn, they drop Gem items.
- Monsters try to pathfind towards you. If they touch you, your health decreases.
- If your health runs out, you die.
- You can't click or press Z to spawn Spawners.
- It is _very hard_. Have fun! :D

## Extensions
New: Extensions!!!

- Extensions can add, remove, or modify blocks, generators, and textures.
- Install an extension by adding the extension package to the "extensions" folder.
- Then, start the game and press "Extensions" to manage your extensions. Have fun!