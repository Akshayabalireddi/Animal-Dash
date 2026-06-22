# -*- coding: utf-8 -*-
"""Lion World (Level 4) - Standalone playable level
Controls: Arrow keys / WASD to move, Space/Up/W to jump (double jump supported)
ESC = pause / menu
"""
import pygame, sys, math, random, json, os
from lion_world import make_lion_data

pygame.init()
clock = pygame.time.Clock()
BASE  = os.path.dirname(os.path.abspath(__file__))
W, H  = 1280, 720
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Animal Dash - Lion World (Level 4)")

FPS   = 60
CAP_DT = 0.05
GRAV  = 1900
FALL  = 1600
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
YELLOW = (255, 215, 0)
GREY   = (160, 160, 160)
DGREY  = (50,  50,  70)
HRED   = (220,  40,  40)
SKY    = (100, 180, 240)
OCEAN  = (30,  100, 180)
MAGENTA= (255,   0, 255)
GREEN  = (50,  200,  50)
ORANGE = (255, 160,  30)
LBLUE  = (120, 200, 255)

# ── Audio stub ────────────────────────────────────────────────────────────────
class Audio:
    def play_sfx(self, n): pass
SFX = Audio()

# ── Asset cache & loader ──────────────────────────────────────────────────────
_CACHE = {}

def spr(rel, size=None):
    k = (rel, size)
    if k in _CACHE: return _CACHE[k]
    try:
        img = pygame.image.load(os.path.join(BASE, rel)).convert_alpha()
    except Exception:
        img = pygame.Surface((64, 64), pygame.SRCALPHA)
        img.fill((255, 0, 255, 180))
        print("MISS:", rel, file=sys.stderr)
    if size:
        img = pygame.transform.smoothscale(img, size)
    _CACHE[k] = img
    return img

def bg_img(rel):
    k = ("BG", rel)
    if k in _CACHE: return _CACHE[k]
    try:
        img = pygame.image.load(os.path.join(BASE, rel)).convert()
    except Exception:
        img = pygame.Surface((W, H))
        img.fill(SKY)
    img = pygame.transform.smoothscale(img, (W, H))
    _CACHE[k] = img
    return img

def scale_spr(rel, h):
    raw = spr(rel)
    rw, rh = raw.get_size()
    ratio = h / rh
    return pygame.transform.smoothscale(raw, (max(1, int(rw * ratio)), h))

def tile_strip(src_rel, dest_w, dest_h):
    raw = spr(src_rel)
    rw, rh = raw.get_size()
    ratio = dest_h / rh
    tile = pygame.transform.smoothscale(raw, (max(1, int(rw * ratio)), dest_h))
    tw = tile.get_width()
    out = pygame.Surface((dest_w, dest_h), pygame.SRCALPHA)
    for x in range(0, dest_w, tw):
        out.blit(tile, (x, 0))
    return out

SP = "assets/sprites"
def p(world, name): return f"{SP}/{world}/{name}"

# ── Font helpers ──────────────────────────────────────────────────────────────
_FONTS = {}
def font(size):
    if size not in _FONTS:
        _FONTS[size] = pygame.font.SysFont("arial", size, bold=True)
    return _FONTS[size]

def draw_text(surf, text, size, color, cx, cy):
    f = font(size)
    s = f.render(str(text), True, color)
    r = s.get_rect(center=(cx, cy))
    surf.blit(s, r)

def draw_text_left(surf, text, size, color, x, y):
    f = font(size)
    s = f.render(str(text), True, color)
    surf.blit(s, (x, y))

# ── Button helper ─────────────────────────────────────────────────────────────
class Button:
    def __init__(self, cx, cy, w, h, text, color=(70,130,180), hover=(100,160,210)):
        self.rect  = pygame.Rect(0, 0, w, h)
        self.rect.center = (cx, cy)
        self.text  = text
        self.col   = color
        self.hcol  = hover

    def draw(self, surf):
        mx, my = pygame.mouse.get_pos()
        c = self.hcol if self.rect.collidepoint(mx, my) else self.col
        pygame.draw.rect(surf, c, self.rect, border_radius=8)
        pygame.draw.rect(surf, WHITE, self.rect, 2, border_radius=8)
        draw_text(surf, self.text, 22, WHITE, self.rect.centerx, self.rect.centery)

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))

