import math

SI_PREFIX = {
    -18: {'multiplier': 10 ** 18, 'prefix': 'a'},
    -17: {'multiplier': 10 ** 18, 'prefix': 'a'},
    -16: {'multiplier': 10 ** 18, 'prefix': 'a'},
    -15: {'multiplier': 10 ** 15, 'prefix': 'f'},
    -14: {'multiplier': 10 ** 15, 'prefix': 'f'},
    -13: {'multiplier': 10 ** 15, 'prefix': 'f'},
    -12: {'multiplier': 10 ** 12, 'prefix': 'p'},
    -11: {'multiplier': 10 ** 12, 'prefix': 'p'},
    -10: {'multiplier': 10 ** 12, 'prefix': 'p'},
    -9: {'multiplier': 10 ** 9, 'prefix': 'n'},
    -8: {'multiplier': 10 ** 9, 'prefix': 'n'},
    -7: {'multiplier': 10 ** 9, 'prefix': 'n'},
    -6: {'multiplier': 10 ** 6, 'prefix': 'µ'},
    -5: {'multiplier': 10 ** 6, 'prefix': 'µ'},
    -4: {'multiplier': 10 ** 6, 'prefix': 'µ'},
    -3: {'multiplier': 10 ** 3, 'prefix': 'm'},
    -2: {'multiplier': 10 ** 3, 'prefix': 'm'},
    -1: {'multiplier': 10 ** 3, 'prefix': 'm'},
    0: {'multiplier': 1, 'prefix': ''},
    1: {'multiplier': 1, 'prefix': ''},
    2: {'multiplier': 1, 'prefix': ''},
    3: {'multiplier': 10 ** -3, 'prefix': 'k'},
    4: {'multiplier': 10 ** -3, 'prefix': 'k'},
    5: {'multiplier': 10 ** -3, 'prefix': 'k'},
    6: {'multiplier': 10 ** -6, 'prefix': 'M'},
    7: {'multiplier': 10 ** -6, 'prefix': 'M'},
    8: {'multiplier': 10 ** -6, 'prefix': 'M'},
    9: {'multiplier': 10 ** -9, 'prefix': 'G'},
    10: {'multiplier': 10 ** -9, 'prefix': 'G'},
    11: {'multiplier': 10 ** -9, 'prefix': 'G'},
    12: {'multiplier': 10 ** -12, 'prefix': 'T'},
    13: {'multiplier': 10 ** -12, 'prefix': 'T'},
    14: {'multiplier': 10 ** -12, 'prefix': 'T'},
    15: {'multiplier': 10 ** -15, 'prefix': 'P'},
    16: {'multiplier': 10 ** -15, 'prefix': 'P'},
    17: {'multiplier': 10 ** -15, 'prefix': 'P'},
    18: {'multiplier': 10 ** -18, 'prefix': 'E'},
}

# some units are not useful with prefix!
NO_Format = {"%", "°C", "h", "kWh", "ms", "MWh", "s", ""}


def convertNumberToNumberWithPrefix(number):
    if number == 0:
        return [number, '']
    exponent = math.floor(math.log10(math.fabs(number)))
    exponent = max(min(exponent, 18), -18)
    return [number * SI_PREFIX[exponent]['multiplier'], SI_PREFIX[exponent]['prefix']]


def formatWithPrefix(number, precision: int = 0, unit=""):
    if unit not in NO_Format:
        n, p = convertNumberToNumberWithPrefix(number)
    else:
        n = number
        p = ''
    return f"{n:.{precision}f} {p}{unit}"


# tests
if __name__ == '__main__':
    print(
        formatWithPrefix(1.189404E+022),
        formatWithPrefix(-4.07237500000000E+007),
        formatWithPrefix(1.943596E-005, 2, "F"),
        formatWithPrefix(1),
        formatWithPrefix(0.1),
        formatWithPrefix(0.001, 3, "A"),
        formatWithPrefix(0.002),
        formatWithPrefix(0.0011),
        formatWithPrefix(0.000999, 2),
        formatWithPrefix(5),
        formatWithPrefix(10),
        formatWithPrefix(100),
        formatWithPrefix(1000),
        formatWithPrefix(0),
        formatWithPrefix(-0.001),
        formatWithPrefix(-0.0011),
        formatWithPrefix(-0.000999, 1, "V"),
        formatWithPrefix(-10),
        formatWithPrefix(-100),
        formatWithPrefix(-1000)
    )
