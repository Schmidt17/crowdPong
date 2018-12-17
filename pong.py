import pyglet
from pyglet.window import key
import ball
import bar
import random
import math
import numpy as np
import cv2

window = pyglet.window.Window()

# Create the pong rackets
barImage = pyglet.resource.image('whiteBar.png')

barSprite1 = bar.Bar(window, up_key=key.W, down_key=key.S, img=barImage)
barSprite1.scale_y = 2.  # stretch the bar image a bit vertically, looks nicer
barSprite1.x = 20
barSprite1.y = (window.height-barSprite1.height)//2
window.push_handlers(barSprite1.key_handler)  # the handler for key pressing events (created in the Bar class) is registered with the pyglet window

barSprite2 = bar.Bar(window, up_key=key.UP, down_key=key.DOWN, img=barImage)
barSprite2.scale_y = 2.   # stretch the bar image a bit vertically, looks nicer
barSprite2.x = window.width - barSprite2.width - 20
barSprite2.y = (window.height-barSprite2.height)//2
window.push_handlers(barSprite2.key_handler)  # the handler for key pressing events (created in the Bar class) is registered with the pyglet window

# Create the ball
circleImage = pyglet.resource.image('whiteCircle.png')
circleSprite = ball.Ball(barSprite1, barSprite2, window, img=circleImage)
circleSprite.scale = 0.1

# Create labels for the current racket velocities
label_left = pyglet.text.Label("Label links", x=5)
label_right = pyglet.text.Label("Label rechts", x=window.width-40)

# Start the video capture stream (from video device with id 0)
cap = cv2.VideoCapture(0)

# Get a frame for calibration and initializing the image. frame is a (h, w, 3)-axis numpy array with uint8 BGR color values (0..255)
ret, frame = cap.read()
# flip all the axes because conventions are the other way around in cv2
frame = np.flip(frame, axis=0)
frame = np.flip(frame, axis=1)
frame = np.flip(frame, axis=2)
# Calibration: record the average blue and red values (between 0 and 255) of both halves of the screen
blue_left_0 = np.mean(frame[:,:frame.shape[1]//2,2])
red_left_0 = np.mean(frame[:,:frame.shape[1]//2,0])
blue_right_0 = np.mean(frame[:,frame.shape[1]//2:,2])
red_right_0 = np.mean(frame[:,frame.shape[1]//2:,0])
# Create a pyglet image from the frame array. tobytes() converts the array to a bytestream.
backgroundImage = pyglet.image.ImageData(width=frame.shape[1], height=frame.shape[0], format='RGB', data=frame.tobytes())

# The (y-)velocities of the left and right racket, later determined from the current color values
velocity_left = 0.
velocity_right = 0.

def reset_game():
	""" 
	Put the ball in the middle of the screen and let it fly at a random angle (with some restriction).
	Center the rackets vertically.	
	"""
	circleSprite.x = (window.width-circleSprite.width)//2
	circleSprite.y = (window.height-circleSprite.height)//2

	# Calculate an initial velocity vector with magnitude circleSprite.v0
	# and an angle chosen randomly from the intervals [-pi/12, pi/12] in positive or negative x-direction (sign is 1 or -1)
	phi = math.pi/6. * random.random() - math.pi/12.  # random number between -pi/12 and pi/12 (i.e. -15 deg and 15 deg)
	sign = round(random.random())*2 - 1  # this gives -1 or 1 with equal probability;
	circleSprite.vx = sign*circleSprite.v0*math.cos(phi)  # sign = 1: velocity to the right, -1: to the left
	circleSprite.vy = circleSprite.v0*math.sin(phi)

	barSprite1.y = (window.height - barSprite1.height)//2
	barSprite2.y = (window.height - barSprite2.height)//2

@window.event
def on_draw():
	window.clear()

	# Draw the camera frame
	backgroundImage.blit(0, 0)

	# Display the current velocities as text
	label_left.text = "{0:.2f}".format(barSprite1.velocity)
	label_left.draw()
	label_right.text = "{0:.2f}".format(barSprite2.velocity)
	label_right.draw()

	# Display the ball and the rackets
	circleSprite.draw()
	barSprite1.draw()
	barSprite2.draw()


def update(dt):
	# Determine the raacket velocities
	ret, frame = cap.read()  # capture a frame from the camera stream
	# flip all the axes because conventions are the other way around in cv2
	frame = np.flip(frame, axis=0)
	frame = np.flip(frame, axis=1)
	frame = np.flip(frame, axis=2)

	# calculate the mean red and blue values of both halves, correcting for the initial calibration values
	# This gives values between 0 and 255 (however, 255 is improbable, since the calibration values will likely be > 0)
	blue_left = np.mean(frame[:,:frame.shape[1]//2,2]) - blue_left_0
	red_left = np.mean(frame[:,:frame.shape[1]//2,0]) - red_left_0
	blue_right = np.mean(frame[:,frame.shape[1]//2:,2]) - blue_right_0
	red_right = np.mean(frame[:,frame.shape[1]//2:,0]) - red_right_0

	# Racket velocity is red minus blue. 
	# Lots of red 	--> vel. is positive 	--> racket moves up fast
	# Lots of blue 	--> vel. is negative	--> racket moves down fast
	velocity_left = red_left - blue_left
	velocity_right = red_right - blue_right
	# Assign the velocities to the racket objects
	barSprite1.velocity = velocity_left
	barSprite2.velocity = velocity_right

	# Save the captured frame for later display
	backgroundImage.set_data('RGB', frame.shape[1]*3 , frame.tobytes())

	# Update all the gameplay objects
	# The update method of the ball also does the collision detection and returns whether it crashed into the left or right wall
	is_game_over = circleSprite.update(dt)
	barSprite1.update(dt)
	barSprite2.update(dt)
	if is_game_over:  # If the ball crashed into left or right wall:
		reset_game()  # Start over

# This schedules to call the function update(dt) every 1/120 seconds. update(dt) gets the time actually elapsed since the last call as the argument dt.
pyglet.clock.schedule_interval(update, 1./120.)

reset_game()  # set all gameplay objects to initial positions and velocities
pyglet.app.run()  # let's go!

# After the pyglet window is closed, release the video stream!
cap.release()
cv2.destroyAllWindows()