# -*- coding: utf-8 -*-
"""
Animal Dash  –  Flappy-Bird-style duck game
Controls:  A/D or ←/→  move  |  W / SPACE / ↑  jump  |  P  pause  |  R  restart  |  ESC  quit
"""
import pygame, sys, random, math, os

pygame.init()

# ── Window ─────────────────────────────────────────────────────────────────────
SW, SH   = 1280, 720
FPS      = 60
screen   = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Animal Dash")
clock    = pygame.time.Clock()

ASSET_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Colours ────────────────────────────────────────────────────────────────────
WHITE  = (255,255,255); BLACK  = (0,0,0);     RED    = (220,50,50)
GREEN  = (50,200,80);   GOLD   = (255,210,0); CYAN   = (0,220,255)
PURPLE = (180,60,220);  ORANGE = (255,140,0); DKGREEN= (30,140,30)
SKY    = (110,185,255); PIPE_G = (60,180,60); PIPE_D = (30,110,30)

# ── Physics ────────────────────────────────────────────────────────────────────
GRAVITY     = 0.38
JUMP_VEL    = -13
DBL_JUMP    = -11
MOVE_SPEED  = 4.0
WORLD_SPEED = 2.2
GROUND_Y    = SH - 100
# 25s midpoint: 2.2 units/frame × 60fps × 25s ≈ 3300. With acceleration buffer → 3500
CHECKPOINT_DIST = 4000

# ── Asset loader ───────────────────────────────────────────────────────────────
def load_img(name, size=None):
    path = os.path.join(ASSET_DIR, name)
    img  = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, size) if size else img

def load_anim_frames(folder, total, size):
    """Load pre-processed alpha frames from frames_alpha/"""
    frames = []
    for i in range(total):
        p = os.path.join(ASSET_DIR, folder, f"frame_{i:03d}.png")
        if os.path.exists(p):
            img = pygame.image.load(p).convert_alpha()
            frames.append(pygame.transform.scale(img, size))
    return frames

