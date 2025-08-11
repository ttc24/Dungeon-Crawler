# Performance

## Profiling setup
A synthetic run of `DungeonBase.play_game` was profiled with `cProfile`. The
floor size was increased to 50x50 and player input was automated for 1000
moves to exercise dungeon generation and movement while avoiding combat.

## Before optimization
- Total function calls: 86,649 in 0.044s
- `generate_dungeon`: 0.009s self time
- `generate_room_name`: 0.014s cumulative

## After optimization
- Total function calls: 92,520 in 0.044s
- `generate_dungeon`: 0.008s self time
- `generate_room_name`: 0.013s cumulative

## Changes
- Room name generation now reuses static adjective and noun lists instead of
  recreating them for each call.
- JSON data loaders for enemies, bosses, and riddles are memoized to avoid
  repeated disk parsing.
