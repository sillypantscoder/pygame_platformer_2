# pygame_platformer_2

The second pygame platformer!

In this version:
- You can't go through walls
- Bad monsters!
- TNT and explosions!
- Danger items!
- Allays and water!

## Read this first before playing the game:

To play the game, run "python3 main.py" in the terminal. When the window pops up, click on "Play", and then "New world" and click on "landscape.py". You will appear in a randomly generated world.

1. You are the red square. You can walk around with the arrow keys, and up to jump.
2. Walking into TNT blocks will explode them. A big danger icon will appear whenever there is an explosion.
3. Occasionally, explosions will drop danger items. These are small items that fall to the ground. You can pick them up by walking on them.
4. There is a minimap in the top left corner. You can mouse over the minimap to expand it.
5. To the right of the minimap is some text showing how many danger items you have collected.
6. Light falls from the top. Most blocks block light, creating shadows.
7. Monsters, which are green, spawn in dark areas. They burn in sunlight.
8. Monsters slowly take damage if you lure them out into the sunlight. They slowly get more and more red and less and less green as they get damaged. When they reach 0 health points, they die, dropping a danger item.
9. Water blocks are blue, and flowing water is light blue and textured. Water flows down, left, and right. You can swim with the up arrow key.

### Danger items
- Danger items fall out of monsters when they die, and they occasionally fall out of explosions.
- If you have 10 or more danger items, you can press space at any time to use them to cause an explosion at your space. The explosion is just like any other explosion and will create a big danger icon and possibly another danger item.
- Creating explosions at your space is useful because it not only pushes monsters away, it also sends you flying upwards.
- If you press Z, you can use up 5 danger items to randomly create a spawner somewhere across the map.

### Allays
- Press the W key to create an Allay Spawner. The Allay Spawner will spawn lots of Allays.
- Allays also spawn randomly across the map.
- Allays try to get to the nearest danger item and pick it up for you.
- Allays will also attack nearby monsters and try to kill them.

## Level editor

- If you want to make your own level, you can! Type in "python3 level_editor.py" instead of "python3 main.py".
- Click the blocks at the top to select them, then click in the world to place the selected block.
- Close the window to save your level.
- Now, to play in the world, start the game (or Zombie Apocalypse Mode) and select "Load save file >" to play in your custom world!

## Zombie Apocalypse Mode
Ok, maybe I should explain "zombieapocalypse.py".

- To run the game in Zombie Apocalypse Mode, type in "python3 zombieapocalypse.py" instead of "python3 main.py".
- New "Auto Apocalypse" option: When enabled, a bot plays the game instead of you.
- There are no Danger or Score items, just Gem items. Explosions drop Gem items instead of danger items.
- Monsters spawn frequently around the map. When they despawn, they drop Gem items.
- Monsters try to pathfind towards you. If they touch you, your health decreases.
- If your health runs out, you die.
- It is _very hard_. Have fun! :D

## Extensions

- Extensions can add, remove, or modify blocks, generators, and textures.
- Install an extension by adding the extension package to the "extensions" folder.
- Then, start the game and press "Extensions" to manage your extensions.
- There are 3 preset extensions: Lava, Realistic, and Generative.
- Lava adds lava. Realistic upgrades the "landscape" generator. Generative adds the "Text" generator, which uses some text as the world, and the "Image" generator, which uses an image as the world.
- You can make your own extension! If you want to, check out [my zip file editor](https://github.com/sillypantscoder/pygame_zip), and look in the "extensions" folder for hints. Have fun! :)

## Updating the game

- To update the game, run "sh update.sh".
- It will show you the list of available updates, then ask you whether you want to update.
- Type "y" and press Enter to update.
