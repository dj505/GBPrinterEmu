from PIL import Image, ImageDraw
import time
import os
import platform
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

def CreateImage(data, colours=((WHITE, DARK_GREY), (LIGHT_GREY, BLACK))):
    if len(data) == 0:
        print("There's nothing to do. Exiting...")
        exit()

    data = bytes.fromhex(data)

    print(f"{str(len(data))} bytes to print...")

    dump = [data[i:i+16] for i in range(0, len(data), 16)]    # 16 bytes per tile
    print(f"{str(len(dump))} tiles to print...")

    TILE_HEIGHT = len(dump) // TILE_WIDTH
    print(f"{TILE_HEIGHT} lines to print...")

    try:
        img = Image.new(mode='RGB', size=(TILE_WIDTH * 8, TILE_HEIGHT * 8))
        pixels = img.load()
        for h in range(TILE_HEIGHT):
            for w in range(TILE_WIDTH):
                tile = dump[(h*TILE_WIDTH) + w]
                for i in range(8):
                    for j in range(8):
                        hi = (tile[i * 2] >> (7 - j)) & 1
                        lo = (tile[i * 2 + 1] >> (7 - j)) & 1
                        pixels[(w * 8) + j, (h * 8) + i] = colours[hi][lo]

        img.save(f"images/decoded_{time.strftime('%Y%m%d - %H%M%S')}.png")
        print("Saved!")
        exit()
    except IndexError as e:
        print("Provided data doesn't match expected size, " \
              "please double check your hex dump!")
        exit()

def CreateImageRGB(red_data, green_data, blue_data, colours=((WHITE, DARK_GREY), (LIGHT_GREY, BLACK))):
    if len(red_data) == 0:
        print("No data for red later, can't do anything. Exiting...")
        exit()
    elif len(green_data) == 0:
        print("No data for green later, can't do anything. Exiting...")
        exit()
    elif len(blue_data) == 0:
        print("No data for blue later, can't do anything. Exiting...")
        exit()

    red_data = bytes.fromhex(red_data)
    green_data = bytes.fromhex(green_data)
    blue_data = bytes.fromhex(blue_data)

    print(f"{str(len(red_data))} bytes to print...")

    red_dump = [red_data[i:i+16] for i in range(0, len(red_data), 16)]
    print(f"{str(len(red_dump))} red tiles to print...")

    green_dump = [green_data[i:i+16] for i in range(0, len(green_data), 16)]
    print(f"{str(len(green_dump))} green tiles to print...")

    blue_dump = [blue_data[i:i+16] for i in range(0, len(blue_data), 16)]
    print(f"{str(len(blue_dump))} blue tiles to print...")

    TILE_HEIGHT = len(red_dump) // TILE_WIDTH
    print(f"{TILE_HEIGHT} lines to print...")

    try:
        red_img = Image.new(mode='RGB', size=(TILE_WIDTH * 8, TILE_HEIGHT * 8))
        red_pixels = red_img.load()
        for h in range(TILE_HEIGHT):
            for w in range(TILE_WIDTH):
                tile = red_dump[(h*TILE_WIDTH) + w]
                for i in range(8):
                    for j in range(8):
                        hi = (tile[i * 2] >> (7 - j)) & 1
                        lo = (tile[i * 2 + 1] >> (7 - j)) & 1
                        red_pixels[(w * 8) + j, (h * 8) + i] = colours[hi][lo]
        red_img = red_img.convert("L")

        green_img = Image.new(mode='RGB', size=(TILE_WIDTH * 8, TILE_HEIGHT * 8))
        green_pixels = green_img.load()
        for h in range(TILE_HEIGHT):
            for w in range(TILE_WIDTH):
                tile = green_dump[(h*TILE_WIDTH) + w]
                for i in range(8):
                    for j in range(8):
                        hi = (tile[i * 2] >> (7 - j)) & 1
                        lo = (tile[i * 2 + 1] >> (7 - j)) & 1
                        green_pixels[(w * 8) + j, (h * 8) + i] = colours[hi][lo]
        green_img = green_img.convert("L")

        blue_img = Image.new(mode='RGB', size=(TILE_WIDTH * 8, TILE_HEIGHT * 8))
        blue_pixels = blue_img.load()
        for h in range(TILE_HEIGHT):
            for w in range(TILE_WIDTH):
                tile = blue_dump[(h*TILE_WIDTH) + w]
                for i in range(8):
                    for j in range(8):
                        hi = (tile[i * 2] >> (7 - j)) & 1
                        lo = (tile[i * 2 + 1] >> (7 - j)) & 1
                        blue_pixels[(w * 8) + j, (h * 8) + i] = colours[hi][lo]
        blue_img = blue_img.convert("L")

        rgb_image = Image.merge("RGB", (red_img, green_img, blue_img))
        rgb_image.save(f"images/decoded_rgb_{time.strftime('%Y%m%d - %H%M%S')}.png")
        print("Saved!")
        exit()
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

if platform.system() != "Windows":
    if dev.is_kernel_driver_active(0):
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

intf = usb.util.find_descriptor(
    cfg,
    bInterfaceClass = 0xff,
    iInterface = 0x5
)
print(intf)

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

print("Control transfer to enable webserial...")
try:
    dev.ctrl_transfer(bmRequestType = 1, bRequest = 0x22, wIndex = 2, wValue = 0x01)
except USBError as e:
    print("Error sending the control transfer.")
    exit()

print("Connection established!")

#########################
# Image Data Collection #
#########################

def CollectData():
    data = ""
    print("Waiting for data...")
    while True:
        recv = epIn.read(epIn.wMaxPacketSize, 30000)
        data += ('%s' % '{:{fill}{width}{base}}'.format(int.from_bytes(recv, byteorder='big'), fill='0', width=len(recv*2), base='x'))
        # print(len(data))
        if len(data) == 11520:
            break
    return data

# Start image processing with the (hopefully) collected data
if not os.path.exists("images"):
    print("'images' directory does not exist, creating it...")
    os.makedirs("images")

##################
# Select options #
##################

print("Please pick an option:\n\
1. Print single image\n\
2. Combine RGB images\n")

choice = input("Number: ")

if choice.startswith("1"):
    while True:
        CreateImage(CollectData())
        another = input("Print another? (Y/N): ")
        if another.startswith("Y"):
            continue
        else:
            exit()

elif choice.startswith("2"):
    while True:
        print("Please print your red layer")
        red_data = CollectData()
        print("Please print your green layer")
        green_data = CollectData()
        print("Please print your blue layer")
        blue_data = CollectData()
        CreateImageRGB(red_data, green_data, blue_data)
        another = input("Print another? (Y/N): ")
        if another.startswith("Y"):
            continue
        else:
            exit()
