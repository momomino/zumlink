from enum import Enum

class DataRate(Enum):
    """ ENUM representing ZUM radio Data Rates """
    RATE_4M = "RATE_4M"
    RATE_1M = "RATE_1M"
    RATE_1_5M_BETA_FEATURE = "RATE_1.5M_BETA_FEATURE"
    RATE_500K = "RATE_500K"
    RATE_250K = "RATE_250K"
    RATE_115_2K = "RATE_115.2K"