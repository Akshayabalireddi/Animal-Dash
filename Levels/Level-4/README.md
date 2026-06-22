# Lion World - Level 4 (Standalone VSCode Project)

A complete, self-contained Lion World game that runs independently in VSCode!

## Quick Start

1. **Open this folder in VSCode**
   - File → Open Folder → select this "Level-4" folder

2. **Install pygame** (if not already installed)
   ```bash
   pip install pygame
   ```

3. **Run the game**
   - Press `Ctrl+F5` (Run Python File) in VSCode, or
   - Open terminal and type: `python main.py`

## What's Inside

📁 **Files in this folder:**
- `main.py` - Complete game engine + Lion World (runnable!)
- `lion_world.py` - Level data (platforms, coins, traps, etc.)
- `README.md` - This file

## How to Play

| Control | Action |
|---------|--------|
| Arrow Keys / WASD | Move left/right |
| Space / Up / W | Jump (double jump mid-air) |
| ESC | Pause/Resume |
| Space (when dead) | Retry from checkpoint |

## Game Overview

### Lion World - Level 4: The Final Challenge

This is the **hardest level** of Animal Dash featuring:

- ✅ **70+ platforms** (static and moving)
- ✅ **Hunter AI** chasing you throughout the level
- ✅ **20+ traps** strategically placed
- ✅ **130+ coins** to collect
- ✅ **4 checkpoints** for respawning
- ✅ **3 health pickups** at difficult sections
- ✅ **Intense difficulty progression**

### Level Layout

| Section | Challenge | Length |
|---------|-----------|--------|
| **A** - Savannah Plains | Intro - medium gaps | x 0-1300 |
| **B** - Rocky Outcrops | Vertical climbing | x 1300-3100 |
| **C** - Gauntlet Alley | **HARDEST** - dense traps | x 3100-4820 |
| **D** - Final Sprint | Hunter pressure | x 4820-7200 |

### Hunter System

The **Hunter** is an AI opponent that:
- Spawns behind you and chases throughout the level
- **Gets closer** when you hit traps or take damage
- **Falls back** when you collect coins or reach checkpoints
- **Shoots projectiles** periodically for extra challenge
- **Catches you = Game Over** (respawn at checkpoint)

The visual danger bar above the Hunter shows how close they are to catching you.

### Game Systems

✅ **Physics & Movement**
- Gravity: 1900 pixels/s²
- Player speed: 380 px/s
- Double jump mechanic

✅ **Health System**
- Start with 3 HP
- Hazards/projectiles: -1 HP each
- Health pickups: +1 HP
- Lose all HP: Game Over

✅ **Collectibles**
- 130+ coins = main collectibles
- Collecting coins makes Hunter fall back
- All coins are obtainable

✅ **Checkpoints**
- 4 checkpoints throughout
- Reaching = new respawn point
- Reaching = Hunter falls back further

✅ **Visual Effects**
- Smooth camera following
- Particle effects on coin pickup
- Camera shake on damage
- Flashing invincibility frames

## Asset Requirements

For the game to display properly, you need these assets in a folder called `assets/sprites/lion/`:

```
assets/sprites/lion/
├── bg.png              (background image)
├── platform.png        (platform texture)
├── lion.png            (player sprite)
├── environment.png     (decoration sprites)
├── hunter.png          (hunter sprite)
└── trap.png            (trap sprite)
```

**If assets are missing:**
- Missing assets are replaced with bright magenta placeholder boxes
- The game is still fully playable
- Error messages appear in the terminal

## File Structure Explained

### main.py (Complete Game)
Contains everything needed to play:
- Game engine (physics, collisions, camera)
- UI system (HUD, pause menu)
- All game objects (Player, Hunter, Platforms, etc.)
- Main game loop

### lion_world.py (Level Data)
Contains only the Lion World level layout:
- Platform positions and sizes
- Coin locations
- Trap locations  
- Checkpoint positions
- Health pickup locations
- Decoration sprites

This separation keeps the code organized and makes it easy to modify the level without touching the engine.

## Customization

### Change Player Speed
Edit in `main.py`, line ~20:
```python
class Player:
    SPEED = 380  # Change this value
```

### Change Hunter Difficulty
Edit in `main.py`:
- `Hunter.SHOOT_INTERVAL_MIN/MAX` - How often hunter shoots
- `Hunter.speed` - How fast hunter moves
- `Hunter.lag` - Initial distance behind player

### Modify Level Layout
Edit `lion_world.py`:
- `plats` - Platform positions
- `traps` - Trap locations
- `coins` - Coin positions
- `checkpoints` - Checkpoint positions
- `health_pickups` - Health pickup positions

## Troubleshooting

**Game won't start?**
- Make sure pygame is installed: `pip install pygame`
- Check Python version: 3.7+

**Assets not showing (magenta boxes)?**
- Create `assets/sprites/lion/` folder relative to this folder
- Add the required sprite files

**Game too fast/slow?**
- Check your FPS setting in `main.py` line 14
- Default is 60 FPS

**Hunter too easy/hard?**
- Edit Hunter parameters in `main.py` around line 550

## Have Fun!

This is the ultimate test of platforming skill and nerves. The Hunter creates constant pressure - manage your checkpoints wisely and time your jumps perfectly!

Good luck! 🎮

---

**Created:** Level 4 Standalone VSCode Project
**Game:** Animal Dash
**Level:** Lion World (Final Challenge)
