import os

# GAME CONSTANTS
CARDSIZE = (350, 500)

# SOCKET CONSTANTS
PING_MESSAGE = "PING" # message sent when a server/client needs to know that a client/server is still connected.
PONG_MESSAGE = "PONG" # response sent back to the server/client by the client/server after they get a PING_MESSAGE.
TIMEOUT_TIME = 5.0  # seconds before a player is dropped for timing-out
PING_FREQUENCY = 1.0  # ping the server/client every X seconds to ensure there's still a connection.
DEFAULT_PORT = 27015

# FILE CONSTANTS
APPDATA_LOCATION = os.getenv('APPDATA').replace("\\","/")
DATA_LOCATION = APPDATA_LOCATION+"/TSSSF"

# TEXT ALIGNMENT CONSTANTS
ALIGN_TOPLEFT = 0
ALIGN_MIDDLE = 1

#MISC.
PRINTABLE_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890~`!@#$%^&*()_+-={}|:\"<>?[]\\;',./ "