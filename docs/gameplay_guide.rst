Gameplay Guide
==============

Use the numbered menu to explore rooms, fight monsters, visit shops, and descend deeper into the dungeon.

At any time choose **8. Show Map** to display the dungeon grid. The map marks your location with ``@``, visited rooms with ``.``, and unexplored or blocked rooms with ``#``.

Progress is automatically saved whenever you clear a floor.

Classes, Guilds and Races
-------------------------
Characters grow through three axes of customization.  A **class** supplies a
stat block and unique abilities that consume stamina.  For instance, the
Barbarian begins with 130 health, 12 attack power and can unleash *Rage*
``(30)`` or a sweeping *Whirlwind* ``(40)``.  Druids wield nature magic through
*Wild Shape* ``(35)`` and *Entangle* ``(20)`` while maintaining balanced stats.

Joining a **guild** applies permanent perks.  The **Shadow Brotherhood** grants
+4 attack power and reduces all skill costs by 5 stamina, turning members into
efficient assassins.  Other guilds focus on raw power, magical prowess or
supportive talents.

Selecting a **race** provides innate bonuses.  Tieflings gain +2 attack power
and the *Infernal resistance* trait, whereas Dragonborn receive +2 health,
+2 attack power and the *Draconic breath* trait.

Boss Encounters
---------------
Each floor culminates in a boss battle against a foe unique to that level.
Bosses telegraph their intentions so observant players can react to heavy
attacks or defensive postures. Defeating a boss now awards the entire loot
table associated with that encounter, guaranteeing meaningful rewards.

Special Events
--------------
To break up the routine of combat, each floor draws exactly one signature event
from a curated pool:

* **Shrine Gauntlet** – fight successive waves to earn blessings.
* **Puzzle Chamber** – solve puzzles or riddles for unique gear.
* **Escort Mission** – protect an NPC for a substantial reward.

These events introduce variety and appear once per floor.

Enemy Intents
-------------
Foes now telegraph their behaviour each round.  Every enemy rolls one of
three intents—Aggressive, Defensive or Unpredictable—weighted by its
archetype.  The selected intent is announced before the action resolves,
for example::

    Goblin steadies a heavy strike…
    Beetle curls into its shell.

Pay attention to these tells to decide when to Defend or attempt a Feint.

Aggressive telegraphs often precede a heavy attack that deals roughly
50% more damage.  Unpredictable intents may unleash wild attacks which
suffer a 20% accuracy penalty but have a small chance to inflict double
damage.

High Floor Debuffs
------------------
Beginning on Floor 10, the dungeon introduces persistent penalties that
accumulate with each descent. Every new floor adds its own challenges while
retaining all previous debuffs.

* **Floor 10** – healing effects are halved and a relentless sandstorm reduces
  vision to four tiles, persisting on later floors.
* **Floor 11** – trap density rises and enemies adopt a Disarm Stance capable
  of riposting, on top of all Floor 10 effects.
* **Floor 12 – “Hunted”**
  - *Blood Torrent* – Minor DoT that persists through healing; enemies gain
    increased vision and aggro radius while active. Stacks to three, each
    intensifying the trail and damage. Counter with Scent-mask Spray or
    Absorbent Gel; bandaging ends the DoT but leaves a faint trail for three
    turns.
  - *Compression Sickness* – After teleportation, blinking or using launch pads
    suffer −10% speed, −10% accuracy and increased fumble chance for five
    turns. Waiting a turn halves the remaining duration; an Anti-Nausea Draught
    removes it.
* **Floor 13 – “Anti-Magic”**
  - *Mana Lock* – Spells cost 50% more resources and cleanse or dispel effects
    have a 25% chance to fail. Mundane kits and consumables are unaffected, and
    a **Suppression Ring** can mitigate the effect at the risk of overheating.
  - *Hex of Dull Wards* – Shields and blocks are 30% less effective and critical
    hits cannot pierce them. Purifying or resetting wards, or opting for
    offense, counters it.
* **Floor 14 – “Entropy”**
  - *Entropic Debt* – Each action adds a stack dealing 1% of max HP per turn, up
    to 10 stacks. Skipping or bracing consumes two stacks. Venting or draining
    the debt into a nearby totem or using an **Entropy Vent Stone** clears
    stacks but may spawn an add.
  - *Spiteful Reflection* – 20% chance to bounce any new debuff back to its
    applier, including the player. Use proxies, pets or throwables to avoid
    self-infliction.
* **Floor 15 – “Pestilence”**
  - *Brood Bloom* – Timed infection that spawns a Broodling on expiry and
    reapplies a weaker stack. Cleansing only delays the spawn; fire dispatches
    Broodlings quickly.
  - *Miasma Carrier* – Entering a room applies a one-turn −50% healing received
    aura to nearby allies and enemies. **Filter Masks** or **Air Filters**
    consume on entry to negate it; suppression rings protect only their
    bearer.
* **Floor 16 – “Time Weirdness”**
  - *Temporal Lag* – 15% chance your last action repeats on the next turn with a
    new target, refunding resources but wasting the turn. Taking short,
    deliberate turns or consuming an **Anchor** clears it.
  - *Haste Dysphoria* – Speed buffs invert into a penalty if total haste exceeds
    25%. Cap haste or purge to avoid the slowdown.
* **Floor 17 – “Oaths & Curses”**
  - *Fester Mark* – Healing beyond 50% overheal converts to a DoT dealing 5% of
    the overheal each turn for five turns. Small, frequent heals or cleansing
    mitigate it.
  - *Soul Tax* – Each kill while taxed reduces your primary stat by one for 10
    turns but increases loot chance. Donate at an altar to remove stacks.
* **Floor 18 – “Broadcast Finale”**
  - *Spotlight* – Entering a room pings your location on the floor map; elites
    home in with +10% damage. A jammer or brief stealth breaks the ping.
  - *Audience Fatigue* – Using the same ability three or more times in five
    turns applies −10% damage/healing for three turns, stacking to −40%. Rotate
    skills or use a Rewrite consumable to clear it.