# ── Camera ────────────────────────────────────────────────────────────────────
class Camera:
    def __init__(self, level_width):
        self.x = 0
        self.level_width = level_width
        self.shake_frames = 0
        self.shake_mag    = 0
        self._ox = 0
        self._oy = 0

    def update(self, target_rect, dt):
        target_x = target_rect.centerx - W // 2
        self.x += (target_x - self.x) * min(1.0, 8 * dt)
        self.x  = max(0, min(self.x, self.level_width - W))
        if self.shake_frames > 0:
            self._ox = random.randint(-self.shake_mag, self.shake_mag)
            self._oy = random.randint(-self.shake_mag, self.shake_mag)
            self.shake_frames -= 1
        else:
            self._ox = 0
            self._oy = 0

    def shake(self, frames=8, mag=6):
        self.shake_frames = frames
        self.shake_mag    = mag

    def apply(self, rect):
        return rect.move(-int(self.x) + self._ox, self._oy)

    def apply_xy(self, x, y):
        return x - int(self.x) + self._ox, y + self._oy

    def world_x(self, screen_x):
        return screen_x + int(self.x) - self._ox

# ── Particle system ───────────────────────────────────────────────────────────
class Particle:
    __slots__ = ("x","y","vx","vy","life","max_life","color","r","grav")
    def __init__(self, x, y, vx, vy, life, color, r=3, grav=True):
        self.x=x; self.y=y; self.vx=vx; self.vy=vy
        self.life=life; self.max_life=life
        self.color=color; self.r=r; self.grav=grav

    def update(self, dt):
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        if self.grav:
            self.vy += 600 * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surf, cam):
        alpha = int(255 * max(0, self.life / self.max_life))
        sx, sy = cam.apply_xy(self.x, self.y)
        r = max(1, int(self.r * (self.life / self.max_life)))
        c = (*self.color[:3], alpha)
        s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, c, (r, r), r)
        surf.blit(s, (sx - r, sy - r))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def coin_burst(self, x, y):
        for _ in range(12):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(80, 220)
            life  = random.uniform(0.4, 0.8)
            self.particles.append(
                Particle(x, y, math.cos(angle)*speed, math.sin(angle)*speed,
                         life, YELLOW, r=4))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surf, cam):
        for p in self.particles:
            p.draw(surf, cam)

# ── Platform ──────────────────────────────────────────────────────────────────
class Platform:
    def __init__(self, x, y, w, h, tile_img_rel):
        self.rect = pygame.Rect(x, y, w, h)
        self._img_rel = tile_img_rel
        self._surf = None

    def _ensure(self):
        if self._surf is None:
            self._surf = tile_strip(self._img_rel, self.rect.w, self.rect.h)

    def draw(self, surf, cam):
        self._ensure()
        surf.blit(self._surf, cam.apply(self.rect))

class MovingPlatform(Platform):
    def __init__(self, x, y, w, h, tile_img_rel, x2, y2, speed):
        super().__init__(x, y, w, h, tile_img_rel)
        self.start = pygame.math.Vector2(x, y)
        self.end   = pygame.math.Vector2(x2, y2)
        self.speed = speed
        self.going_to_end = True
        self.dx = 0
        self.dy = 0

    def update(self, dt):
        target = self.end if self.going_to_end else self.start
        diff   = target - pygame.math.Vector2(self.rect.x, self.rect.y)
        dist   = diff.length()
        move   = self.speed * dt
        if dist <= move:
            self.rect.x = int(target.x)
            self.rect.y = int(target.y)
            self.going_to_end = not self.going_to_end
            self.dx = 0
            self.dy = 0
        else:
            d = diff.normalize() * move
            self.dx = d.x
            self.dy = d.y
            self.rect.x += int(self.dx)
            self.rect.y += int(self.dy)

