import pyglet
import random
import math

class Ball(pyglet.sprite.Sprite):
	def __init__(self, bar_left, bar_right, window, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.vx = 0.	# x-velocity
		self.vy = 0.	# y-velocity
		self.v0 = 150.	# initial velocity magnitude
		self.window = window
		self.bar_left = bar_left
		self.bar_right = bar_right

		self.friction = 0.3  # this factor determines how much "spin" the ball gets from a moving racket
		self.bounce = 1.05  # speed-up factor at every racket hit

	def update(self, dt):
		last_x = self.x  # the last x-position is needed for safe collision detection with the rackets

		self.x += self.vx * dt
		self.y += self.vy * dt

		is_game_over = False  # Flag to signify whether the game should continue or not
		if (self.x > self.window.width - self.width) or (self.x < 0):  # game over on collision with left or right wall
			is_game_over = True

		# reflect at rackets
		if (self.x > self.bar_right.x-self.width) and (last_x < self.bar_right.x-self.width) and (self.y > self.bar_right.y - self.height) and (self.y < self.bar_right.y+self.bar_right.height) and (self.vx > 0):
			self.x = last_x
			self.vx = - self.vx*self.bounce
			self.vy -= self.friction * self.bar_right.v
		if (self.x < self.bar_left.x + self.bar_left.width) and (last_x > self.bar_left.x + self.bar_left.width) and (self.y > self.bar_left.y - self.height) and (self.y < self.bar_left.y+self.bar_left.height) and (self.vx < 0):
			self.x = last_x
			self.vx = - self.vx*self.bounce
			self.vy -= self.friction * self.bar_left.v

		# reflect at top and bottom
		if (self.y > self.window.height-self.height) and (self.vy > 0):
			self.vy = - self.vy
		if (self.y < 0) and (self.vy < 0):
			self.vy = - self.vy

		return is_game_over