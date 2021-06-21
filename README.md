# GBPrinterEmu
A GameBoy Printer emulator for use with Stacksmashing's GB link cable adapter

As of right now, it doesn't do much, because of the lack of SPI secondary support (easy fix, but I don't know any C)  

# Some notes
- Currently, all this does is connect to the adapter, establish some endpoints, and then disconnect. Working image decoding code is present, but isn't used because there's no way to respond to the GameBoy and read data back from the adapter yet
- Only the image decoding is guaranteed to work right now, and only if the data is added to the list properly
- This is my first time ever doing anything libusb related so there may be too much or too little code present to handle the USB connection
- I haven't written any Python in a while so I'm sorry if the code is messy!

# Dependencies
- Python 3
- pyusb > 1.1.1
- Pillow >= 8.2.0

# Credits
- Code for image decoding borrowed from https://github.com/lennartba/gbpinter_dump2image_py
