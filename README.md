# FinalProject

| Group 6|
| ------ |
| Anna | 
| Habib ur Rehman| 
| Rajguru | 
| Sarthak | 
 


## Usage:

To access MRTD module and application code, first clone the latest master, then:

```
import json
from MRTD import MachineReadableTravelDocument

if __name__ == 'main':
    decoded_data = open('/path/to/file', 'r')
    input = json.load(decoded_data)

    mrtd = MachineReadableTravelDocument()
    encoded = mrtd.encode_mrz_input(input.get('obj'))

    decoded = mrtd.decode_mrz_input("<encoded_string>")
```

To run unit tests:

```
> python3 MRTDTest.py
```

To run unit tests with Coverage (must have Coverage library installed):

```
> coverage run MRTDTest.py
```
