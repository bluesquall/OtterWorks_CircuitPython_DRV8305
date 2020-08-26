# The MIT License (MIT)
#
# Copyright (c) 2020 M J Stanway for Otter Works LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`otterworks_drv8305` - Otter Works DRV8305 - 
=========================================================================================

CircuitPython driver for Texas Instruments DRV8305 Three-Phase Gate Driver

* Author(s): bluesquall
"""
import ctypes
from time import sleep
from micropython import const


__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/bluesquall/OtterWorks_CircuitPython_DRV8305.git"

_DRV8305_WARNING_WATCHDOG_REGISTER = const(0x01)
_DRV8305_OV_VDS_FAULT_REGISTER = const(0x02)
_DRV8305_IC_FAULT_REGISTER = const(0x03)
_DRV8305_VGS_FAULT_REGISTER = const(0x04)
_DRV8305_HS_GATE_DRIVE_CONTROL_REGISTER = const(0x05)
_DRV8305_LS_GATE_DRIVE_CONTROL_REGISTER = const(0x06)
_DRV8305_GATE_DRIVE_CONTROL_REGISTER = const(0x07)
_DRV8305_RESERVED_REGISTER = const(0x08) # for completeness -- appears to always be zero
_DRV8305_IC_OPERATION_REGISTER = const(0x09)
_DRV8305_SHUNT_AMPLIFIER_CONTROL_REGISTER = const(0x0A)
_DRV8305_VOLTAGE_REGULATOR_CONTROL_REGISTER = const(0x0B)
_DRV8305_VDS_SENSE_CONTROL_REGISTER = const(0x0C)

class OtterWorks_DRV8305:
    """Driver for DRV8305 Three-Phase Gate Driver"""

    def __init__(self, spi, cs, baudrate=100000):
        import adafruit_bus_device.spi_device as spi_device  # pylint: disable=import-outside-toplevel
        self._spi = spi_device.SPIDevice(spi, cs, baudrate=baudrate)
        self._w = _DRV8305_SPI_Word()
        # check for a known response to confirm the DRV8395 is there

    def _read_register(self, register): # DRV8305 transactions are always 2 bytes
        with self._spi as spi:
            self._w.control.read = True
            self._w.control.register = register
            self._w.control.data = 0
            spi.write(bytes(self._w)) # TODO: why can't we use .as_bytes here?
            spi.readinto(self._w.as_bytes)
            # TODO ^    consider going back to write_readinto after
            #           confirming the same buffer can be used for both args
            return self._w

    def _write_register(self, register, data):
        with self._spi as spi:
            self._w.control.read = True
            self._w.control.register = register
            self._w.control.data = data
            spi.write(bytes(self._w)) # TODO: why can't we use .as_bytes here?
            spi.readinto(self._w.as_bytes)
            # TODO ^    consider going back to write_readinto after
            #           confirming the same buffer can be used for both args
            return self._w

    def _get_warning_watchdog_reset(self):
        return self._read_register(_DRV8305_WARNING_WATCHDOG_REGISTER)

    def _get_overcurrent(self):
        return self._read_register(_DRV8305_OV_VDS_FAULT_REGISTER)

class _Control(ctypes.BigEndianStructure):
    _fields_ = [
                ("read", ctypes.c_uint8, 1),
                ("address", ctypes.c_uint8, 4),
                ("data", ctypes.c_uint16, 11)
            ]

class _Warning_Watchdog_Reset_Flags(ctypes.BigEndianStructure):
    _fields_ = [
                ("empty", ctypes.c_uint8, 5),
                ("fault", ctypes.c_uint8, 1),
                ("reserved", ctypes.c_uint8, 1),
                ("temp4", ctypes.c_uint8, 1),
                ("pvdd_uv", ctypes.c_uint8, 1),
                ("pvdd_ov", ctypes.c_uint8, 1),
                ("vds_status", ctypes.c_uint8, 1),
                ("vchp_uv", ctypes.c_uint8, 1),
                ("temp1", ctypes.c_uint8, 1),
                ("temp2", ctypes.c_uint8, 1),
                ("temp3", ctypes.c_uint8, 1),
                ("overtemp", ctypes.c_uint8, 1),
            ]

class _Overcurrent_Flags(ctypes.BigEndianStructure):
    _fields_ = [
                ("empty", ctypes.c_uint8, 5),
                ("high_a", ctypes.c_uint8, 1),
                ("low_a", ctypes.c_uint8, 1),
                ("high_b", ctypes.c_uint8, 1),
                ("low_b", ctypes.c_uint8, 1),
                ("high_c", ctypes.c_uint8, 1),
                ("low_c", ctypes.c_uint8, 1),
                ("reserved", ctypes.c_uint8, 2),
                ("sense_c", ctypes.c_uint8, 1),
                ("sense_b", ctypes.c_uint8, 1),
                ("sense_a", ctypes.c_uint8, 1),
            ]

class _IC_Fault_Flags(ctypes.BigEndianStructure):
    _fields_ = [
                ("empty", ctypes.c_uint8, 5),
                ("pvdd_uv_2", ctypes.c_uint8, 1),
                ("watchdog", ctypes.c_uint8, 1),
                ("overtemp", ctypes.c_uint8, 1),
                ("reserved", ctypes.c_uint8, 1),
                ("vreg_uv", ctypes.c_uint8, 1),
                ("avdd_uv", ctypes.c_uint8, 1),
                ("low_gate_supply", ctypes.c_uint8, 1),
                ("reserved_2", ctypes.c_uint8, 1),
                ("high_charge_pump_uv_2", ctypes.c_uint8, 1),
                ("high_charge_pump_ov", ctypes.c_uint8, 1),
                ("high_charge_pump_ov_abs", ctypes.c_uint8, 1),
            ]

class _VGS_Fault_Flags(ctypes.BigEndianStructure):
    _fields_ = [
                ("empty", ctypes.c_uint8, 5),
                ("high_a", ctypes.c_uint8, 1),
                ("low_a", ctypes.c_uint8, 1),
                ("high_b", ctypes.c_uint8, 1),
                ("low_b", ctypes.c_uint8, 1),
                ("high_c", ctypes.c_uint8, 1),
                ("low_c", ctypes.c_uint8, 1),
                ("reserved", ctypes.c_uint8, 5),
            ]

class _Gate_Control(ctypes.BigEndianStructure):
    _fields_ = [
                ("empty", ctypes.c_uint8, 5),
                ("reserved", ctypes.c_uint8, 1),
                ("t_driven", ctypes.c_uint8, 2),
                ("i_peak_sink", ctypes.c_uint8, 4),
                ("i_peak_source", ctypes.c_uint8, 4),
            ]

class _Drive_Control(ctypes.BigEndianStructure):
    _fields_ = [
                ("empty", ctypes.c_uint8, 5),
                ("reserved", ctypes.c_uint8, 1),
                ("active_freewheeling", ctypes.c_uint8, 1),
                ("pwm_mode", ctypes.c_uint8, 2),
                ("dead_time", ctypes.c_uint8, 3),
                ("vds_sense_blanking", ctypes.c_uint8, 2),
                ("vds_sense_deglitch", ctypes.c_uint8, 2),
            ]

class _IC_Operation_Control(ctypes.BigEndianStructure):
    _fields_ = [
                ("empty", ctypes.c_uint8, 5),
                ("enable_OTSD", ctypes.c_uint8, 1),
                ("disable_PVDD_UVLO2", ctypes.c_uint8, 1),
                ("disable_GDRV_FAULT", ctypes.c_uint8, 1),
                ("enable_SNS_CLAMP", ctypes.c_uint8, 1),
                ("watchdog_delay", ctypes.c_uint8, 2),
                ("disable_SNS_OCP", ctypes.c_uint8, 1),
                ("enable_watchdog", ctypes.c_uint8, 1),
                ("sleep", ctypes.c_uint8, 1),
                ("clear_faults", ctypes.c_uint8, 1),
                ("set_VCPH_UV", ctypes.c_uint8, 1),
            ]

class _Shunt_Amplifier_Control(ctypes.BigEndianStructure):
    _fields_ = [
                ("empty", ctypes.c_uint8, 5),
                ("calibrate_3", ctypes.c_uint8, 1),
                ("calibrate_2", ctypes.c_uint8, 1),
                ("calibrate_1", ctypes.c_uint8, 1),
                ("blanking", ctypes.c_uint8, 2),
                ("gain_3", ctypes.c_uint8, 2),
                ("gain_2", ctypes.c_uint8, 2),
                ("gain_1", ctypes.c_uint8, 2),
            ]

class _Voltage_Regulator_Control(ctypes.BigEndianStructure):
    _fields_ = [
                ("empty", ctypes.c_uint8, 5),
                ("reserved", ctypes.c_uint8, 1),
                ("scaling", ctypes.c_uint8, 2),
                ("reserved_2", ctypes.c_uint8, 1),
                ("sleep_delay", ctypes.c_uint8, 2),
                ("disable_undervoltage_fault", ctypes.c_uint8, 1),
                ("undervoltage_setpoint", ctypes.c_uint8, 2),
            ]

class _Voltage_Sense_Control(ctypes.BigEndianStructure):
    _fields_ = [
                ("empty", ctypes.c_uint8, 5),
                ("reserved", ctypes.c_uint8, 3),
                ("comparator_threshold", ctypes.c_uint8, 5),
                ("mode", ctypes.c_uint8, 3),
            ]

class _DRV8305_SPI_Word(ctypes.Union):
    _fields_ = [
                ("as_word", ctypes.c_uint16),
                ("as_bytes", ctypes.c_byte * 2),
                ("control", _Control),
                ("wwr", _Warning_Watchdog_Reset_Flags),
                ("oc", _Overcurrent_Flags),
                ("ic_fault", _IC_Fault_Flags),
                ("vgs", _VGS_Fault_Flags),
                ("hs", _Gate_Control),
                ("ls", _Gate_Control),
                ("drive", _Drive_Control),
                ("ic_op", _IC_Operation_Control),
                ("shunt", _Shunt_Amplifier_Control),
                ("vreg", _Voltage_Regulator_Control),
                ("vsen", _Voltage_Sense_Control),
            ]

