# -*- coding: utf-8 -*-
"""Lion World (Level 4) Level Data - Standalone Version"""

# Screen height constant
H = 720

def p(world, name):
    """Asset path helper."""
    return f"assets/sprites/{world}/{name}"


def make_lion_data():
    """Lion World (Hardest – savannah theme + Hunter AI).
    Assets: lion/bg.png, lion/platform.png, lion/env.png, lion/trap.png,
            lion/hunter.png (Hunter AI only)
    Collectibles: drawn procedurally (coins). NO assets from duck/deer/whale.
    """
    GY = H - 80

    # ── Platforms ──────────────────────────────────────────────────────────────
    # Section A (x 0-1500): savannah plains – medium gaps, traps on ground
    # Section B (x 1500-3200): rocky outcrop climbs – narrow platforms
    # Section C (x 3200-5000): gauntlet alley – dense traps + moving platforms
    # Section D (x 5000-7000): final sprint under hunter pressure
    plats = [
        # Section A – savannah plains, moderate gaps
        (180,  GY-130, 220, 24),   # A1
        (480,  GY-170, 200, 24),   # A2
        (760,  GY-130, 220, 24),   # A3 back down
        (1040, GY-180, 200, 24),   # A4
        (1300, GY-130, 240, 24),   # A5 rest
        # Section B – rocky outcrops (smaller platforms, larger vertical range)
        (1620, GY-170, 180, 24),   # B1
        (1870, GY-240, 180, 24),   # B2 rise
        (2120, GY-310, 180, 24),   # B3 high
        (2380, GY-240, 180, 24),   # B4 dip
        (2620, GY-170, 200, 24),   # B5
        (2860, GY-250, 180, 24),   # B6
        (3080, GY-170, 220, 24),   # B7 rest
        # Section C – tight gauntlet (traps between every platform)
        (3380, GY-200, 170, 24),   # C1
        (3620, GY-270, 170, 24),   # C2
        (3860, GY-340, 170, 24),   # C3 peak
        (4100, GY-270, 170, 24),   # C4
        (4340, GY-200, 170, 24),   # C5
        (4580, GY-270, 170, 24),   # C6
        (4820, GY-200, 190, 24),   # C7 rest
        # Section D – final pressure run
        (5100, GY-230, 170, 24),   # D1
        (5340, GY-300, 170, 24),   # D2
        (5580, GY-370, 170, 24),   # D3 high
        (5820, GY-300, 170, 24),   # D4
        (6060, GY-230, 170, 24),   # D5
        (6300, GY-300, 170, 24),   # D6
        (6540, GY-230, 200, 24),   # D7
        (6780, GY-160, 260, 24),   # D8 pre-goal
    ]
    
    mplats = [
        # (x, y, w, h, x2, y2, speed)
        (1460, GY-130, 160, 24, 1600, GY-130, 130),   # A→B
        (3220, GY-140, 150, 24, 3360, GY-240, 130),   # B→C vertical
        (4900, GY-140, 150, 24, 5080, GY-140, 145),   # C→D
        (5980, GY-170, 150, 24, 6180, GY-170, 135),   # D mid
        (6700, GY-150, 150, 24, 6900, GY-150, 140),   # D final
    ]
    
    # ── Coins – placed above platforms, guide the player ─────────────────────
    coins = (
        # A section
        [(220,GY-165),(280,GY-165),(340,GY-165)] +      # A1
        [(520,GY-205),(580,GY-205),(640,GY-205)] +      # A2
        [(800,GY-165),(860,GY-165),(920,GY-165)] +      # A3
        [(1080,GY-215),(1140,GY-215)] +                  # A4
        [(1340,GY-165),(1400,GY-165),(1460,GY-165)] +   # A5
        # B rocky outcrops
        [(1660,GY-205),(1720,GY-205)] +                  # B1
        [(1910,GY-275),(1970,GY-275)] +                  # B2
        [(2160,GY-345),(2220,GY-345),(2280,GY-345)] +   # B3 peak triple
        [(2420,GY-275),(2480,GY-275)] +                  # B4
        [(2660,GY-205),(2720,GY-205)] +                  # B5
        [(2900,GY-285),(2960,GY-285)] +                  # B6
        [(3120,GY-205),(3180,GY-205),(3240,GY-205)] +   # B7
        # C gauntlet
        [(3420,GY-235),(3480,GY-235)] +                  # C1
        [(3660,GY-305),(3720,GY-305)] +                  # C2
        [(3900,GY-375),(3960,GY-375),(4010,GY-375)] +   # C3 peak triple reward
        [(4140,GY-305),(4200,GY-305)] +                  # C4
        [(4380,GY-235),(4440,GY-235)] +                  # C5
        [(4620,GY-305),(4680,GY-305)] +                  # C6
        [(4860,GY-235),(4920,GY-235),(4980,GY-235)] +   # C7
        # D final
        [(5140,GY-265),(5200,GY-265)] +                  # D1
        [(5380,GY-335),(5440,GY-335)] +                  # D2
        [(5620,GY-405),(5680,GY-405),(5720,GY-405)] +   # D3 peak
        [(5860,GY-335),(5920,GY-335)] +                  # D4
        [(6100,GY-265),(6160,GY-265)] +                  # D5
        [(6340,GY-335),(6400,GY-335)] +                  # D6
        [(6580,GY-265),(6640,GY-265),(6700,GY-265)] +   # D7
        [(6820,GY-195),(6900,GY-195),(6980,GY-195)]     # D8 → goal
    )
    
    # ── Traps – placed intentionally in gaps and on platform approaches ───────
    # On ground between platforms (lion/trap.png)
    # Placed where the hunter pressure makes them hard to dodge
    traps = [
        # A section – introduce traps, one per gap
        (400,  GY-40, 38),    # between A1 and A2
        (680,  GY-40, 38),    # between A2 and A3
        (960,  GY-40, 38),    # between A3 and A4
        (1220, GY-40, 38),    # between A4 and A5
        # B outcrops – tighter, traps on ledge approaches
        (1780, GY-40, 38),    # B1 approach
        (2040, GY-40, 38),    # B2→B3
        (2560, GY-40, 38),    # B4→B5
        (2780, GY-40, 38),    # B5→B6
        # C gauntlet – dense, every gap has a trap
        (3270, GY-40, 40),    # before C1
        (3540, GY-40, 40),    # C1→C2
        (3780, GY-40, 40),    # C2→C3
        (4020, GY-40, 40),    # C3→C4
        (4260, GY-40, 40),    # C4→C5
        (4500, GY-40, 40),    # C5→C6
        (4740, GY-40, 40),    # C6→C7
        # D final – traps under high-pressure hunter chase
        (5000, GY-40, 40),    # C→D
        (5240, GY-40, 40),    # D1→D2
        (5480, GY-40, 40),    # D2→D3
        (5760, GY-40, 40),    # D3→D4
        (5980, GY-40, 40),    # D4→D5
        (6220, GY-40, 40),    # D5→D6
        (6460, GY-40, 40),    # D6→D7
    ]
    
    checkpoints = [
        (1300, GY),    # end of A
        (3080, GY),    # end of B / before gauntlet
        (4820, GY),    # end of C / before final
        (6540, GY),    # D7 near goal
    ]
    
    health_pickups = [
        (2125, GY-350),   # B3 peak reward
        (3865, GY-380),   # C3 peak reward
        (5585, GY-410),   # D3 peak reward
    ]
    
    # ── Decors – ONLY lion/env.png, savannah themed ────────────────────────────
    # env.png: acacia trees, rocks, savannah bushes
    # Placed to frame sections, vary heights for natural savannah silhouette
    decors = [
        # Intro savannah A
        (60,  GY-95,  p("lion","env.png"), 95),
        (150, GY-70,  p("lion","env.png"), 70),
        (240, GY-110, p("lion","env.png"),110),
        (360, GY-80,  p("lion","env.png"), 80),
        (460, GY-100, p("lion","env.png"),100),
        (560, GY-75,  p("lion","env.png"), 75),
        (660, GY-90,  p("lion","env.png"), 90),
        (760, GY-110, p("lion","env.png"),110),
        (880, GY-80,  p("lion","env.png"), 80),
        (980, GY-100, p("lion","env.png"),100),
        (1080,GY-75,  p("lion","env.png"), 75),
        (1180,GY-95,  p("lion","env.png"), 95),
        (1280,GY-110, p("lion","env.png"),110),
        (1380,GY-80,  p("lion","env.png"), 80),
        # Rocky outcrops B – sparser, more dramatic
        (1560,GY-100, p("lion","env.png"),100),
        (1700,GY-85,  p("lion","env.png"), 85),
        (1880,GY-110, p("lion","env.png"),110),
        (2040,GY-90,  p("lion","env.png"), 90),
        (2200,GY-75,  p("lion","env.png"), 75),
        (2360,GY-100, p("lion","env.png"),100),
        (2560,GY-110, p("lion","env.png"),110),
        (2720,GY-85,  p("lion","env.png"), 85),
        (2880,GY-95,  p("lion","env.png"), 95),
        (3040,GY-80,  p("lion","env.png"), 80),
        # Gauntlet C – flanking the tight platforms
        (3240,GY-100, p("lion","env.png"),100),
        (3420,GY-85,  p("lion","env.png"), 85),
        (3600,GY-110, p("lion","env.png"),110),
        (3780,GY-80,  p("lion","env.png"), 80),
        (3960,GY-100, p("lion","env.png"),100),
        (4140,GY-90,  p("lion","env.png"), 90),
        (4320,GY-75,  p("lion","env.png"), 75),
        (4520,GY-105, p("lion","env.png"),105),
        (4700,GY-85,  p("lion","env.png"), 85),
        (4880,GY-100, p("lion","env.png"),100),
        # Final section D – dramatic silhouettes
        (5060,GY-110, p("lion","env.png"),110),
        (5240,GY-80,  p("lion","env.png"), 80),
        (5440,GY-100, p("lion","env.png"),100),
        (5640,GY-90,  p("lion","env.png"), 90),
        (5820,GY-110, p("lion","env.png"),110),
        (6020,GY-75,  p("lion","env.png"), 75),
        (6200,GY-100, p("lion","env.png"),100),
        (6400,GY-85,  p("lion","env.png"), 85),
        (6600,GY-110, p("lion","env.png"),110),
        (6800,GY-90,  p("lion","env.png"), 90),
        (6960,GY-80,  p("lion","env.png"), 80),
    ]
    
    return {
        "id":            "lion1",
        "world":         "lion",
        "width":         7500,
        "bg":            p("lion","bg.png"),
        "platform_tile": p("lion","platform.png"),
        "spawn":         (80, GY-68),
        "goal":          (7200, GY-80),
        "platforms":     plats,
        "moving_platforms": mplats,
        "coins":         coins,
        "collectibles":  [],          # no cross-world collectibles
        "hazards":       [],          # traps handle all hazards
        "traps":         traps,
        "water":         [],
        "checkpoints":   checkpoints,
        "health_pickups":health_pickups,
        "decors":        decors,
        "moving_decors": [],
    }
