import json
import unittest
import csv
from MRTD import MachineReadableTravelDocument
import time
from MRTDTest import TestMachineReadableTravelDocument

if __name__ == '__main__':
    mrtd = MachineReadableTravelDocument()
    mrtdTest = TestMachineReadableTravelDocument()
    noOfLines = 10000
    
    """
    1. Measure performance time for DECODE with unit tests
    """
    with open('resources/records_encoded.json', 'r') as file:
        d = json.load(file)
    start_time = time.time()
    x = d.get('records_encoded')
    itr = x[:noOfLines]
    for index, val in enumerate(itr):
        mrtd.decode_mrz_input(val)

    unittest.main(exit = False)
    print("--- %s seconds ---" % (time.time() - start_time))
    encwounit = time.time() - start_time

    """
    2. Measure performance time for DECODE without unit tests
    """
    start_time = time.time()
    x = d.get('records_encoded')
    itr = x[:noOfLines]
    for index, val in enumerate(itr):
        mrtd.decode_mrz_input(val)
    print("--- %s seconds ---" % (time.time() - start_time))
    encunit = time.time() - start_time

    """
    3. Measure performance time for ENCODE with unit tests
    """
    with open('resources/records_decoded.json', 'r') as file:
        d = json.load(file)
    start_time = time.time()
    x = d.get('records_decoded')
    itr = x[:noOfLines]
    for index, val in enumerate(itr):
        mrtd.encode_mrz_input(val)

    unittest.main(exit = False)
    print("--- %s seconds ---" % (time.time() - start_time))
    decwounit = time.time() - start_time

    """
    4. Measure performance time for ENCODE without unit tests
    """
    start_time = time.time()
    x = d.get('records_decoded')
    itr = x[:noOfLines]
    for index, val in enumerate(itr):
        mrtd.encode_mrz_input(val)
    print("--- %s seconds ---" % (time.time() - start_time))
    decunit = time.time() - start_time

    """
    Print to CSV files
    """
    with open('csv/encode_{}.csv'.format(noOfLines), 'w') as file:
        writer = csv.writer(file)
        rowNumber = 1
        for i in range(rowNumber):
            row = [noOfLines, encwounit, encunit]
            writer.writerow(row)

    with open('csv/decode_{}.csv'.format(noOfLines), 'w') as file:
        writer = csv.writer(file)
        rowNumber = 1
        for i in range(rowNumber):
            row = [noOfLines, decwounit, decunit]
            writer.writerow(row)
