import os

__all__ = (
    "cap_area",
    "bob_track_probe",
    "bob_color_diff",
    "splash_diff_thresh",
    "bob_fade_thresh",
    "splash_radius",
    "max_wait_time",
    "init_wait_time",
    "shift_right_speed",
    "sct_check_iters",
    "sct_check_pause"
)

# capture area
cap_area = {'top': 70, 'left': 70, 'width': 1134, 'height': 650}

# size of bob finder probe in pixels
bob_track_probe = 20

# difference threshold. lower value will be more sensitive and may get false
# positives
bob_color_diff = 2.

# splash threshold. lower value will be more sensitive and may get false
# positives
splash_diff_thresh = 1.2

# fade threshold. not that important. determines when the bobber fades away
bob_fade_thresh = -4.

# size of box surrounding bobber. adjust until cursor draws a box just outside
# but fully around the bobber
splash_radius = 40

# max amount of time to wait for splash
max_wait_time = 30

# wait time in seconds between cycles
init_wait_time = 5

# make this a little higher if HereFishy appears to be right clicking, not
# shift right clicking
shift_right_speed = 0.1

# screenshot validity check iterations. decrease to increase sensitivity and
# speed, but may find false positives
sct_check_iters = 3

# validity check pause time in seconds. time between validity checks
sct_check_pause = .15

# developer mode on or off
_dev_mode = False

os = os.name
