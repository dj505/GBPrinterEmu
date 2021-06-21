from PIL import Image, ImageDraw
import time
import os
import usb.core
import usb.util

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

# Look for the TinyUSB device (unsure if this is enough or if I need to check
# for the Adafruit vendor ID as well, we'll find out I guess)
adapter = usb.core.find(idVendor=0xcafe, idProduct=0x4011)

# Try to establish A Link to the Past-- I mean, to the cable
if adapter is None:
    print("I can't find your link cable adapter!")
    exit()
else:
    print("Found the link cable adapter! Connecting...")
    if adapter.is_kernel_driver_active(0): # Check if the kernel driver is using
        reattach = True                    # the device, and disconnect it if it
        adapter.detach_kernel_driver(0)    # is so that we can claim it instead
    try:
        adapter.set_configuration()
        usb.util.claim_interface(adapter, 0) # Claim the interface
    except IOError as err:
        if "Resource busy" in err:
            print("The device seems to be busy/in use. Exiting...")
        else:
            print("Something went wrong, but I'm not sure what. Exiting...")
        exit()

# Get the device's active configuration
cfg = adapter.get_active_configuration()
intf = cfg[(0,0)]

# This is where we want to talk to the adapter, receive the image data,
# add the necessary parts of that data to a list to pass it to CreateImage(),
# send some keepalive stuff, and so on - not completely sure what to do
# past here quite yet until the adapter supports SPI secondary mode

# We're gonna need an endpoint to read from (and write to?), probably
# I really don't know but we'll find out
ep = usb.util.find_descriptor(
    intf,
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_IN)

# I don't know if we want an IN endpoint or OUT endpoint
# Probably one of each actually, for two way communication?
# But it can't currently seem to find an OUT endpoint and idk what I'm doing yet
if ep is not None:
    print("IN endpoint established...")
else:
    print("Endpoint could not be established. Exiting...")
    exit()

# Put the image data into this list
data = []
# There's no communication yet tho, so this is about the best I can do for now

# Disconnect the adapter and pass control back to the kernel driver
usb.util.release_interface(adapter, intf)
adapter.attach_kernel_driver(0)
print("Disconnected from adapter...")

# Start image processing with the (hopefully) collected data
if not os.path.exists('images'):
    print("'images' directory does not exist, creating it...")
    os.makedirs('images')

CreateImage(data)
