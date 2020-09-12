def BCD2int(bcd):
    """
      Convert BCD number of an arbitrary length to an int.
      bcd (int)
        bcd number
      Returns the same number as an int.
    """
    value = 0
    nibble = 0
    while bcd:
        nibble_value = bcd & 0xf
        bcd >>= 4
        value += nibble_value * (10 ** nibble)
        nibble += 1
    return value


def int2BCD(value, length=1):
    """
      Convert an int into a BCD number.
      value (int)
        Integer value.
      length (int)
        Length limit for output number, in bytes.
      Returns the same value in BCD.
    """
    if value > 10 ** (length * 2 - 1):
        raise ValueError('Value %r cannot fit in %i bytes in BCD' %
             (value, length))
    bcd = 0
    nibble = 0
    while value:
        value, nibble_value = divmod(value, 10)
        bcd |= nibble_value << (4 * nibble)
        nibble += 1
    return bcd


def bytes_to_str(value):
    return ''.join([chr(c) for c in value])


def str_to_bytearray(value):
    return bytearray([ord(c) for c in value])


def create_iv():
    return (8 * '\0').encode('utf-8')
