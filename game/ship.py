# -*- coding: utf-8 *-*

from pyglet.window import key
from pyglet import clock
from . import util, physicalobject
from . import resources

class Ship(physicalobject.PhysicalObject):
    """A class for the player"""
    def __init__(self, thrust_image=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set some easy-to-tweak constants
        # play values
        self.rotate_speed = 170.0
        self.bullet_speed = 500.0
        self.thrust_acc = 500
        self.friction = 0.95
        self.bullet_duration = 0.6

        self.thrust = False
        self.thrust_image = thrust_image
        self.normal_image = self.image

        self.bullets = set() # FIXME: bullet by OOT
        self.forward = [0, 1]
        self.shoot_angle = [0, 0]
        
        self.keyMask = 0;
        self.W_PRESSED = 1
        self.A_PRESSED = 2
        self.S_PRESSED = 4
        self.D_PRESSED = 8

    def on_joybutton_press(self, joystick, button):
        self.shoot()


    def on_joyaxis_motion(self, joystick, axis, value):
        #i = {'x': (self.forward, 0)
        #     'y': (self.forward, 1),
        #     'rz': (self.shoot_angle, 0),
        #     'rx': (self.shoot_angle, 1),
        #i[axis][0][axis][1] = valie }

        print(axis, value)
        if axis == 'x':
            self.forward[0] = value
            do_update = True
        elif axis == 'y':
            self.forward[1] = -value
            do_update = True
        elif axis == 'rx':
            self.shoot_angle[1] = -value
            self.shoot(shoot_angle)
        elif axis == 'rz':
            self.shoot_angle[0] = value
            self.shoot(shoot_angle)
        else:
            do_update = False

        if do_update:
            self.rotation = util.vector_to_angle(self.forward)


    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.shoot()
        elif symbol == key.LEFT:
            self.turn(-1)
        elif symbol == key.RIGHT:
            self.turn(1)
        elif symbol == key.UP:
            self.set_thrust(True)
        
        if symbol == key.W:    
            self.keyMask |= self.W_PRESSED
        elif symbol == key.A:
            self.keyMask |= self.A_PRESSED
        elif symbol == key.S:
            self.keyMask |= self.S_PRESSED
        elif symbol == key.D:
            self.keyMask |= self.D_PRESSED
  
        angle = 0
        counter = 0;
        if self.keyMask != 0:
            if self.keyMask & self.W_PRESSED:
                angle += 270
                counter += 1
            if self.keyMask & self.A_PRESSED:
                angle += 180
                counter += 1
            if self.keyMask & self.S_PRESSED:
                angle += 90
                counter += 1
            if self.keyMask & self.D_PRESSED:
                angle += 360
                counter += 1
                
            angle /= counter;
            self.shoot(angle)
            

    def on_key_release(self, symbol, modifiers):
        if symbol in (key.LEFT, key.RIGHT):
            self.turn(0)
        elif symbol == key.UP:
            self.set_thrust(False)

        if symbol == key.W:    
            self.keyMask &= ~self.W_PRESSED
        elif symbol == key.A:
            self.keyMask &= ~self.A_PRESSED
        elif symbol == key.S:
            self.keyMask &= ~self.S_PRESSED
        elif symbol == key.D:
            self.keyMask &= ~self.D_PRESSED

    def update(self, dt):
        super().update(dt)
        if self.thrust and self.thrust_image:
            self.image = self.thrust_image
        else:
            self.image = self.normal_image

        # update velocity
        if self.thrust:
            acc = util.angle_to_vector(self.rotation)
            for i in (0,1):
                self.vel[i] += acc[i] * self.thrust_acc * dt

        # add friction
        for i in (0,1):
            self.vel[i] *= (1 - self.friction * dt)

        for bullet in set(self.bullets):
            if bullet.update(dt):
                self.bullets.remove(bullet)

        return False

    def set_thrust(self, on):
        self.thrust = on
        if on:
            self.forward = util.angle_to_vector(self.rotation)
            resources.thrust_sound.seek(0)
            resources.thrust_sound.play()
        else:
            self.forward = [0, 0]
            resources.thrust_sound.pause()

    def turn(self, clockwise):
        self.rotation_speed = clockwise * self.rotate_speed


    def shoot(self, angle=None):
        resources.bullet_sound.play()

        if not angle:
            forward = util.angle_to_vector(self.rotation)
        else:
            forward = util.angle_to_vector(angle)
            
        bullet_pos = [self.x + self.radius * forward[0], self.y + self.radius * forward[1]]
        bullet_vel = [self.vel[0] + self.bullet_speed * forward[0], self.vel[1] + self.bullet_speed * forward[1]]
        bullet = physicalobject.PhysicalObject(lifespan=self.bullet_duration, vel=bullet_vel, x=bullet_pos[0], y=bullet_pos[1],
            img=resources.shot_image, batch=self.batch, group=self.group, screensize=self.screensize)
        self.bullets.add(bullet)

    def destroy(self):
        # check invulnerability
        if self.opacity != 255:
            return

        explosion = super().destroy()

        self.rotation = -90
        self.x = self.screensize[0] / 2
        self.y = self.screensize[1] / 2
        self.vel = [0, 0]
        self.set_thrust(False)
        self.visible = True
        return explosion


    def normal_mode(self, dt):
        self.opacity = 255


    def invulnerable(self, time):
        # be invulnerable for a brief time
        self.opacity = 128
        clock.schedule_once(self.normal_mode, time)
    
