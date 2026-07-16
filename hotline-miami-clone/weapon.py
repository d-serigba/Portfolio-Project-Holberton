import pygame

class Weapon:
    def __init__(self, weapon_type, ammo, fire_rate, pos=None):
        self.type = weapon_type  # 'semi' ou 'auto'
        self.ammo = ammo
        self.max_ammo = ammo
        self.fire_rate = fire_rate  # en frames
        self.last_fire = 0
        self.pos = pos  # pour pickup au sol

    def can_fire(self):
        return self.ammo > 0 and pygame.time.get_ticks() - self.last_fire > self.fire_rate

    def fire(self, start_pos, target_pos, bullets_group):
        direction = (target_pos - start_pos).normalize()
        bullet = Bullet(start_pos, direction)
        bullets_group.add(bullet)
        self.ammo -= 1
        self.last_fire = pygame.time.get_ticks()
        if self.ammo == 0:
            # L'arme est jetée, le joueur la perd
            return None
        return self
