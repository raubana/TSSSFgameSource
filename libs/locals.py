import os

# GAME CONSTANTS
CARDSIZE = (350, 500)

# SOCKET CONSTANTS
PING_MESSAGE = "PING" # message sent when a server/client needs to know that a client/server is still connected.
PONG_MESSAGE = "PONG" # response sent back to the server/client by the client/server after they get a PING_MESSAGE.
TIMEOUT_TIME = 10.0  # seconds before a player is dropped for timing-out
PING_FREQUENCY = 2.0  # ping the server/client every X seconds to ensure there's still a connection.
BUFFERSIZE = 2048 # the size of the buffer used in the sockets
MESSAGE_DELAY = 0.1 # the delay between sent messages to prevent buffer overflows
DEFAULT_PORT = 27015
ESCAPE_CHARACTER = str(chr(6))+str(chr(6))

# FILE CONSTANTS
APPDATA_LOCATION = os.getenv('APPDATA').replace("\\","/")
DATA_LOCATION = APPDATA_LOCATION+"/TSSSF"

# TEXT ALIGNMENT CONSTANTS
ALIGN_TOPLEFT = 0
ALIGN_MIDDLE = 1

#GUI CONSTANTS
LAYOUT_FLOW = 0
LAYOUT_VERTICAL = 1

SCROLLBAR_VERTICAL = 0
SCROLLBAR_HORIZONTAL = 1
SCROLLBAR_WIDTH = 15
SCROLLBAR_BAR_MINSIZE = 10

#MISC.
PRINTABLE_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890~`!@#$%^&*()_+-={}|:\"<>?[]\\;',./ "