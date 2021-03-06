#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time

import board
import busio
import digitalio
import otterworks_drv8305

# on beaglebone black, make sure SPI_1 pins are configured
subprocess.run(["config-pin", "P9_17", "spi_cs"])
subprocess.run(["config-pin", "P9_18", "spi"])
subprocess.run(["config-pin", "P9_21", "spi"])
subprocess.run(["config-pin", "P9_22", "spi_sclk"])

spi = busio.SPI(board.SCK_1, board.MISO_1, board.MOSI_1)
cs = digitalio.DigitalInOut(board.P9_17)
drv8305 = otterworks_drv8305.OtterWorks_DRV8305(spi, cs)

drv8305._spi.chip_select.value = False
time.sleep(50e-3)
drv8305._spi.chip_select.value = True
time.sleep(50e-3)
drv8305._spi.chip_select.value = False
time.sleep(50e-3)
drv8305._spi.chip_select.value = True
time.sleep(50e-3)
drv8305._spi.chip_select.value = False
time.sleep(50e-3)
drv8305._spi.chip_select.value = True
time.sleep(50e-3)
drv8305._spi.chip_select.value = False
time.sleep(50e-3)
drv8305._spi.chip_select.value = True

