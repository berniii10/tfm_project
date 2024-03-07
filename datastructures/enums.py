from enum import Enum

class Layer(Enum):
    PHY = "PHY"
    MAC = "MAC"
    RRC = "RRC"
    NAS = "NAS"
    RLC = "RLC"

class Direction(Enum):
    UL = "UL"
    DL = "DL"
    NA = "- "

"""
class Info(Enum):
    PDCCH = "PDCCH"
    PDSCH = "PDSCH"
    PRACH = "PRACH"
    PUCCH = "PUCCH"
    PUSCH = "PUSCH"
    PBCH = "PBCH"
    BCCHNR = "BCCH-NR"
    CCCHNR = "CCCH-NR"
    DCCHNR = "DCCH-NR"
    empty = "empty"
    _5GMM = "5GMM"
"""