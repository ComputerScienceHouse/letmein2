import board, digitalio

s_stairs = digitalio.DigitalInOut(board.IO0)
n_stairs = digitalio.DigitalInOut(board.IO18)
level_a = digitalio.DigitalInOut(board.IO17)
level_1 = digitalio.DigitalInOut(board.IO7)
l_well = digitalio.DigitalInOut(board.IO6)

s_stairs.direction = digitalio.Direction.OUTPUT
level_1.direction = digitalio.Direction.OUTPUT
level_a.direction = digitalio.Direction.OUTPUT
n_stairs.direction = digitalio.Direction.OUTPUT
l_well.direction = digitalio.Direction.OUTPUT