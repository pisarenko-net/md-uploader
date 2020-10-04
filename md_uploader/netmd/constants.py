KNOWN_USB_ID_SET = frozenset([
    (0x04dd, 0x7202), # Sharp IM-MT899H
    (0x054c, 0x0075), # Sony MZ-N1 
    (0x054c, 0x0080), # Sony LAM-1 
    (0x054c, 0x0081), # Sony MDS-JB980 
    (0x054c, 0x0084), # Sony MZ-N505 
    (0x054c, 0x0085), # Sony MZ-S1 
    (0x054c, 0x0086), # Sony MZ-N707 
    (0x054c, 0x00c6), # Sony MZ-N10 
    (0x054c, 0x00c7), # Sony MZ-N910
    (0x054c, 0x00c8), # Sony MZ-N710/NF810 
    (0x054c, 0x00c9), # Sony MZ-N510/N610 
    (0x054c, 0x00ca), # Sony MZ-NE410/NF520D 
    (0x054c, 0x00eb), # Sony MZ-NE810/NE910
    (0x054c, 0x0101), # Sony LAM-10
    (0x054c, 0x0113), # Aiwa AM-NX1
    (0x054c, 0x014c), # Aiwa AM-NX9
    (0x054c, 0x017e), # Sony MZ-NH1
    (0x054c, 0x0180), # Sony MZ-NH3D
    (0x054c, 0x0182), # Sony MZ-NH900
    (0x054c, 0x0184), # Sony MZ-NH700/NH800
    (0x054c, 0x0186), # Sony MZ-NH600/NH600D
    (0x054c, 0x0188), # Sony MZ-N920
    (0x054c, 0x018a), # Sony LAM-3
    (0x054c, 0x01e9), # Sony MZ-DH10P
    (0x054c, 0x0219), # Sony MZ-RH10
    (0x054c, 0x021b), # Sony MZ-RH710/MZ-RH910
    (0x054c, 0x022c), # Sony CMT-AH10 (stereo set with integrated MD)
    (0x054c, 0x023c), # Sony DS-HMD1 (device without analog music rec/playback)
    (0x054c, 0x0286), # Sony MZ-RH1
])

WIREFORMAT_PCM = 0
WIREFORMAT_105KBPS = 0x90
WIREFORMAT_LP2 = 0x94
WIREFORMAT_LP4 = 0xA8

WIRE_TO_FRAME_SIZE = {
    WIREFORMAT_PCM: 2048,
    WIREFORMAT_LP2: 192,
    WIREFORMAT_105KBPS: 152, 
    WIREFORMAT_LP4: 96,
}

DISKFORMAT_LP4 = 0
DISKFORMAT_LP2 = 2
DISKFORMAT_SP_MONO = 4
DISKFORMAT_SP_STEREO = 6

WIRE_TO_DISK_FORMAT = {
    WIREFORMAT_PCM: DISKFORMAT_SP_STEREO,
    WIREFORMAT_LP2: DISKFORMAT_LP2,
    WIREFORMAT_105KBPS: DISKFORMAT_LP2,
    WIREFORMAT_LP4: DISKFORMAT_LP4,
}

ROOT_KEY = b"\x12\x34\x56\x78\x9a\xbc\xde\xf0\x0f\xed\xcb\xa9\x87\x65\x43\x21"
KEK = b"\x14\xe3\x83\x4e\xe2\xd3\xcc\xa5"
