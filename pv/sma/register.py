from datetime import timedelta
from time import localtime, strftime

from pymodbus.exceptions import NotImplementedException
from pymodbus.client import ModbusBaseClient
from .format_unit import formatWithPrefix


def _JsonPoint(measurement="series_name", fields={}, tags={}):
    # create a json point for write to influxDB
    return [{
            "measurement": measurement,
            "fields": fields,
            "tags": tags,
            # "time": time
            }]


class Register:
    def __init__(self, id, name, description, length, format=None, unit=None):
        self.id = id
        self.name = name
        self.description = description
        self.length = length
        self.value = None
        self.format = format
        self.unit = unit
        self.scalefactor, self.formatprecision = Register.getScale(format)
        self.noprefix = format in Register.NO_PREFIX_FORMATTING
        self._oh_name = None
        self._influx_tag = None

    def __str__(self):
        return f"{self.id} {self.name} ({self.description}) {self.get_formattedValue()}"

    def set_registers(self, registers):
        # Decode the registers and store it to value
        # If Value is Numeric in Subclass use scalefactor
        raise NotImplementedException()

    def get_formattedValue(self):
        if self.noprefix:
            return 'No Value' if self.value is None else f"{self.value} {self.unit}"
        elif self.format == "Dauer":
            return 'No Duration' if self.value is None else str(timedelta(seconds=self.value))
        elif self.format == "DT":
            return 'No Time' if self.value is None else strftime("%a, %d %b %Y %H:%M:%S", localtime(self.value))
        else:
            return 'No Value' if self.value is None else formatWithPrefix(self.value, self.formatprecision, self.unit)

    def get_value(self):
        return self.value

    def get_JSON(self, measurement, tags={}):
        # format Data to JSON, used to write Data to influxDB
        # append the Names and unit to TAGs
        # build the Tag-List by splitting the name by '.'
        if not self._influx_tag:
            parts = self.name.split('.')
            self._influx_tag = {
                'group': parts[0],
                'function': '.'.join(parts[1:]),
                'unit': self.unit
            }

        if self.format in Register.OUT_INFLUX_AS_STRING:
            return [] + _JsonPoint(measurement + "_status", {"value": self.get_formattedValue()}, tags | self._influx_tag)
        elif self.value is None:
            return []
        else:
            return [] + _JsonPoint(measurement, {"value": float(self.value)}, tags | self._influx_tag)

    """
    Produktübersicht SMA Solar Technology AG
    Technische Information SMA-Modbus-general-TI-de-10 14

    Format Erklärung
    Dauer Zeit in Sekunden, in Minuten oder in Stunden, je nach Modbus-Register (Ganzzahl)

    ENUM,TAGLIST Codierte Zahlenwerte. Die Aufschlüsselung der möglichen Codes fin-
    den Sie jeweils direkt unter der Bezeichnung des Modbus-Registers
    in den Zuordnungstabellen. Siehe modbuslist_de.html (Ganzzahl)

    FIX0 Dezimalzahl, kaufmännisch gerundet, ohne Nachkommastelle
    FIX1 Dezimalzahl, kaufmännisch gerundet, 1 Nachkommastelle
    FIX2 Dezimalzahl, kaufmännisch gerundet, 2 Nachkommastellen
    FIX3 Dezimalzahl, kaufmännisch gerundet, 3 Nachkommastellen
    FIX4 Dezimalzahl, kaufmännisch gerundet, 4 Nachkommastellen

    FUNKTION_SEC Das im Modbus-Register gespeicherte Datum wird bei Änderung an
    eine Funktion übergeben und startet diese. Nach Ausführen der
    Funktion ist kein Statuswert mehr gesetzt. Vor Ausführen der Funktion
    sollte in der Client-Software eine Sicherheitsabfrage vorgesehen
    werden.

    FW Firmware-Version (Ganzzahl)

    HW Hardware-Version z. B. 24 (Ganzzahl)

    IP4 4-Byte-IP-Adresse (IPv4) der Form XXX.XXX.XXX.XXX (Nicht implemetiert nur als (Ganzzahl))

    RAW Text oder Zahl. Eine RAW-Zahl hat keine Nachkommastellen und
    keine Tausender- oder sonstigen Trennzeichen. (Ganzzahl)

    REV Revisionsnummer der Form 2.3.4.5 (Ganzzahl)

    TEMP Temperaturwerte werden in speziellen Modbus-Registern in Grad
    Celsius (°C), in Grad Fahrenheit (°F) oder in Kelvin (K) gespeichert.
    Die Werte sind kaufmännisch gerundet, mit einer Nachkommastelle. (FIX1)

    TM UTC-Zeit, in Sekunden (Ganzzahl)

    UTF8 Daten im Format UTF8

    DT Datum/Uhrzeit, gemäß der Ländereinstellung (Übertragung in Se-
    kunden seit 01.01.1970) (Ganzzahl)
    """
    FORMATS = {
        "FIX1": [0.1, 1],
        "FIX2": [0.01, 2],
        "FIX3": [0.001, 3],
        "FIX4": [0.0001, 4],
        "TEMP": [0.1, 1]
    }

    NO_PREFIX_FORMATTING = {"UTF8", "TM", "REV", "RAW", "IP4", "HW", "FW"}

    OUT_OPENHAB_AS_STRING = {"UTF8", "TM", "TAGLIST", "Dauer", "DT"}

    OUT_INFLUX_AS_STRING = {"UTF8", "TM", "TAGLIST", "DT"}

    OUT_OPENHAB_NONE_AS_0 = {"W", "A", "VAr", "VA"}

    @staticmethod
    def getScale(format):
        if format is None:
            return [1, 0]
        f = Register.FORMATS.get(format, [1, 0])
        return f

    SMA_TAGLIST = {}  # must assigned on startup! see sma.py for example


