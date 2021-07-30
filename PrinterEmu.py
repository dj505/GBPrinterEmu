from PIL import Image, ImageDraw
import time
import os
import usb.util
import usb.core

########################
# Imade decoding stuff #
########################

# Bits and pieces (the important decoding stuff, really) borrowed from
# https://github.com/lennartba/gbpinter_dump2image_py/blob/master/dump2img.py
# The original doesn't have a license, so I'll credit the contributers here:
# - lennartba
# - Cabalist / Ryan Jarvis
# - BjornB2

BLACK = (0, 0, 0)
DARK_GREY = (90, 90, 90)
LIGHT_GREY = (180, 180, 180)
WHITE = (255, 255, 255)

TILE_WIDTH = 20
TILE_HEIGHT = 18
TILE_SIZE = TILE_WIDTH * TILE_HEIGHT

def CreateImage(hexdata, colours=((WHITE, DARK_GREY), (LIGHT_GREY, BLACK))):
    if len(hexdata) == 0:
        print("There's nothing to do. Exiting...")
        exit()

    dump = hexdata.splitlines()
    print(f"\n{str(len(dump))} lines to print...\n")

    for c in range(len(dump) // TILE_SIZE):
        try:
            img = Image.new(mode='RGB', size=(TILE_WIDTH * 8, TILE_HEIGHT * 8))
            pixels = img.load()
            for h in range(TILE_HEIGHT):
                for w in range(TILE_WIDTH):
                    tile = bytes.fromhex(dump[(c*TILE_SIZE) + (h*TILE_WIDTH) + w])
                    for i in range(8):
                        for j in range(8):
                            hi = (tile[i * 2] >> (7 - j)) & 1
                            lo = (tile[i * 2 + 1] >> (7 - j)) & 1
                            pixels[(w * 8) + j, (h * 8) + i] = colours[hi][lo]

            img.save(f"images/decoded_{time.strftime('%Y%m%d - %H%M%S')}.png")
            print("Saved!")
        except IndexError as e:
            print("Provided data doesn't match expected size, " \
                  "please double check your hex dump!")
            exit()

#############
# USB stuff #
#############

dev = usb.core.find(idVendor=0xcafe, idProduct=0x4011)

if dev is None:
    print("I could not find your link cable adapter!")
    exit()

reattach = False

if dev.kernel_driver_is_active(0):
    try:
        reattach = True
        dev.detach_kernel_driver(0)
        print("Detached kernel driver...")
    except usb.core.USBError as e:
        print("Could not detach kernel driver :(")
        exit()
else:
    print("No kernel driver attached...")

dev.reset()
dev.set_configuration()

cfg = dev.get_active_configuration()

print(f"Configuration: {cfg}")

intf = cfg[(2,0)]
print(f"Interface: {intf}")

epIn = usb.util.find_descriptor(
    intf,
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_IN)

if epIn is None:
    print("Could not establish an In endpoint.")
    exit()

epOut = usb.util.find_descriptor(
    intf,
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_OUT)

if epOut is None:
    print("Could not establish an Out endpoint.")
    exit()

print("Control transfer to enable WebUSB...")
dev.ctrl_transfer(bmRequestType = 1, bRequest = 0x22, wIndex = 2, wValue = 0x01)

data = []

# Start image processing with the (hopefully) collected data
if not os.path.exists("images"):
    print("'images' directory does not exist, creating it...")
    os.makedirs("images")

# CreateImage(data)
