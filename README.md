# pygame_platformer_2

The second pygame platformer!

In this version:
- You can't go through walls
- You can climb up walls [(but you sometimes teleport to the bottom?)](https://github.com/sillypantscoder/pygame_platformer_2/issues/3)
- TNT and explosions!
- Danger items!
- Allays and water!

## Read this first before playing the game:

To play the game, run "sh play.sh" in the terminal, and then type "play". When the window pops up, click on "Go" and click on "random.py". You will appear in a randomly generated world.

1. You are the red square. You can walk around with the arrow keys, and up to jump.
2. Walking into red TNT blocks will explode them. A big danger icon will appear whenever there is an explosion.
3. Occasionally, explosions will drop danger items. These are small items that fall to the ground. You can pick them up by walking on them
4. There is a minimap in the top left corner. You can try to use that to get around.
5. To the right of the minimap is some text showing how many danger items you have collected.
6. Occasionally, spawners will spawn around the map. These look just like you, but they are blue instead of red. The spawners will spawn lots of monsters, which are green, and exploding monsters, which are light green.
7. Normal monsters will drop lots of danger items when they despawn, which shouldn't take very long. Exploding monsters will explode when they despawn, producing a big danger icon and possibly a danger item. Exploding monsters also drop score items, which you can use to increase your score.
8. Water blocks are blue, and flowing water is light blue and textured. Water flows down, left, and right. You can swim with the up arrow key.

### Danger items
- If you have 10 or more danger items, you can press space at any time to use them to cause an explosion at your space. The explosion is just like any other explosion and will create a big danger icon and possibly another danger item.
- If you have 15 or more danger items, you can click anywhere on the screen to immediately spawn a spawner there. This is a good way to get danger items and score items.
- Score items are green, with a big plus on them, and picking one up will increase your score.
- If you press Z, you can use up 5 danger items to randomly create a spawner somewhere across the map.

### Allays
- Press the W key to create an Allay Spawner. The Allay Spawner will spawn lots of Allays.
- Allays try to get to the nearest Item and pick it up for you.

## Level editor

- If you want to make your own level, you can! Type in "leveleditor" instead of "play".
- Click the blocks at the top to select them, then click in the world to place the selected block.
- Close the window to save. (You can open it up back again by typing "leveleditor" again.)
- Now, to play in the world, start the game (or Zombie Apocalypse Mode) and turn off "Generate new world". Then click Go to play in your custom world!

## Zombie Apocalypse Mode
Ok, maybe I should explain "zombieapocalypse.py".

- To run the game in Zombie Apocalypse Mode, type in "zombie" instead of "play".
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
- Then, start the game and press "Extensions" to manage your extensions.
- There are 3 preset extensions: Lava, Realistic, and Generative.
- Lava adds lava. Realistic upgrades the "landscape" generator. Generative adds the "Text" generator, which uses some text as the world, and the "Image" generator, which uses an image as the world.
- You can make your own extension! If you want to, check out [my zip file editor](https://github.com/sillypantscoder/pygame_zip), and look in the "extensions" folder for hints. Have fun! :)

## Updating the game

- To update the game, type "sh play.sh" to enter the platformer terminal, then type "update".