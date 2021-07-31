# GBPrinterEmu
A GameBoy Printer emulator for use with Stacksmashing's GB link cable adapter, using [marian-m12l's gb-link-printer-firmware](https://github.com/marian-m12l/gb-link-printer-firmware)

# Some notes
- You can print more than one image without restarting the script
- You can also combine 3 red/green/filtered images into a single RGB image
- I'm still de-rusting on my Python knowledge so this is super janky but it works

# Dependencies
- Python 3
- pyusb > 1.1.1
- Pillow >= 8.2.0

# Credits
- Code for image decoding borrowed from https://github.com/lennartba/gbpinter_dump2image_py
