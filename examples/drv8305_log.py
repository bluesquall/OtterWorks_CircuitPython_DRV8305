#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import subprocess
import time

import board
import busio
import digitalio
import otterworks_drv8305

logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S %z', level=logging.DEBUG)

# on beaglebone black, make sure SPI_1 pins are configured
# subprocess.run(["config-pin", "P9_17", "spi_cs"])
subprocess.run(["config-pin", "P9_18", "spi"])
subprocess.run(["config-pin", "P9_21", "spi"])
subprocess.run(["config-pin", "P9_22", "spi_sclk"])

cs = digitalio.DigitalInOut(board.P9_15)
cs.switch_to_output()
cs.value = False

spi = busio.SPI(board.SCK_1, board.MISO_1, board.MOSI_1)
drv8305 = otterworks_drv8305.OtterWorks_DRV8305(spi, cs)

while True:

    wwr = drv8305._get_warning_watchdog_reset().wwr # TODO: wrap _get methods

    if wwr.fault:
        level = logging.CRITICAL
    else:
        level = logging.INFO
    logging.log(level, "fault: {}".format(wwr.fault == True))

    if wwr.overtemp:
        level = logging.CRITICAL
    else:
        level = logging.INFO
    logging.log(level, "overtemperature: {}".format(wwr.overtemp == True))

    if wwr.pvdd_ov:
        level = logging.CRITICAL
    else:
        level = logging.INFO
    logging.log(level, "PVDD overvoltage: {}".format(wwr.pvdd_ov == True))

    if wwr.overtemp:
        level = logging.CRITICAL
    else:
        level = logging.INFO
    logging.log(level, "PVDD undervoltage: {}".format(wwr.pvdd_uv == True))

    if wwr.overtemp:
        level = logging.CRITICAL
    else:
        level = logging.INFO
    logging.log(level, "charge pump undervoltage: {}".format(wwr.vchp_uv == True))

    # TODO: temp 1-4, vds_status

    oc = drv8305._get_overcurrent().oc
    logging.debug("high-side overcurrents: A = {a}, B = {b}, C = {c}".format(
        a = (oc.high_a == True), b = (oc.high_b == True), c = (oc.high_c == True)))
    logging.debug("low-side overcurrents: A = {a}, B = {b}, C = {c}".format(
        a = (oc.low_a == True), b = (oc.low_b == True), c = (oc.low_c == True)))
    logging.debug("sense overcurrents: A = {a}, B = {b}, C = {c}".format(
        a = (oc.sense_a == True), b = (oc.sense_b == True), c = (oc.sense_c == True)))

    time.sleep(3)