# ── Font cache — never call SysFont inside a draw loop ─────────────────────────
_font_cache: dict = {}
def get_font(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.SysFont("segoeui", size, bold=True)
    return _font_cache[size]

# ── Font helper ────────────────────────────────────────────────────────────────
def txt(surf, text, size, x, y, col=WHITE, anchor="topleft", shadow=True):
    f = get_font(size)
    if shadow:
        s = f.render(text, True, BLACK)
        r = s.get_rect(**{anchor:(x+2,y+2)})
        surf.blit(s, r)
    s = f.render(text, True, col)
    r = s.get_rect(**{anchor:(x,y)})
    surf.blit(s, r)
    return r

# ── Particle ───────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, col, vx=None, vy=None, life=40, r=5):
        self.x, self.y, self.col = x, y, col
        self.vx = vx if vx is not None else random.uniform(-3, 3)
        self.vy = vy if vy is not None else random.uniform(-4, -1)
        self.life = self.max_life = life
        self.r = r
    def update(self):
        self.x += self.vx; self.y += self.vy
        self.vy += 0.18;   self.life -= 1
    def draw(self, surf):
        a = int(255 * self.life / self.max_life)
        r = max(1, int(self.r * self.life / self.max_life))
        # draw directly — no per-frame surface allocation
        pygame.draw.circle(surf, self.col, (int(self.x), int(self.y)), r)
    def dead(self): return self.life <= 0

# ── Score popup ────────────────────────────────────────────────────────────────
class Popup:
    def __init__(self, x, y, text, col=GOLD):
        self.x, self.y, self.text, self.col = x, y, text, col
        self.life = self.max_life = 55
    def update(self): self.y -= 1.2; self.life -= 1
    def draw(self, surf):
        f = get_font(22)
        s = f.render(self.text, True, self.col)
        s.set_alpha(int(255 * self.life / self.max_life))
        surf.blit(s, s.get_rect(center=(int(self.x), int(self.y))))
    def dead(self): return self.life <= 0

# ── Gem ────────────────────────────────────────────────────────────────────────
GEM_KINDS = [(GOLD,"coin",10),(CYAN,"crystal",25),(PURPLE,"diamond",50),(GREEN,"emerald",30)]

class Gem:
    R = 12
    def __init__(self, x, y):
        self.wx, self.y = x, y     # wx = world x
        self.base_y = y
        self.col, self.name, self.value = random.choice(GEM_KINDS)
        self.angle = random.uniform(0,360)
        self.bob   = random.uniform(0, math.pi*2)
        self.alive = True
    def update(self):
        self.bob   += 0.07
        self.y      = self.base_y + math.sin(self.bob)*5
        self.angle += 3
    def sx(self, cam): return int(self.wx - cam)
    def draw(self, surf, cam):
        x, y, r = self.sx(cam), int(self.y), self.R
        # simple rotating diamond, no per-frame surface
        pts = [(x+math.cos(math.radians(self.angle+i*90))*r,
                y+math.sin(math.radians(self.angle+i*90))*r) for i in range(4)]
        pygame.draw.polygon(surf, self.col, pts)
        pygame.draw.polygon(surf, WHITE,
            [pts[0], (pts[0][0]*.6+pts[1][0]*.4, pts[0][1]*.6+pts[1][1]*.4),
                     (pts[0][0]*.6+pts[3][0]*.4, pts[0][1]*.6+pts[3][1]*.4)])
    def rect(self, cam):
        return pygame.Rect(self.sx(cam)-self.R, self.y-self.R, self.R*2, self.R*2)

# ── Health Potion ──────────────────────────────────────────────────────────────
class HealthPotion:
    R = 14
    COL_BODY  = (220,  60,  80)
    COL_TOP   = (255, 120, 140)
    COL_SHINE = (255, 200, 210)
    COL_CORK  = (200, 160,  80)

    def __init__(self, wx, y):
        self.wx     = wx
        self.base_y = y
        self.y      = float(y)
        self.bob    = random.uniform(0, math.pi * 2)
        self.pulse  = 0.0
        self.alive  = True

    def update(self):
        self.bob   += 0.06
        self.y      = self.base_y + math.sin(self.bob) * 5
        self.pulse  = (self.pulse + 3) % 360

    def sx(self, cam): return int(self.wx - cam)

    def draw(self, surf, cam):
        x  = self.sx(cam)
        y  = int(self.y)
        r  = self.R
        # bottle body — no per-frame surface
        pygame.draw.ellipse(surf, self.COL_BODY,  (x-r,   y-r,   r*2,   r*2))
        pygame.draw.ellipse(surf, self.COL_TOP,   (x-r+3, y-r+3, r*2-6, r-4))
        pygame.draw.ellipse(surf, self.COL_SHINE, (x-r+5, y-r+5, r//2, r//3))
        pygame.draw.rect(surf, self.COL_CORK, (x-4, y-r-10, 8, 10), border_radius=3)
        pygame.draw.rect(surf, WHITE, (x-5, y-4, 10, 4), border_radius=2)
        pygame.draw.rect(surf, WHITE, (x-2, y-7,  4, 10), border_radius=2)

    def rect(self, cam):
        return pygame.Rect(self.sx(cam)-self.R, self.y-self.R, self.R*2, self.R*2)


# ── Checkpoint (finish line) ───────────────────────────────────────────────────
class Checkpoint:
    W      = 20
    FLAG_W = 80
    FLAG_H = 50

    def __init__(self, wx):
        self.wx    = wx
        self.pulse = 0.0
        # pre-bake beam surface once — no per-frame allocation
        self._beam = pygame.Surface((80, GROUND_Y), pygame.SRCALPHA)
        for bx in range(80):
            dist = abs(bx - 40) / 40
            a = int(60 * max(0, 1 - dist ** 1.4))
            if a > 0:
                pygame.draw.line(self._beam, (255, 230, 80, a), (bx, 0), (bx, GROUND_Y))

    def sx(self, cam): return int(self.wx - cam)

    def draw(self, surf, cam):
        x = self.sx(cam)
        self.pulse = (self.pulse + 2.5) % 360
        p = abs(math.sin(math.radians(self.pulse)))

        # beam — cached, just set alpha
        self._beam.set_alpha(int(80 + 160 * p))
        surf.blit(self._beam, (x + self.W//2 - 40, 0))

        # chequered pole
        pygame.draw.rect(surf, (200, 200, 200), (x, 0, self.W, GROUND_Y))
        pygame.draw.rect(surf, (240, 240, 240), (x+2, 0, 5, GROUND_Y))
        sq = 18
        for row in range(GROUND_Y // sq + 1):
            for col in range(self.W // sq + 1):
                if (row + col) % 2 == 0:
                    rx = x + col * sq
                    ry = row * sq
                    rw = min(sq, x + self.W - rx)
                    rh = min(sq, GROUND_Y - ry)
                    if rw > 0 and rh > 0:
                        pygame.draw.rect(surf, (30, 30, 30), (rx, ry, rw, rh))

        # waving flag
        flag_col = (255, int(160 + 80*p), 0)
        pts_top  = [(x + self.W, 15)]
        pts_bot  = [(x + self.W, 15 + self.FLAG_H)]
        for i in range(10):
            fx   = x + self.W + i * (self.FLAG_W // 9)
            wave = int(math.sin(math.radians(self.pulse * 1.5 + i * 36)) * 10)
            pts_top.append((fx, 15 + wave))
            pts_bot.append((fx, 15 + self.FLAG_H + wave))
        pygame.draw.polygon(surf, flag_col, pts_top + list(reversed(pts_bot)))
        pygame.draw.lines(surf, (160, 100, 0), False, pts_top, 2)

        txt(surf, "FINISH!", 28, x + self.W//2 + self.FLAG_W//2,
            15 + self.FLAG_H + 10, GOLD, anchor="midtop")

    def rect(self, cam):
        return pygame.Rect(self.sx(cam), 0, self.W + 10, GROUND_Y)


# ── Pipe obstacle (Flappy Bird style) ─────────────────────────────────────────
PIPE_W   = 80
GAP_H    = 220    # vertical gap between top and bottom pipe
MIN_TOP  = 80     # minimum top-pipe height

class Pipe:
    def __init__(self, wx):
        self.wx    = wx
        gap_top    = random.randint(MIN_TOP, GROUND_Y - GAP_H - 40)
        self.top   = gap_top          # bottom of top pipe
        self.bot   = gap_top + GAP_H  # top of bottom pipe
        self.alive = True
        self.scored= False            # did the player already earn a point?

    def sx(self, cam): return int(self.wx - cam)

    def draw(self, surf, cam):
        x = self.sx(cam)
        w = PIPE_W
        cap_h = 30

        # ── top pipe ──────────────────────────────────────────────────────────
        if self.top > 0:
            # body gradient (left bright → right dark)
            pygame.draw.rect(surf, (55, 170, 55),  (x,    0, w,    self.top))
            pygame.draw.rect(surf, (35, 110, 35),  (x+w-16,0, 16, self.top))
            pygame.draw.rect(surf, (95, 210, 95),  (x,    0, 10,  self.top))
            # inner shadow line
            pygame.draw.line(surf, (20, 90, 20), (x+w-17, 0), (x+w-17, self.top), 2)
            # horizontal ring marks every 80px
            for ry in range(40, self.top, 80):
                pygame.draw.rect(surf, (40,130,40), (x-1, ry, w+2, 7))
                pygame.draw.rect(surf, (80,200,80), (x,   ry, w,   3))
            # cap (wider, rounded)
            pygame.draw.rect(surf, (55,175,55),  (x-10, self.top-cap_h, w+20, cap_h), border_radius=5)
            pygame.draw.rect(surf, (30,105,30),  (x+w-4, self.top-cap_h, 14, cap_h), border_radius=4)
            pygame.draw.rect(surf, (100,220,100),(x-10, self.top-cap_h, 12, cap_h), border_radius=4)
            # rivet bolts on cap
            for bx in [x-4, x+w//2-4, x+w+2]:
                pygame.draw.circle(surf, (20,80,20),  (bx+4, self.top-cap_h//2), 5)
                pygame.draw.circle(surf, (80,180,80), (bx+3, self.top-cap_h//2-1), 2)

        # ── bottom pipe ───────────────────────────────────────────────────────
        body_h = GROUND_Y - self.bot
        if body_h > 0:
            pygame.draw.rect(surf, (55, 170, 55),  (x,    self.bot, w,    body_h))
            pygame.draw.rect(surf, (35, 110, 35),  (x+w-16,self.bot, 16, body_h))
            pygame.draw.rect(surf, (95, 210, 95),  (x,    self.bot, 10,  body_h))
            pygame.draw.line(surf, (20, 90, 20), (x+w-17, self.bot), (x+w-17, self.bot+body_h), 2)
            for ry in range(self.bot+40, self.bot+body_h, 80):
                pygame.draw.rect(surf, (40,130,40), (x-1, ry, w+2, 7))
                pygame.draw.rect(surf, (80,200,80), (x,   ry, w,   3))
            # cap
            pygame.draw.rect(surf, (55,175,55),  (x-10, self.bot, w+20, cap_h), border_radius=5)
            pygame.draw.rect(surf, (30,105,30),  (x+w-4, self.bot, 14, cap_h), border_radius=4)
            pygame.draw.rect(surf, (100,220,100),(x-10, self.bot, 12, cap_h), border_radius=4)
            for bx in [x-4, x+w//2-4, x+w+2]:
                pygame.draw.circle(surf, (20,80,20),  (bx+4, self.bot+cap_h//2), 5)
                pygame.draw.circle(surf, (80,180,80), (bx+3, self.bot+cap_h//2-1), 2)

    def top_rect(self, cam):
        x = self.sx(cam)
        return pygame.Rect(x+4, 0, PIPE_W-8, self.top)

    def bot_rect(self, cam):
        x = self.sx(cam)
        return pygame.Rect(x+4, self.bot, PIPE_W-8, GROUND_Y-self.bot)

    def off_screen(self, cam):
        return self.sx(cam) < -PIPE_W - 20

# ── Floating platform ──────────────────────────────────────────────────────────
class Platform:
    H = 22
    def __init__(self, wx, y, w, tile):
        self.wx, self.y, self.w, self.tile = wx, y, w, tile
    def sx(self, cam): return int(self.wx - cam)
    def draw(self, surf, cam):
        x = self.sx(cam)
        tw = self.tile.get_width()
        for tx in range(0, self.w, tw):
            surf.blit(self.tile, (x+tx, int(self.y)))
    def rect(self, cam):
        return pygame.Rect(self.sx(cam), int(self.y), self.w, self.H)
    def off_screen(self, cam): return self.sx(cam) < -self.w - 20

# ── Background ────────────────────────────────────────────────────────────────
class Background:
    """
    duckbackground.png is the main background, tiled and parallax-scrolled.
    duck enviroment.png is a semi-transparent midground layer on top.
    Both are driven by cam so movement feels grounded.
    """
    def __init__(self, bg, env):
        self.bg  = bg    # duckbackground.png — primary scene
        self.env = env   # duck enviroment.png — foreground scenery

        # Pre-bake a cloud surface at startup (drawn between bg layers)
        self._cloud_surf = None
        self._cloud_scroll = 0.0
        self._build_clouds()

    def _build_clouds(self):
        # Soft puffy clouds drawn once onto a wide surface, then scrolled
        cw = SW * 4
        self._cloud_surf = pygame.Surface((cw, SH), pygame.SRCALPHA)
        rng = random.Random(42)  # deterministic seed for consistent look
        for _ in range(18):
            cx = rng.randint(0, cw)
            cy = rng.randint(30, GROUND_Y - 220)
            cr = rng.randint(28, 65)
            alpha = rng.randint(160, 230)
            # 4-circle fluffy cloud
            for ox, oy, or_ in [(-cr//2, cr//3, int(cr*0.85)),
                                  (0,       0,    cr),
                                  (cr//2,  cr//3, int(cr*0.85)),
                                  (0,      -cr//3, int(cr*0.6))]:
                s = pygame.Surface((or_*2+4, or_*2+4), pygame.SRCALPHA)
                pygame.draw.circle(s, (248, 252, 255, alpha), (or_+2, or_+2), or_)
                self._cloud_surf.blit(s, (cx+ox-or_-2, cy+oy-or_-2))

    def draw(self, surf, cam):
        bg_w = self.bg.get_width()

        # ── Primary background — duckbackground.png tiles at 30% parallax ───
        bx = int(-cam * 0.30) % bg_w
        for x in range(-bg_w, SW + bg_w, bg_w):
            surf.blit(self.bg, (x + bx, 0))

        # ── Soft pre-baked cloud overlay at 18% (very slow drift) ────────────
        cw = self._cloud_surf.get_width()
        cx = int(-cam * 0.18) % cw
        surf.blit(self._cloud_surf, (cx - cw, 0))
        surf.blit(self._cloud_surf, (cx,       0))
        surf.blit(self._cloud_surf, (cx + cw,  0))

# ── Duck (player) ─────────────────────────────────────────────────────────────
DUCK_W, DUCK_H = 110, 110
LEFT_LIMIT  = 60          # minimum screen-x for duck's left edge
RIGHT_LIMIT = SW - 200    # maximum screen-x for duck's left edge

class Duck:
    MAX_HP  = 5
    IFRAMES = 80

    def __init__(self, run_frames, jump_frames, companion_img):
        self.run_f   = run_frames
        self.jump_f  = jump_frames
        self.comp_img= companion_img

        # world position
        self.wx  = 300.0
        self.y   = float(GROUND_Y - DUCK_H)
        self.vy  = 0.0

        self.on_ground  = False
        self.jumps_left = 2
        self.hp         = self.MAX_HP
        self.score      = 0
        self.gems       = 0
        self.alive      = True
        self.iframes    = 0
        self.anim_t     = 0.0
        self.squish     = 1.0

        # companion
        self.comp_wx    = self.wx - 100
        self.comp_y     = float(GROUND_Y - DUCK_H)
        self.comp_bob   = 0.0

        self.shield     = False
        self.shield_t   = 0

    # screen-x of duck's left edge
    def sx(self, cam): return int(self.wx - cam)

    def jump(self, particles):
        if self.jumps_left > 0:
            self.vy = JUMP_VEL if self.jumps_left == 2 else DBL_JUMP
            self.jumps_left -= 1
            self.on_ground   = False
            for _ in range(14):
                particles.append(Particle(
                    self.wx - cam_ref[0] + DUCK_W//2,
                    self.y + DUCK_H,
                    (200,230,255),
                    vx=random.uniform(-2.5,2.5),
                    vy=random.uniform(-3.5,0), life=22, r=5))

    def hurt(self, amt, particles):
        if self.iframes > 0:
            return False
        if self.shield:
            self.shield   = False
            self.shield_t = 0
            for _ in range(20):
                particles.append(Particle(
                    self.wx - cam_ref[0] + DUCK_W//2,
                    self.y + DUCK_H//2, CYAN, life=30, r=7))
            return False
        self.hp      = max(0, self.hp - amt)
        self.iframes = self.IFRAMES
        for _ in range(22):
            particles.append(Particle(
                self.wx - cam_ref[0] + DUCK_W//2,
                self.y + DUCK_H//2, RED, life=36, r=8))
        if self.hp <= 0:
            self.alive = False
        return True

    def update(self, move_x, platforms, cam):
        self.iframes = max(0, self.iframes - 1)
        if self.shield_t > 0:
            self.shield_t -= 1
            if self.shield_t <= 0:
                self.shield = False

        # horizontal
        self.wx += move_x
        # screen-space clamping
        screen_x = self.wx - cam
        if screen_x < LEFT_LIMIT:
            self.wx = cam + LEFT_LIMIT
        if screen_x > RIGHT_LIMIT:
            self.wx = cam + RIGHT_LIMIT

        # vertical
        self.vy += GRAVITY
        self.y  += self.vy
        self.anim_t += 0.30

        # squish recovery
        if self.squish < 1.0:
            self.squish = min(1.0, self.squish + 0.07)

        # ground
        prev_on = self.on_ground
        self.on_ground = False
        if self.y >= GROUND_Y - DUCK_H:
            self.y = float(GROUND_Y - DUCK_H)
            if self.vy > 5 and not prev_on:
                self.squish = 0.62
            self.vy = 0
            self.on_ground  = True
            self.jumps_left = 2

        # platforms
        if self.vy >= 0:
            for p in platforms:
                pr    = p.rect(cam)
                feet  = self.y + DUCK_H
                prev_feet = feet - self.vy
                px    = self.wx - cam + DUCK_W//2
                if pr.left < px < pr.right and pr.top < feet <= pr.bottom and prev_feet <= pr.top+6:
                    self.y = p.y - DUCK_H
                    self.vy = 0
                    self.on_ground  = True
                    self.jumps_left = 2

        # ceiling clamp
        if self.y < 0:
            self.y = 0
            self.vy = max(0, self.vy)

        # companion lazy follow
        self.comp_bob += 0.05
        self.comp_wx += (self.wx - 110 - self.comp_wx) * 0.08
        self.comp_y  += (self.y  + math.sin(self.comp_bob)*8 - self.comp_y) * 0.08

    def get_rect(self, cam):
        m = 12
        return pygame.Rect(self.wx - cam + m, self.y + m, DUCK_W - m*2, DUCK_H - m*2)

    def draw(self, surf, cam):
        sx = int(self.wx - cam)
        sy = int(self.y)

        # companion
        cx = int(self.comp_wx - cam)
        cy = int(self.comp_y)
        c  = self.comp_img.copy()
        c.set_alpha(170)
        surf.blit(c, (cx, cy))

        # shield bubble — cached
        if self.shield:
            if not hasattr(self, '_shield_surf'):
                sr = DUCK_W//2 + 16
                ss = pygame.Surface((sr*2+4, sr*2+4), pygame.SRCALPHA)
                pygame.draw.circle(ss, (100,200,255,70),  (sr+2,sr+2), sr)
                pygame.draw.circle(ss, (180,240,255,190), (sr+2,sr+2), sr, 4)
                self._shield_surf = ss
            sr = DUCK_W//2 + 16
            surf.blit(self._shield_surf, (sx+DUCK_W//2-sr-2, sy+DUCK_H//2-sr-2))

        # flicker during iframes
        if self.iframes > 0 and (self.iframes//5)%2==0:
            return

        # pick frame
        if self.on_ground:
            frames = self.run_f
        else:
            frames = self.jump_f
        img = frames[int(self.anim_t) % len(frames)]

        # squish
        if self.squish != 1.0:
            w = int(DUCK_W * (2.0 - self.squish))
            h = int(DUCK_H * self.squish)
            img = pygame.transform.scale(img, (w, h))
            dx, dy = sx - (w-DUCK_W)//2, sy + (DUCK_H-h)
        else:
            dx, dy = sx, sy

        # shadow — cached
        if not hasattr(Duck, '_shadow_surf'):
            sh = pygame.Surface((DUCK_W, 18), pygame.SRCALPHA)
            pygame.draw.ellipse(sh, (0,0,0,70), (0,0,DUCK_W,18))
            Duck._shadow_surf = sh
        surf.blit(Duck._shadow_surf, (sx, sy+DUCK_H-6))

        # blit the duck — no white outline, just the clean sprite
        surf.blit(img, (dx, dy))

# global cam reference so Duck.jump can access it (avoids circular arg passing)
cam_ref = [0.0]

# ── HUD ────────────────────────────────────────────────────────────────────────
def draw_heart(surf, cx, cy, r, col):
    pygame.draw.circle(surf, col, (cx-r//2, cy-r//4), r//2+1)
    pygame.draw.circle(surf, col, (cx+r//2, cy-r//4), r//2+1)
    pygame.draw.polygon(surf, col, [(cx-r,cy-r//4),(cx+r,cy-r//4),(cx,cy+r)])

def draw_hud(surf, duck, speed, hi, checkpoint_wx, cam):
    # ── top glass panel ──────────────────────────────────────────────────────
    # pre-baked — build once and reuse
    if not hasattr(draw_hud, '_panel'):
        p = pygame.Surface((SW, 74), pygame.SRCALPHA)
        p.fill((10, 12, 30, 145))
        pygame.draw.line(p, (80, 120, 200, 80), (0, 73), (SW, 73), 1)
        draw_hud._panel = p
    surf.blit(draw_hud._panel, (0, 0))

    # ── Health bar ───────────────────────────────────────────────────────────
    hbx, hby = 16, 12
    hbw, hbh = 190, 26
    max_hp   = duck.MAX_HP
    t_hp     = duck.hp / max_hp

    # colour: green→yellow→red
    r_col = int(220 * (1 - t_hp) + 50 * t_hp)
    g_col = int(195 * t_hp       + 30 * (1 - t_hp))
    hp_col = (r_col, g_col, 35)

    # pulse when low HP
    pulse_a = 0
    if duck.hp == 1:
        pulse_a = int(abs(math.sin(pygame.time.get_ticks() * 0.008)) * 180)

    # track
    pygame.draw.rect(surf, (45, 15, 15), (hbx, hby, hbw, hbh), border_radius=13)
    # fill
    fill_w = max(0, int(hbw * t_hp))
    if fill_w > 0:
        pygame.draw.rect(surf, hp_col, (hbx, hby, fill_w, hbh), border_radius=13)
        # gloss shine
        pygame.draw.rect(surf, (min(r_col+60,255), min(g_col+60,255), 120),
                         (hbx+3, hby+3, max(1, fill_w-6), hbh//3), border_radius=8)
    # low-HP pulse — draw directly, no surface allocation
    if pulse_a > 0:
        pygame.draw.rect(surf, (min(255, RED[0]), RED[1], RED[2]),
                         (hbx, hby, hbw, hbh), border_radius=13)
    # segment dividers
    seg_w = hbw // max_hp
    for i in range(1, max_hp):
        sx = hbx + i * seg_w
        pygame.draw.line(surf, (0, 0, 0), (sx, hby+2), (sx, hby+hbh-2), 2)
    # border
    pygame.draw.rect(surf, (180, 200, 255), (hbx, hby, hbw, hbh), 2, border_radius=13)

    # HP text
    txt(surf, f"HP  {duck.hp} / {max_hp}", 15, hbx + hbw + 8, hby + 4, (220, 230, 255))
    if duck.shield:
        txt(surf, "SHIELD", 14, hbx + hbw + 76, hby + 4, CYAN)

    # ── Score (centre top) ───────────────────────────────────────────────────
    txt(surf, f"SCORE  {duck.score:07d}", 27, SW//2,  6, GOLD,          anchor="midtop")
    txt(surf, f"BEST   {hi:07d}",         17, SW//2, 37, (180, 190, 220), anchor="midtop")

    # ── Tokens / speed (right) ───────────────────────────────────────────────
    txt(surf, f"TOKENS  {duck.gems}", 21, SW - 16,  8, CYAN,          anchor="topright")
    txt(surf, f"SPD  {speed:.1f}",    17, SW - 16, 36, (160, 240, 160), anchor="topright")

    # ── Level progress bar (bottom of screen) ────────────────────────────────
    pbw, pbx, pby = 440, SW//2 - 220, SH - 30
    dist  = max(0.0, checkpoint_wx - (cam + SW * 0.30))
    done  = max(0, min(pbw, int(pbw * (1.0 - dist / CHECKPOINT_DIST))))

    # track
    pygame.draw.rect(surf, (20, 22, 45), (pbx - 2, pby - 2, pbw + 4, 18), border_radius=9)
    pygame.draw.rect(surf, (30, 35, 60), (pbx, pby, pbw, 14), border_radius=7)
    # fill — gradient green to gold as you approach finish
    prog_t = done / pbw if pbw else 0
    pr = int(60 + 195 * prog_t)
    pg = int(200 - 50 * prog_t)
    pb_col = (pr, pg, 40)
    if done > 0:
        pygame.draw.rect(surf, pb_col, (pbx, pby, done, 14), border_radius=7)
        pygame.draw.rect(surf, (min(pr+60,255), min(pg+60,255), 120),
                         (pbx+2, pby+2, max(1, done-4), 5), border_radius=4)
    # border + labels
    pygame.draw.rect(surf, (100, 120, 200), (pbx, pby, pbw, 14), 1, border_radius=7)
    txt(surf, "START", 11, pbx - 2,     pby - 2, (160, 170, 200), anchor="topright")
    txt(surf, "FINISH", 11, pbx + pbw + 4, pby - 2, GOLD)
    # mini flag
    pygame.draw.line(surf, (180, 180, 180), (pbx + pbw + 4, pby + 14), (pbx + pbw + 4, pby - 4), 2)
    pygame.draw.polygon(surf, GOLD, [(pbx+pbw+4, pby-4), (pbx+pbw+14, pby+1), (pbx+pbw+4, pby+6)])

# ── Ground tiles ───────────────────────────────────────────────────────────────
def draw_ground(surf, cam, tile_img):
    tw = tile_img.get_width()
    ox = int(-cam) % tw

    # deep soil base
    pygame.draw.rect(surf, (100, 65, 30), (0, GROUND_Y, SW, SH - GROUND_Y))
    # mid soil layer
    pygame.draw.rect(surf, (130, 85, 45), (0, GROUND_Y + 18, SW, SH - GROUND_Y - 18))

    # platform tiles along the top edge
    th = tile_img.get_height()
    for x in range(-tw, SW + tw, tw):
        surf.blit(tile_img, (x + ox, GROUND_Y - th // 2))

    # thick grass band
    pygame.draw.rect(surf, (50, 165, 50), (0, GROUND_Y, SW, 16))
    pygame.draw.rect(surf, (75, 210, 70), (0, GROUND_Y, SW, 6))

    # random grass tufts scrolling with ground
    rng = random.Random(int(cam // 40))
    for i in range(30):
        gx = (rng.randint(0, SW + tw) + ox) % (SW + tw) - tw // 2
        gh = rng.randint(6, 14)
        gc = (40 + rng.randint(0,30), 160 + rng.randint(0,40), 40)
        pygame.draw.line(surf, gc, (gx,   GROUND_Y), (gx-3, GROUND_Y - gh), 2)
        pygame.draw.line(surf, gc, (gx+4, GROUND_Y), (gx+7, GROUND_Y - gh), 2)
        pygame.draw.line(surf, gc, (gx+2, GROUND_Y), (gx+2, GROUND_Y - gh - 2), 2)

# ── Left border wall ───────────────────────────────────────────────────────────
# ── Left border wall — pre-baked glow surface ─────────────────────────────────
_border_surf = None
def _build_border():
    global _border_surf
    gw = 36
    _border_surf = pygame.Surface((gw + 4, SH), pygame.SRCALPHA)
    for i in range(gw, 0, -1):
        a = int(90 * (i / gw) ** 1.5)
        pygame.draw.line(_border_surf, (60, 160, 255, a), (i, 0), (i, SH))

def draw_border(surf):
    global _border_surf
    if _border_surf is None:
        _build_border()
    t = pygame.time.get_ticks()
    p = abs(math.sin(t * 0.003))
    _border_surf.set_alpha(int(120 + 100 * p))
    surf.blit(_border_surf, (LEFT_LIMIT - 36, 0))
    pygame.draw.line(surf, (40, 120, 220),  (LEFT_LIMIT,   0), (LEFT_LIMIT,   SH), 4)
    pygame.draw.line(surf, (140, 210, 255), (LEFT_LIMIT+1, 0), (LEFT_LIMIT+1, SH), 1)
    node_col = (int(120 + 120*p), 210, 255)
    for cy in range(60, SH - 60, 70):
        offset = int(math.sin(t * 0.004 + cy * 0.02) * 4)
        pygame.draw.circle(surf, node_col, (LEFT_LIMIT + offset, cy), 5)
        pygame.draw.circle(surf, WHITE,    (LEFT_LIMIT + offset, cy), 2)

# ── Main Game class ────────────────────────────────────────────────────────────
class Game:
    PIPE_INTERVAL = 620    # world units between pipes
    PLAT_INTERVAL = 900
    GEM_INTERVAL  = 300
    BASE_SPEED    = WORLD_SPEED
    MAX_SPEED     = 5.5
    ACCEL         = 0.0008

    def __init__(self):
        self._load_assets()
        self.hi = 0
        self.state = "menu"   # menu | playing | paused | dead | win
        self.reset()

    def _load_assets(self):
        # backgrounds
        raw_bg = load_img("duckbackground.png")
        bg_h   = SH
        bg_w   = int(raw_bg.get_width() * bg_h / raw_bg.get_height())
        self.bg_img = pygame.transform.scale(raw_bg, (bg_w, bg_h))

        raw_env = load_img("duck enviroment.png")
        env_h   = SH
        env_w   = int(raw_env.get_width() * env_h / raw_env.get_height())
        self.env_img = pygame.transform.scale(raw_env, (env_w, env_h))

        self.bg = Background(self.bg_img, self.env_img)

        # pre-bake full-screen overlay surfaces — never allocate during gameplay
        def _make_overlay(r,g,b,a):
            s = pygame.Surface((SW,SH), pygame.SRCALPHA)
            s.fill((r,g,b,a))
            return s
        self._ov_pause = _make_overlay(0,0,0,140)
        self._ov_dead  = _make_overlay(80,0,0,155)
        self._ov_win   = _make_overlay(20,14,0,150)
        self._ov_menu  = _make_overlay(5,8,25,165)

        # companion
        self.comp_img = load_img("duck other duck.png", (DUCK_W-28, DUCK_H-28))

        # platform tile
        raw_p  = load_img("duck assets platform.png")
        ph     = Platform.H
        pw     = int(raw_p.get_width()*ph/raw_p.get_height())
        self.plat_tile = pygame.transform.scale(raw_p, (pw, ph))
        # also a wider tile for the ground strip
        gth    = 28
        gtw    = int(raw_p.get_width()*gth/raw_p.get_height())
        self.ground_tile = pygame.transform.scale(raw_p, (gtw, gth))

        # animation frames
        FSIZE = (DUCK_W, DUCK_H)
        run_f  = load_anim_frames("frames_alpha", 80, FSIZE)
        jump_f = load_anim_frames("frames_alpha", 121, FSIZE)[80:]
        # fallback — draw a simple duck shape if frames are missing
        if not run_f:
            fb = pygame.Surface((DUCK_W, DUCK_H), pygame.SRCALPHA)
            # body
            pygame.draw.ellipse(fb, (240, 200, 60), (10, 30, DUCK_W-20, DUCK_H-40))
            # head
            pygame.draw.circle(fb, (240, 200, 60), (DUCK_W-22, 28), 22)
            # eye
            pygame.draw.circle(fb, (20, 20, 20), (DUCK_W-14, 22), 4)
            pygame.draw.circle(fb, WHITE,         (DUCK_W-13, 21), 1)
            # beak
            pygame.draw.polygon(fb, (255, 150, 0),
                [(DUCK_W-2, 28),(DUCK_W+14, 32),(DUCK_W-2, 36)])
            # wing
            pygame.draw.ellipse(fb, (210, 165, 40), (18, 42, DUCK_W-40, DUCK_H-60))
            run_f = jump_f = [fb]
        self.run_frames  = run_f
        self.jump_frames = jump_f if jump_f else run_f

    def reset(self):
        self.cam     = 0.0
        self.speed   = self.BASE_SPEED
        self.world   = 0.0
        self.particles   = []
        self.popups      = []
        self.pipes       = []
        self.platforms   = []
        self.gems        = []
        self.potions     = []
        self.next_pipe   = SW + 200
        self.next_plat   = SW + 400
        self.next_gem    = SW + 150
        self.next_potion = SW + 700
        self.checkpoint  = Checkpoint(CHECKPOINT_DIST)
        self.duck = Duck(self.run_frames, self.jump_frames, self.comp_img)
        cam_ref[0] = self.cam

    # ── input ──────────────────────────────────────────────────────────────────
    def _move(self):
        keys = pygame.key.get_pressed()
        dx = 0.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += MOVE_SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= MOVE_SPEED
        return dx

    # ── spawning ───────────────────────────────────────────────────────────────
    def _spawn(self):
        edge = self.cam + SW + 100
        if edge >= self.next_pipe:
            self.pipes.append(Pipe(self.next_pipe))
            # scatter 1-3 gems in the gap
            p = self.pipes[-1]
            for _ in range(random.randint(1,3)):
                gy = random.randint(int(p.top)+20, int(p.bot)-20)
                self.gems.append(Gem(self.next_pipe + random.randint(10, PIPE_W-10), gy))
            self.next_pipe += self.PIPE_INTERVAL + random.randint(-80,80)

        if edge >= self.next_plat:
            w  = random.randint(130,260)
            y  = random.randint(GROUND_Y-300, GROUND_Y-130)
            wx = self.next_plat
            self.platforms.append(Platform(wx, y, w, self.plat_tile))
            # gems on platform
            for i in range(random.randint(1,3)):
                self.gems.append(Gem(wx+30+i*65, y-35))
            self.next_plat += self.PLAT_INTERVAL + random.randint(-100,100)

        if edge >= self.next_gem:
            y = random.randint(GROUND_Y-220, GROUND_Y-60)
            for i in range(random.randint(1,4)):
                self.gems.append(Gem(self.next_gem+i*55, y))
            self.next_gem += self.GEM_INTERVAL + random.randint(-60,60)

        # health potions — spawn every ~700-1100 units
        if edge >= self.next_potion:
            y = random.randint(GROUND_Y - 200, GROUND_Y - 60)
            self.potions.append(HealthPotion(self.next_potion, y))
            self.next_potion += random.randint(700, 1100)

    # ── update ─────────────────────────────────────────────────────────────────
    def update(self):
        # world scroll — camera follows duck's world position
        self.speed  = min(self.MAX_SPEED, self.BASE_SPEED + self.world*self.ACCEL)
        self.world += self.speed
        # camera glides so duck stays near screen centre-left
        target_cam  = self.duck.wx - SW * 0.30
        self.cam   += (target_cam - self.cam) * 0.12
        cam_ref[0]  = self.cam

        # score from distance
        self.duck.score += int(self.speed * 0.18)

        self._spawn()

        # duck update
        dx = self._move()
        self.duck.update(dx, self.platforms, self.cam)

        # pipes move left in world space
        for p in self.pipes:
            p.wx -= self.speed

        # gems + platforms
        for g in self.gems:     g.update()

        # particles / popups
        for p in self.particles: p.update()
        for p in self.popups:    p.update()

        dr = self.duck.get_rect(self.cam)

        # ── pipe collisions ──────────────────────────────────────────────────
        for p in self.pipes:
            tr = p.top_rect(self.cam)
            br = p.bot_rect(self.cam)

            for pipe_rect in (tr, br):
                if not pipe_rect.colliderect(dr):
                    continue

                # ── work out overlap on each axis ──────────────────────────
                ol = dr.right  - pipe_rect.left   # duck right into pipe left
                or_ = pipe_rect.right - dr.left   # duck left into pipe right
                ot = dr.bottom - pipe_rect.top    # duck bottom into pipe top
                ob = pipe_rect.bottom - dr.top    # duck top into pipe bottom

                min_overlap = min(ol, or_, ot, ob)

                if min_overlap == ot:
                    # duck landed on top of pipe — stand on it
                    self.duck.y  = pipe_rect.top - DUCK_H
                    self.duck.vy = 0
                    self.duck.on_ground  = True
                    self.duck.jumps_left = 2
                elif min_overlap == ob:
                    # duck hit underside — bounce down
                    self.duck.y  = pipe_rect.bottom
                    self.duck.vy = max(0, self.duck.vy)
                elif min_overlap == ol:
                    # duck right side hit pipe left face — push left
                    self.duck.wx = self.cam + pipe_rect.left - DUCK_W - 12
                    self.duck.vy = max(self.duck.vy, 0)  # stop upward momentum
                    self.duck.hurt(1, self.particles)
                else:
                    # duck left side hit pipe right face — push right
                    self.duck.wx = self.cam + pipe_rect.right + 12
                    self.duck.hurt(1, self.particles)

            # score point when duck passes through gap centre
            if not p.scored and p.sx(self.cam) + PIPE_W < self.duck.sx(self.cam):
                p.scored = True
                self.duck.score += 10
                self.popups.append(Popup(self.duck.sx(self.cam) + DUCK_W//2,
                                         self.duck.y - 20, "+10", GOLD))

        # gem collisions — tokens only, no win condition
        for g in self.gems:
            if g.alive and g.rect(self.cam).colliderect(dr):
                g.alive = False
                self.duck.gems  += 1
                self.duck.score += g.value
                self.popups.append(Popup(g.sx(self.cam), g.y, f"+{g.value}", g.col))
                for _ in range(14):
                    self.particles.append(Particle(g.sx(self.cam),g.y,g.col,life=26,r=5))

        # health potion collisions
        for pot in self.potions:
            if pot.alive and pot.rect(self.cam).colliderect(dr):
                pot.alive = False
                if self.duck.hp < self.duck.MAX_HP:
                    self.duck.hp += 1
                    self.popups.append(Popup(pot.sx(self.cam), pot.y,
                                             "+1 HP", (220,80,100)))
                    for _ in range(18):
                        self.particles.append(Particle(
                            pot.sx(self.cam), pot.y,
                            (220,80,100), life=30, r=6))
                else:
                    # already full hp — still collect for score
                    self.duck.score += 50
                    self.popups.append(Popup(pot.sx(self.cam), pot.y,
                                             "+50 FULL!", GOLD))

        # checkpoint collision — level complete
        if self.checkpoint.rect(self.cam).colliderect(dr):
            self.hi    = max(self.hi, self.duck.score)
            self.state = "win"

        # update potions
        for pot in self.potions: pot.update()

        # cull
        self.pipes      = [p for p in self.pipes      if not p.off_screen(self.cam)]
        self.platforms  = [p for p in self.platforms  if not p.off_screen(self.cam)]
        self.gems       = [g for g in self.gems        if g.alive and g.sx(self.cam)>-60]
        self.potions    = [p for p in self.potions     if p.alive and p.sx(self.cam)>-60]
        self.particles  = [p for p in self.particles   if not p.dead()]
        self.popups     = [p for p in self.popups      if not p.dead()]

        if not self.duck.alive:
            self.hi = max(self.hi, self.duck.score)
            self.state = "dead"

    # ── draw ───────────────────────────────────────────────────────────────────
    def draw(self):
        # sky + parallax
        self.bg.draw(screen, self.cam)

        # platforms
        for p in self.platforms:
            p.draw(screen, self.cam)

        # pipes
        for p in self.pipes:
            p.draw(screen, self.cam)

        # checkpoint (draw behind duck)
        self.checkpoint.draw(screen, self.cam)

        # gems (tokens)
        for g in self.gems:
            g.draw(screen, self.cam)

        # health potions
        for pot in self.potions:
            pot.draw(screen, self.cam)

        # particles
        for p in self.particles:
            p.draw(screen)

        # ground strip
        draw_ground(screen, self.cam, self.ground_tile)

        # duck on top
        self.duck.draw(screen, self.cam)

        # popups
        for p in self.popups:
            p.draw(screen)

        # left border
        draw_border(screen)

        # HUD last
        draw_hud(screen, self.duck, self.speed, self.hi,
                 self.checkpoint.wx, self.cam)

        if self.duck.shield:
            txt(screen, "SHIELD ACTIVE", 24, SW//2, SH-70, CYAN, anchor="midtop")

        # pause overlay
        if self.state == "paused":
            screen.blit(self._ov_pause, (0, 0))
            txt(screen, "PAUSED", 72, SW//2, SH//2-40, WHITE, anchor="center")
            txt(screen, "P  resume   R  restart   ESC  quit",
                26, SW//2, SH//2+40, (200,200,200), anchor="center")

        pygame.display.flip()

    # ── screens ────────────────────────────────────────────────────────────────
    def draw_menu(self):
        # draw scrolling background
        bw = self.bg_img.get_width()
        t  = pygame.time.get_ticks() * 0.0005
        ox = int(-t * 80) % bw
        for x in range(-bw, SW + bw, bw):
            screen.blit(self.bg_img, (x + ox, 0))
        draw_ground(screen, t * 80, self.ground_tile)

        # dark tinted overlay
        ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
        ov.fill((5, 8, 25, 165))
        screen.blit(ov, (0, 0))

        # title with glow
        for gd in range(8, 0, -2):
            txt(screen, "ANIMAL  DASH", 84, SW//2 + gd, 88 + gd,
                (160, 100, 0), anchor="center", shadow=False)
        txt(screen, "ANIMAL  DASH", 84, SW//2, 88, GOLD, anchor="center")
        txt(screen, "Duck · Jump · Survive · Reach the Finish!",
            24, SW//2, 186, (200, 215, 255), anchor="center")

        lines = [
            ("A / D  or  ← →     Move left / right",   (180, 220, 255)),
            ("W / SPACE / ↑       Jump  (double-jump!)", WHITE),
            ("Reach the FINISH flag to complete level",  GOLD),
            ("Collect red potions to restore HP",        (230, 110, 130)),
            ("Collect gems as tokens for score",         CYAN),
            ("P  pause          R  restart",             (180, 190, 210)),
        ]
        bx2, by2, bw2 = SW//2 - 310, 232, 620
        bh2 = len(lines) * 40 + 20
        panel = pygame.Surface((bw2, bh2), pygame.SRCALPHA)
        panel.fill((10, 15, 40, 160))
        pygame.draw.rect(panel, (70, 90, 180, 140), (0, 0, bw2, bh2), border_radius=14)
        screen.blit(panel, (bx2, by2))
        pygame.draw.rect(screen, (80, 100, 200), (bx2, by2, bw2, bh2), 2, border_radius=14)
        for i, (t2, c) in enumerate(lines):
            txt(screen, t2, 21, SW//2, by2 + 12 + i*40, c, anchor="midtop")

        # pulsing start button
        p2 = abs(math.sin(pygame.time.get_ticks() * 0.003))
        btn_col = (int(40 + 40*p2), int(180 + 40*p2), int(40 + 40*p2))
        txt(screen, "Press  SPACE  to start", 38, SW//2, by2 + bh2 + 20, btn_col, anchor="midtop")
        pygame.display.flip()

    def draw_win(self):
        t   = pygame.time.get_ticks()
        t2  = t * 0.001

        # ── full background ────────────────────────────────────────────────────
        self.bg.draw(screen, self.cam)
        draw_ground(screen, self.cam, self.ground_tile)

        # deep dark overlay so colours pop
        screen.blit(self._ov_win, (0, 0))

        # ── confetti — 80 pieces, varied shapes ───────────────────────────────
        rng = random.Random(99)
        conf_cols = [
            (255, 215,  0), (0,   230, 255), (255,  60, 180),
            (60,  255, 120), (255, 120,  0), (200, 100, 255),
            (255, 255,  80), (80,  255, 220),
        ]
        for i in range(80):
            speed_x = rng.uniform(0.015, 0.07)
            speed_y = rng.uniform(0.04,  0.13)
            cx2 = (rng.randint(0, SW) + int(t * speed_x)) % SW
            cy2 = (rng.randint(0, SH) + int(t * speed_y)) % SH
            cr2 = rng.randint(5, 12)
            cc  = conf_cols[i % len(conf_cols)]
            shape = i % 3
            if shape == 0:
                # triangle
                ang = math.radians(t * rng.uniform(0.8, 2.5) + i * 45)
                pts2 = [(cx2 + math.cos(ang + j*2.094)*cr2,
                         cy2 + math.sin(ang + j*2.094)*cr2) for j in range(3)]
                pygame.draw.polygon(screen, cc, pts2)
            elif shape == 1:
                # square rotated
                ang = math.radians(t * rng.uniform(0.5, 2.0) + i * 30)
                pts2 = [(cx2 + math.cos(ang + j*1.571)*cr2,
                         cy2 + math.sin(ang + j*1.571)*cr2) for j in range(4)]
                pygame.draw.polygon(screen, cc, pts2)
            else:
                # circle
                pygame.draw.circle(screen, cc, (cx2, cy2), cr2 // 2)

        # ── double starburst — two rings, different speeds ────────────────────
        cx, cy = SW//2, SH//2 - 40
        for ring, (r1, r2, n, width, speed) in enumerate([
            (100, 165, 24, 4, 55),
            (170, 230, 16, 3, -35),
        ]):
            for i in range(n):
                a  = math.radians(i * (360//n) + t2 * speed)
                pr = abs(math.sin(t2 * 3 + i * 0.5))
                ra = r1 + math.sin(t2 * 4 + i) * 14
                rb = r2 + math.sin(t2 * 2 + i) * 18
                hue = (i / n + t2 * 0.3) % 1.0
                # cycle hue: gold→cyan→pink→green
                palette = [(255,210,0),(0,230,255),(255,60,180),(60,255,120)]
                c2 = palette[(i + ring * 4) % len(palette)]
                pygame.draw.line(screen, c2,
                    (int(cx + math.cos(a)*ra), int(cy + math.sin(a)*ra)),
                    (int(cx + math.cos(a)*rb), int(cy + math.sin(a)*rb)), width)

        # ── title glow — layered shadows then sharp text ──────────────────────
        title = "LEVEL COMPLETE!"
        # outer orange glow layers
        for gd in range(14, 0, -2):
            alpha_surf = get_font(110).render(title, True, (180, 80, 0))
            alpha_surf.set_alpha(int(30 * (gd / 14)))
            r2 = alpha_surf.get_rect(center=(SW//2 + gd//2, 118 + gd//2))
            screen.blit(alpha_surf, r2)
        # yellow inner glow
        for gd in range(6, 0, -2):
            gs = get_font(110).render(title, True, (255, 240, 80))
            gs.set_alpha(120)
            r2 = gs.get_rect(center=(SW//2, 118))
            screen.blit(gs, r2)
        # sharp gold text
        txt(screen, title, 110, SW//2, 118, GOLD, anchor="center", shadow=False)
        # white highlight pass
        txt(screen, title, 110, SW//2 - 1, 117, (255, 255, 200), anchor="center", shadow=False)

        # ── subtitle ──────────────────────────────────────────────────────────
        pulse = abs(math.sin(t2 * 2.5))
        sub_col = (int(180 + 70*pulse), int(230 + 20*pulse), 255)
        txt(screen, "You reached the Finish!", 36, SW//2, 238, sub_col, anchor="center")

        # ── stats card ────────────────────────────────────────────────────────
        card_w, card_h = 520, 180
        card_x, card_y = SW//2 - card_w//2, 290

        # card background with gradient effect
        for row in range(card_h):
            t_row = row / card_h
            rc = int(8  + 18 * t_row)
            gc = int(12 + 28 * t_row)
            bc = int(40 + 50 * t_row)
            pygame.draw.line(screen, (rc, gc, bc),
                             (card_x, card_y + row), (card_x + card_w, card_y + row))
        # card border — animated colour
        border_pulse = abs(math.sin(t2 * 1.5))
        bc1 = (int(80  + 120*border_pulse), int(130 + 80*border_pulse), 255)
        bc2 = (int(180 + 60*border_pulse),  int(200 + 50*border_pulse), 120)
        pygame.draw.rect(screen, bc1, (card_x, card_y, card_w, card_h), 3, border_radius=18)
        pygame.draw.rect(screen, bc2, (card_x+3, card_y+3, card_w-6, card_h-6), 1, border_radius=16)

        # stats text
        txt(screen, f"SCORE   {self.duck.score:,}", 44, SW//2, card_y + 20, GOLD,          anchor="midtop")
        txt(screen, f"TOKENS  {self.duck.gems}",    34, SW//2, card_y + 74, CYAN,           anchor="midtop")
        txt(screen, f"BEST    {self.hi:,}",         28, SW//2, card_y + 118, (180,200,255), anchor="midtop")

        # ── NEW BEST badge ────────────────────────────────────────────────────
        if self.duck.score >= self.hi:
            badge_p = abs(math.sin(t2 * 4))
            badge_col = (int(255), int(180 + 60*badge_p), int(30*badge_p))
            # badge backing
            pygame.draw.rect(screen, (80, 50, 0),
                             (SW//2 - 120, card_y + card_h + 12, 240, 50), border_radius=25)
            pygame.draw.rect(screen, badge_col,
                             (SW//2 - 120, card_y + card_h + 12, 240, 50), 3, border_radius=25)
            txt(screen, "★  NEW BEST!  ★", 32, SW//2, card_y + card_h + 18, badge_col, anchor="midtop")

        # ── prompt ────────────────────────────────────────────────────────────
        prompt_pulse = abs(math.sin(t2 * 2))
        prompt_col = (int(100 + 100*prompt_pulse), int(220 + 30*prompt_pulse), int(100 + 100*prompt_pulse))
        txt(screen, "R  play again          ESC  quit", 28, SW//2, SH - 52, prompt_col, anchor="center")

        pygame.display.flip()

    def draw_dead(self):
        self.bg.draw(screen, self.cam)
        draw_ground(screen, self.cam, self.ground_tile)
        ov = pygame.Surface((SW,SH),pygame.SRCALPHA)
        ov.fill((80,0,0,155))
        screen.blit(ov,(0,0))

        txt(screen,"GAME  OVER",88,SW//2,140,RED,anchor="center")
        txt(screen,f"Score  :  {self.duck.score:,}",44,SW//2,260,GOLD,anchor="center")
        txt(screen,f"Best   :  {self.hi:,}",         34,SW//2,316,WHITE,anchor="center")
        txt(screen,f"Tokens :  {self.duck.gems}",    28,SW//2,362,CYAN,anchor="center")
        if self.duck.score >= self.hi > 0:
            txt(screen,"NEW BEST!",44,SW//2,414,GOLD,anchor="center")
        txt(screen,"R  try again     ESC  quit",
            28,SW//2,SH-70,(200,200,200),anchor="center")
        pygame.display.flip()

    # ── main loop ──────────────────────────────────────────────────────────────
    def run(self):
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if self.state == "menu":
                    if ev.type == pygame.KEYDOWN and ev.key in (
                            pygame.K_SPACE, pygame.K_RETURN):
                        self.state = "playing"

                elif self.state == "playing":
                    if ev.type == pygame.KEYDOWN:
                        if ev.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                            self.duck.jump(self.particles)
                        elif ev.key == pygame.K_p:
                            self.state = "paused"
                        elif ev.key == pygame.K_ESCAPE:
                            pygame.quit(); sys.exit()

                elif self.state == "paused":
                    if ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_p:
                            self.state = "playing"
                        elif ev.key == pygame.K_r:
                            self.reset(); self.state = "playing"
                        elif ev.key == pygame.K_ESCAPE:
                            pygame.quit(); sys.exit()

                elif self.state == "dead":
                    if ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_r:
                            self.reset(); self.state = "playing"
                        elif ev.key == pygame.K_ESCAPE:
                            pygame.quit(); sys.exit()

                elif self.state == "win":
                    if ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_r:
                            self.reset(); self.state = "playing"
                        elif ev.key == pygame.K_ESCAPE:
                            pygame.quit(); sys.exit()

            if self.state == "menu":
                self.draw_menu()
            elif self.state == "playing":
                self.update()
                self.draw()
            elif self.state == "paused":
                self.draw()
            elif self.state == "dead":
                self.draw_dead()
            elif self.state == "win":
                self.draw_win()

            clock.tick(FPS)

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    Game().run()
