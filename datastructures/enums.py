from enum import Enum

class Layer(Enum):
    PHY = "PHY"
    MAC = "MAC"
    RRC = "RRC"
    NAS = "NAS"
    RLC = "RLC"
    S1AP = "S1AP"

class Direction(Enum):
    UL = "UL"
    DL = "DL"
    NA = "- "

class Channel(Enum):
    PUSCH = "PUSCH"
    PUCCH = "PUCCH"
    PRACH = "PRACH"
    PDSCH = "PDSCH"
    PDCCH = "PDCCH"

class MessagesRrc(Enum):
    RRC_setup_request = " RRC setup request"
    RRC_setup = "RRC setup"
    RRC_setup_complete = "RRC setup complete"
    DL_information_transfer = "DL information transfer"
    UL_information_transfer = "UL information transfer"
    Security_mode_command = "Security mode command"
    Security_mode_complete = "Security mode complete"
    UE_capability_enquiry = "UE capability enquiry"
    UE_capability_information = "UE capability information"
    RRC_reconfiguration = "RRC reconfiguration"
    RRC_reconfiguration_complete = "RRC reconfiguration complete"
    
    SIB1 = "SIB1"

class MessagesNas(Enum):
    Identity_request = "Identity request"
    Identity_response = "Identity response"
    Authentication_request = "Authentication request"
    Authentication_response = "Authentication response"
    Security_mode_command = "Security mode command"
    Security_mode_complete = "Security mode complete"
    Registration_accept = "Registration accept"
    Registration_complete = "Registration complete"
    Configuration_update_command = "Configuration update command"



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