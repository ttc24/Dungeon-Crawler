Gameplay Guide
==============

Use the numbered menu to explore rooms, fight monsters, visit shops, and descend deeper into the dungeon.

At any time choose **8. Show Map** to display the dungeon grid. The map marks your location with ``@``, visited rooms with ``.``, and unexplored or blocked rooms with ``#``.

Progress is automatically saved whenever you clear a floor.

Random Events
-------------
As you explore, floors can trigger random events:

* **MerchantEvent** – a travelling merchant appears and opens the shop.
* **PuzzleEvent** – solve a riddle for a chance to earn extra gold.
* **TrapEvent** – an unexpected hazard deals damage to the player.

These events add variety and can occur on any floor.

Enemy Intents
-------------
Foes now telegraph their behaviour each round.  Every enemy rolls one of
three intents—Aggressive, Defensive or Unpredictable—weighted by its
archetype.  The selected intent is announced before the action resolves,
for example::

    Goblin steadies a heavy strike…
    Beetle curls into its shell.

Pay attention to these tells to decide when to Defend or attempt a Feint.

