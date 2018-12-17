import pyglet
from pyglet.window import key

class Bar(pyglet.sprite.Sprite):
	def __init__(self, window, up_key, down_key, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.v0 = 150
		self.v = 0
		self.window = window
		self.up_key = up_key
		self.down_key = down_key

		self.key_handler = key.KeyStateHandler()  # this provides a dictionary that contains whether a particular key is currently pressed (see below for usage)

		self.velocity = 0.

	def update(self, dt):
		if self.key_handler[self.up_key]:
			self.v = self.v0  # prepare for moving up
		elif self.key_handler[self.down_key]:
			self.v = -self.v0  # prepare for moving down
		else:
			self.v = self.velocity
			# self.v = 0  # Use this for playing traditionally, only with the keyboard

		# Check if we move into the top or bottom wall (so check position AND velocity).
		# If so, don't go further in that direction. Going in the opposite direction is ok (we don't want to get stuck).
		if not ((self.y < 0 and self.v < 0) or (self.y + self.height > self.window.height and self.v > 0)):
			self.y += self.v*dt  # Move!