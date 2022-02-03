# pygame_platformer_2

The second pygame platformer!

In this version:
- You can't go through walls
- You can climb up walls [(but you sometimes teleport to the bottom?)](https://github.com/sillypantscoder/pygame_platformer_2/issues/3)
- TNT and explosions!
- Danger items!

**Read this first before playing the game:**

To play the game, run the program. Then click on "Go" and click on "default.py". You will appear in a randomly generated world.

1. You are the red square. You can walk around with the arrow keys, and up to jump.
2. Walking into red TNT blocks will explode them. A big danger icon will appear whenever there is an explosion.
3. Occasionally, explosions will drop danger items ![](danger.png). These are small items that fall to the ground. You can pick them up by walking on them
4. There is a minimap in the top left corner. You can try to use that to get around.
5. To the right of the minimap is some text showing how many danger items you have collected.
6. Occasionally, spawners will spawn around the map. These look just like you, but they are blue instead of red. The spawners will spawn lots of monsters, which are green, and exploding monsters, which are light green.
7. Normal monsters will drop lots of danger items when they despawn, which shouldn't take very long. Exploding monsters will explode when they despawn, producing a big danger icon and possibly a danger item.
8. If you have 10 or more danger items, you can press space at any time to cause an explosions at your space. The explosion is just like any other explosion and will create a big danger icon and possibly another danger item.
9. (New!) If you have 15 or more danger items, you can click anywhere on the screen to immediately spawn a spawner there. This is a good way to get danger items, but I'm not sure if it's actually worth it yet.


New: The super non-glitchy update

- Now doesn't tick entities that are off the screen. This can be weird (e.g. falling items pause in midair), but it is MUCH less glitchy.

Maybe I am going to have an option in the future for whether to tick offscreen entities?
