"""
**ACC_FSR_CHAR** *Default value is ACC_SCALE_2G*
```
ACC_SCALE_2G: 0x00
ACC_SCALE_4G: 0x01
ACC_SCALE_8G: 0x02
ACC_SCALE_16G: 0x03
```
"""

ACC_FSR_CHAR = {2: 0x00, 4: 0x01, 8: 0x02, 16: 0x03}
GYRO_FSR_CHAR = {250: 0x00, 500: 0x01, 1000: 0x02, 2000: 0x03}
DATA_RATE = {10: 0x00, 20: 0x01, 50: 0x02, 100: 0x03,
             200: 0x04, 500: 0x05, 1000: 0x06,
             1: 0x10, 5: 0x11, 40: 0x13}
ACC_FSR_CHAR_MAP = {0x00: 2, 0x01: 4, 0x02: 8, 0x03: 16}
GYRO_FSR_CHAR_MAP = {0x00: 250, 0x01: 500, 0x02: 1000, 0x03: 2000}
DATA_RATE_MAP = {0x00: 10, 0x01: 20, 0x02: 50, 0x03: 100,
                 0x04: 200, 0x05: 500, 0x06: 1000,
                 0x10: 1, 0x11: 5, 0x13: 40}