def hex_to_signed(source):
    """Convert a string hex value to a signed hexidecimal value.

    This assumes that source is the proper length, and the sign bit
    is the first bit in the first byte of the correct length.

    hex_to_signed("F") should return -1.
    hex_to_signed("0F") should return 15.
    """
    if not isinstance(source, str):
        raise ValueError("string type required")
    if 0 == len(source):
        raise ValueError("string is empty")
    sign_bit_mask = 1 << (len(source) * 4 - 1)
    other_bits_mask = sign_bit_mask - 1
    value = int(source, 16)
    return -(value & sign_bit_mask) | (value & other_bits_mask)


S16_NAN = hex_to_signed("8000")


class S16(Register):
    def __init__(self, register_id, name, description, format=None, unit=''):
        Register.__init__(self, register_id, name, description, 1, format, unit)

    def set_registers(self, registers):
        v = ModbusBaseClient.convert_from_registers(registers, ModbusBaseClient.DATATYPE.INT16)
        # direct compare to 0x8000 doesn't work because 0x8000 is two's complement!!!
        # v==0x8000 is c/c++ style! This will only work in python for unsigned ints
        self.value = None if v == S16_NAN else v * self.scalefactor


S32_NAN = hex_to_signed("80000000")


class S32(Register):
    def __init__(self, register_id, name, description, format=None, unit=''):
        Register.__init__(self, register_id, name, description, 2, format, unit)

    def set_registers(self, registers):
        v = ModbusBaseClient.convert_from_registers(registers, ModbusBaseClient.DATATYPE.INT32)
        self.value = None if v == S32_NAN else v * self.scalefactor


class U16(Register):
    def __init__(self, register_id, name, description, format=None, unit=''):
        Register.__init__(self, register_id, name, description, 1, format, unit)

    def set_registers(self, registers):
        v = ModbusBaseClient.convert_from_registers(registers, ModbusBaseClient.DATATYPE.UINT16)
        self.value = None if v == 0xFFFF else v * self.scalefactor


class U32(Register):
    def __init__(self, register_id, name, description, format=None, unit=''):
        Register.__init__(self, register_id, name, description, 2, format, unit)

    def set_registers(self, registers):
        v = ModbusBaseClient.convert_from_registers(registers, ModbusBaseClient.DATATYPE.UINT32)
        self.value = None if v == 0xFFFFFFFF or v == 0xFFFFFD else v * self.scalefactor

        if self.value and self.format == "TAGLIST":
            self.raw_value = self.value
            self.value = Register.SMA_TAGLIST.get(self.value, f"Unknown Value {self.value}")

    def get_formattedValue(self):
        if self.value and self.format == "TAGLIST":
            return self.value
        else:
            return super().get_formattedValue()


class U64(Register):
    def __init__(self, register_id, name, description, format=None, unit=''):
        Register.__init__(self, register_id, name, description, 4, format, unit)

    def set_registers(self, registers):
        v = ModbusBaseClient.convert_from_registers(registers, ModbusBaseClient.DATATYPE.UINT64)
        self.value = None if v == 0xFFFFFFFFFFFFFFFF else v * self.scalefactor


class STR32(Register):
    # STR32 Registers have variable length see modbuslist_de.html
    # Format is ignored ... it is always utf-8; unit is also ignored
    def __init__(self, register_id, name, description, length=16):
        if length < 1:
            raise "STR32 Register must have length > 0"
        Register.__init__(self, register_id, name, description, length, "UTF8", "")

    def set_registers(self, registers):
        # size is in bytes! one modbus register is 2 bytes wide
        # new pymodbus: converts full register to string and convert to string and remove trailing Null-Chars
        s = ModbusBaseClient.convert_from_registers(registers, ModbusBaseClient.DATATYPE.STRING)
        s = s.strip()

        self.value = None if s == "" else s

    def get_formattedValue(self):
        return self.value