# ── Coin ─────────────────────────────────────────────────────────────────────
class Coin:
    def __init__(self, x, y):
        self.rect    = pygame.Rect(x, y, 20, 20)
        self.bob     = random.uniform(0, math.tau)
        self.collected = False

    def update(self, dt):
        self.bob += 3 * dt

    def draw(self, surf, cam):
        if self.collected: return
        by = int(math.sin(self.bob) * 4)
        r  = cam.apply(self.rect).move(0, by)
        pygame.draw.circle(surf, YELLOW, r.center, 10)
        pygame.draw.circle(surf, (200, 180, 0), r.center, 10, 2)

# ── Hazard (spike shape) ──────────────────────────────────────────────────────
class Hazard:
    def __init__(self, x, y, w=32, h=24):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surf, cam):
        r = cam.apply(self.rect)
        spike_w = max(8, self.rect.w // 4)
        num_spikes = self.rect.w // spike_w
        for i in range(num_spikes):
            bx = r.x + i * spike_w
            pts = [(bx, r.bottom), (bx + spike_w//2, r.top), (bx + spike_w, r.bottom)]
            pygame.draw.polygon(surf, (180, 60, 60), pts)
            pygame.draw.polygon(surf, (220, 80, 80), pts, 1)

# ── TrapHazard (lion trap sprite) ─────────────────────────────────────────────
class TrapHazard:
    def __init__(self, x, y, size=40):
        self.rect = pygame.Rect(x, y, size, size)
        self._size = size

    def draw(self, surf, cam):
        img = scale_spr(p("lion", "trap.png"), self._size)
        surf.blit(img, cam.apply(self.rect))

# ── Checkpoint ────────────────────────────────────────────────────────────────
class Checkpoint:
    def __init__(self, x, y):
        self.rect      = pygame.Rect(x, y, 24, 60)
        self.activated = False
        self.bob       = 0.0

    def update(self, dt):
        self.bob += 3 * dt

    def draw(self, surf, cam):
        r  = cam.apply(self.rect)
        c  = (50, 220, 50) if self.activated else (200, 200, 80)
        pygame.draw.rect(surf, c, r, border_radius=4)
        pygame.draw.polygon(surf, c,
            [(r.x, r.y), (r.x + 20, r.y + 10), (r.x, r.y + 20)])

# ── Goal ──────────────────────────────────────────────────────────────────────
class Goal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 80)
        self.bob  = 0.0

    def update(self, dt):
        self.bob += 2 * dt

    def draw(self, surf, cam):
        r = cam.apply(self.rect)
        pygame.draw.rect(surf, (200, 200, 80), (r.x + 18, r.y, 4, r.height))
        bob_y = int(math.sin(self.bob) * 3)
        pygame.draw.polygon(surf, (255, 80, 80),
            [(r.x + 22, r.y + bob_y),
             (r.x + 22, r.y + 24 + bob_y),
             (r.x + 46, r.y + 12 + bob_y)])

# ── HealthPickup ──────────────────────────────────────────────────────────────
class HealthPickup:
    def __init__(self, x, y):
        self.rect      = pygame.Rect(x, y, 24, 24)
        self.bob       = random.uniform(0, math.tau)
        self.collected = False

    def update(self, dt):
        self.bob += 2 * dt

    def draw(self, surf, cam):
        if self.collected: return
        by = int(math.sin(self.bob) * 3)
        r  = cam.apply(self.rect).move(0, by)
        cx, cy = r.center
        pygame.draw.circle(surf, HRED, (cx - 6, cy - 2), 7)
        pygame.draw.circle(surf, HRED, (cx + 6, cy - 2), 7)
        pygame.draw.polygon(surf, HRED, [(cx - 12, cy), (cx, cy + 14), (cx + 12, cy)])

# ── Decor (non-collidable env sprite) ─────────────────────────────────────────
class Decor:
    def __init__(self, x, y, img_rel, h):
        self._img_rel = img_rel
        self._h       = h
        self._img     = None
        raw  = spr(img_rel)
        rw, rh = raw.get_size()
        ratio  = h / rh
        self._w = max(1, int(rw * ratio))
        self.rect = pygame.Rect(x, y, self._w, h)

    def draw(self, surf, cam):
        if self._img is None:
            self._img = scale_spr(self._img_rel, self._h)
        surf.blit(self._img, cam.apply(self.rect))

# ── Projectile (Hunter shoots) ────────────────────────────────────────────────
class Projectile:
    def __init__(self, x, y):
        self.rect  = pygame.Rect(x, y, 12, 12)
        self.speed = 500
        self.alive = True

    def update(self, dt):
        self.rect.x += int(self.speed * dt)

    def draw(self, surf, cam):
        r = cam.apply(self.rect)
        pygame.draw.circle(surf, ORANGE, r.center, 6)
        pygame.draw.circle(surf, YELLOW, r.center, 3)

# ── Hunter (Lion level) ───────────────────────────────────────────────────────
class Hunter:
    SHOOT_INTERVAL_MIN = 3.0
    SHOOT_INTERVAL_MAX = 5.0

    def __init__(self, player_x):
        self.x          = float(player_x - 400)
        self.y          = float(H - 80 - 60)
        self.lag        = 400.0      # distance behind player
        self.speed      = 340.0
        self.shoot_timer = random.uniform(self.SHOOT_INTERVAL_MIN,
                                          self.SHOOT_INTERVAL_MAX)
        self.projectiles = []
        self._img       = None

    def _get_img(self):
        if self._img is None:
            self._img = scale_spr(p("lion", "hunter.png"), 60)
        return self._img

    def good_event(self):
        """Player collected item or reached checkpoint → hunter slows."""
        self.lag = min(800.0, self.lag + 60.0)

    def bad_event(self):
        """Player took damage or hit trap → hunter speeds up."""
        self.lag = max(0.0, self.lag - 80.0)

    def update(self, player_rect, dt, level_width):
        target_x = float(player_rect.x) - self.lag
        self.x  += (target_x - self.x) * min(1.0, 4 * dt)
        self.x   = max(0.0, min(self.x, level_width - 60))

        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.projectiles.append(Projectile(int(self.x) + 60, int(self.y) + 20))
            self.shoot_timer = random.uniform(self.SHOOT_INTERVAL_MIN,
                                              self.SHOOT_INTERVAL_MAX)

        for proj in self.projectiles:
            proj.update(dt)
        self.projectiles = [pr for pr in self.projectiles
                            if pr.rect.x < level_width]

    def catches_player(self, player_rect):
        hunter_rect = pygame.Rect(int(self.x), int(self.y), 50, 60)
        return hunter_rect.colliderect(player_rect)

    def draw(self, surf, cam):
        img = self._get_img()
        sx, sy = cam.apply_xy(self.x, self.y)
        surf.blit(img, (sx, sy))
        lag_pct = self.lag / 800.0
        bar_w   = 60
        pygame.draw.rect(surf, HRED,   (sx, sy - 10, bar_w, 6))
        pygame.draw.rect(surf, GREEN,  (sx, sy - 10, int(bar_w * lag_pct), 6))
        for proj in self.projectiles:
            proj.draw(surf, cam)

# ── Player ────────────────────────────────────────────────────────────────────
class Player:
    JUMP_V       = -760
    DOUBLE_JUMP_V = -700
    MAX_HP       = 3
    INV_TIME     = 1.5
    SPEED        = 380  # Lion world speed
    GRAV_SCALE   = 1.0  # Lion world gravity

    def __init__(self, x, y):
        self.rect        = pygame.Rect(x, y, 56, 68)
        self.vx          = 0.0
        self.vy          = 0.0
        self.on_ground   = False
        self.jumps_left  = 2
        self.hp          = self.MAX_HP
        self.inv_timer   = 0.0
        self.facing_right = True
        self.alive       = True
        self.bob         = 0.0
        self._img        = None
        self._plat_carry = pygame.math.Vector2(0.0, 0.0)

    def _get_img(self):
        if self._img is None:
            self._img = scale_spr(p("lion", "lion.png"), 68)
        return self._img

    def jump(self):
        if self.jumps_left == 2:
            self.vy = self.JUMP_V
            self.jumps_left -= 1
            self.on_ground = False
        elif self.jumps_left == 1:
            self.vy = self.DOUBLE_JUMP_V
            self.jumps_left -= 1

    def take_damage(self, cam=None):
        if self.inv_timer > 0:
            return False
        self.hp       -= 1
        self.inv_timer = self.INV_TIME
        if cam:
            cam.shake()
        return True

    def update(self, dt, platforms, all_hazards, checkpoints, coins,
               health_pickups, particles, cam, hunter=None):
        keys = pygame.key.get_pressed()

        # horizontal input
        dx = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx =  1
        self.vx = dx * self.SPEED

        if dx > 0: self.facing_right = True
        elif dx < 0: self.facing_right = False

        # gravity
        self.vy += GRAV * self.GRAV_SCALE * dt
        self.vy  = min(self.vy, FALL)

        # carry from moving platform
        cx, cy = float(self._plat_carry.x), float(self._plat_carry.y)
        self._plat_carry = pygame.math.Vector2(0.0, 0.0)

        # ── x-axis move ──
        self.rect.x += int(self.vx * dt + cx)
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vx > 0 or cx > 0:
                    self.rect.right = plat.rect.left
                else:
                    self.rect.left  = plat.rect.right
                self.vx = 0

        # ── y-axis move ──
        self.rect.y += int(self.vy * dt + cy)
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vy >= 0:
                    self.rect.bottom = plat.rect.top
                    self.vy          = 0
                    self.on_ground   = True
                    self.jumps_left  = 2
                    if isinstance(plat, MovingPlatform):
                        self._plat_carry = pygame.math.Vector2(plat.dx, plat.dy)
                else:
                    self.rect.top = plat.rect.bottom
                    self.vy = 0

        # ground clamp
        ground_y = H - 80
        if self.rect.bottom >= ground_y:
            self.rect.bottom = ground_y
            self.vy          = 0
            self.on_ground   = True
            self.jumps_left  = 2

        # left boundary
        if self.rect.left < 0:
            self.rect.left = 0
            self.vx = 0

        if self.inv_timer > 0:
            self.inv_timer -= dt

        self.bob += 3 * dt

        # ── hazards ──
        if self.inv_timer <= 0:
            for hz in all_hazards:
                if self.rect.colliderect(hz.rect):
                    if self.take_damage(cam):
                        self.vy = -300
                        if hunter: hunter.bad_event()

        # ── checkpoints ──
        for cp in checkpoints:
            if not cp.activated and self.rect.colliderect(cp.rect):
                cp.activated = True
                if hunter: hunter.good_event()

        # ── coins ──
        for coin in coins:
            if not coin.collected and self.rect.colliderect(coin.rect):
                coin.collected = True
                particles.coin_burst(coin.rect.centerx, coin.rect.centery)

        # ── health pickups ──
        for hp_pu in health_pickups:
            if not hp_pu.collected and self.rect.colliderect(hp_pu.rect):
                hp_pu.collected = True
                self.hp = min(self.MAX_HP, self.hp + 1)

        # hunter projectiles
        if hunter and self.inv_timer <= 0:
            for proj in hunter.projectiles:
                if self.rect.colliderect(proj.rect):
                    proj.alive = False
                    if self.take_damage(cam):
                        if hunter: hunter.bad_event()
            hunter.projectiles = [pr for pr in hunter.projectiles if pr.alive]

        if self.hp <= 0:
            self.alive = False

    def draw(self, surf, cam):
        img = self._get_img()
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        if self.inv_timer > 0:
            flash = int(self.inv_timer * 10) % 2 == 0
            if flash:
                return
        r = cam.apply(self.rect)
        surf.blit(img, r)

# ── Level ─────────────────────────────────────────────────────────────────────
class Level:
    def __init__(self, data):
        self.data          = data
        self.world         = data["world"]
        self.level_width   = data["width"]
        self.bg            = bg_img(data["bg"])
        self.platform_rel  = data["platform_tile"]
        self.cam           = Camera(self.level_width)
        self.particles     = ParticleSystem()

        self.platforms     = []
        self.coins         = []
        self.hazards       = []
        self.checkpoints   = []
        self.health_pickups= []
        self.decors        = []
        self.goal          = None
        self.hunter        = None

        px, py = data.get("spawn", (80, H - 80 - 68))
        self.spawn_x = px
        self.spawn_y = py
        self.checkpoint_pos = (px, py)
        self.player = Player(px, py)

        self._build(data)

        # lion hunter
        if self.world == "lion":
            self.hunter = Hunter(self.player.rect.x)

        gx, gy = data.get("goal", (self.level_width - 200, H - 80 - 80))
        self.goal = Goal(gx, gy)

        self.complete    = False
        self.dead        = False
        self.dead_timer  = 0.0
        self.total_coins = len(self.coins)

    def _build(self, d):
        ground_w = self.level_width
        self.platforms.append(Platform(0, H - 80, ground_w, 80, self.platform_rel))

        for item in d.get("platforms", []):
            x, y, w, h = item
            self.platforms.append(Platform(x, y, w, h, self.platform_rel))

        for item in d.get("moving_platforms", []):
            x, y, w, h, x2, y2, spd = item
            self.platforms.append(MovingPlatform(x, y, w, h, self.platform_rel, x2, y2, spd))

        for cx, cy in d.get("coins", []):
            self.coins.append(Coin(cx, cy))

        for item in d.get("hazards", []):
            x, y, w, h = item
            self.hazards.append(Hazard(x, y, w, h))

        for item in d.get("traps", []):
            x, y = item[0], item[1]
            sz   = item[2] if len(item) > 2 else 40
            self.hazards.append(TrapHazard(x, y, sz))

        for cx, cy in d.get("checkpoints", []):
            self.checkpoints.append(Checkpoint(cx, cy))

        for hx, hy in d.get("health_pickups", []):
            self.health_pickups.append(HealthPickup(hx, hy))

        for item in d.get("decors", []):
            x, y, rel, h = item[0], item[1], item[2], item[3]
            self.decors.append(Decor(x, y, rel, h))

    def respawn(self):
        rx, ry = self.checkpoint_pos
        self.player = Player(rx, ry)
        self.dead    = False

    def _update_checkpoint_pos(self):
        for cp in self.checkpoints:
            if cp.activated:
                self.checkpoint_pos = (cp.rect.x, cp.rect.bottom - 68)

    def update(self, dt):
        moving_plats = [p for p in self.platforms if isinstance(p, MovingPlatform)]
        for mp in moving_plats:
            mp.update(dt)

        self.player.update(dt, self.platforms, self.hazards,
                           self.checkpoints, self.coins,
                           self.health_pickups, self.particles, self.cam,
                           hunter=self.hunter)

        self._update_checkpoint_pos()

        for coin   in self.coins:        coin.update(dt)
        for cp     in self.checkpoints:  cp.update(dt)
        for hp_pu  in self.health_pickups: hp_pu.update(dt)
        if self.goal: self.goal.update(dt)

        self.particles.update(dt)
        self.cam.update(self.player.rect, dt)

        if self.hunter:
            self.hunter.update(self.player.rect, dt, self.level_width)
            if self.hunter.catches_player(self.player.rect):
                self.player.alive = False

        if not self.player.alive:
            self.dead = True
            return

        # check goal
        if self.goal and self.player.rect.colliderect(self.goal.rect):
            self.complete = True

    def draw(self, surf):
        surf.blit(self.bg, (0, 0))

        for decor in self.decors:
            decor.draw(surf, self.cam)

        for plat in self.platforms:
            plat.draw(surf, self.cam)

        for hazard in self.hazards:
            hazard.draw(surf, self.cam)

        for coin in self.coins:
            coin.draw(surf, self.cam)

        for cp in self.checkpoints:
            cp.draw(surf, self.cam)

        for hp_pu in self.health_pickups:
            hp_pu.draw(surf, self.cam)

        if self.goal:
            self.goal.draw(surf, self.cam)

        self.particles.draw(surf, self.cam)

        if self.hunter:
            self.hunter.draw(surf, self.cam)

        self.player.draw(surf, self.cam)

    def count_collected(self):
        return sum(1 for coin in self.coins if coin.collected)

# ── HUD ───────────────────────────────────────────────────────────────────────
class HUD:
    def draw(self, surf, player, level):
        # Hearts
        for i in range(Player.MAX_HP):
            cx = 30 + i * 34
            cy = 36
            if i < player.hp:
                pygame.draw.circle(surf, HRED,   (cx - 6, cy - 2), 7)
                pygame.draw.circle(surf, HRED,   (cx + 6, cy - 2), 7)
                pygame.draw.polygon(surf, HRED, [(cx - 12, cy), (cx, cy + 14), (cx + 12, cy)])
            else:
                pygame.draw.circle(surf, GREY,   (cx - 6, cy - 2), 7)
                pygame.draw.circle(surf, GREY,   (cx + 6, cy - 2), 7)
                pygame.draw.polygon(surf, GREY, [(cx - 12, cy), (cx, cy + 14), (cx + 12, cy)])

        # Coins collected
        coins_str = f"Coins: {level.count_collected()}/{level.total_coins}"
        draw_text_left(surf, coins_str, 20, YELLOW, W - 300, 20)

        # Level name
        draw_text(surf, "Lion World - Level 4", 28, WHITE, W // 2, 40)

        if level.dead:
            draw_text(surf, "YOU DIED - Press SPACE to retry", 24, HRED, W // 2, H // 2)
        elif level.complete:
            draw_text(surf, f"LEVEL COMPLETE! Score: {level.count_collected()}/{level.total_coins}", 28, GREEN, W // 2, H // 2)

# ── Pause Menu ────────────────────────────────────────────────────────────────
class PauseMenu:
    def __init__(self):
        self.resume_btn = Button(W // 2, H // 2 - 50, 200, 60, "Resume")
        self.quit_btn   = Button(W // 2, H // 2 + 50, 200, 60, "Quit")

    def draw(self, surf):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        surf.blit(s, (0, 0))
        draw_text(surf, "PAUSED", 48, WHITE, W // 2, H // 2 - 120)
        self.resume_btn.draw(surf)
        self.quit_btn.draw(surf)

    def handle(self, event):
        if self.resume_btn.clicked(event):
            return "resume"
        if self.quit_btn.clicked(event):
            return "quit"
        return None

# ── Main Game ─────────────────────────────────────────────────────────────────
def main():
    level_data = make_lion_data()
    level = Level(level_data)
    hud = HUD()
    paused = False
    pause_menu = None
    
    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, CAP_DT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if paused:
                        paused = False
                    else:
                        paused = True
                        pause_menu = PauseMenu()
                elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    if not paused and level.player.on_ground:
                        level.player.jump()
                elif event.key == pygame.K_SPACE and level.dead:
                    if paused:
                        paused = False
                    level.respawn()

            if paused and pause_menu and event.type in (pygame.MOUSEBUTTONDOWN,):
                action = pause_menu.handle(event)
                if action == "resume":
                    paused = False
                elif action == "quit":
                    running = False

        if not paused:
            level.update(dt)
            if level.complete:
                pygame.time.wait(2000)
                running = False

        screen.fill(SKY)
        level.draw(screen)
        hud.draw(screen, level.player, level)

        if paused and pause_menu:
            pause_menu.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
