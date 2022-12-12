import re
import json
from CharacterMap import CharacterMap

# assume that line length will be at most 44 characters
MAX_MRZ_LENGTH=44

class MachineReadableTravelDocument:
    def __init__(self):
        self.decoded_mrz = {}
        self.encoded_mrz = ""
        self.cmap = CharacterMap().character_map

    """ 
    Empty method that returns an empty String to emulate hardware scanner 
    """
    def scan_mrz(hardware_scanner: None) -> str:
        return ""
    
    """ 
    Empty method that queries DB layer to get fields for User 
    """
    def get_fields_for_user(last_name: str, given_name: str, personal_number: str) -> str:
        return None

    """
    Method to take given MRZ input from scanner
    and prepare JSON payload for DB to commit/save
    """
    def decode_mrz_input(self, encoded_mrz: str) -> dict():
        lines = encoded_mrz.split(";")
        if len(lines) != 2:
            raise Exception("The MRZ input provided cannot be parsed because there were not two identifiable MRZ lines")
        
        line_1 = lines[0]
        line_2 = lines[1]

        # line_1 decoding
        country_name_combo = re.findall(r"\<(.*?)\<", line_1)[0]
        names = re.findall(r"\<{2}(.*?)\<(.*?)\<+", line_1)[0] # returns tuple
        given_name = ' '.join(names)

        self.decoded_mrz["document_type"] = line_1[0]
        self.decoded_mrz["issuing_country"] = country_name_combo[0:3]
        self.decoded_mrz["last_name"] = country_name_combo[3:len(country_name_combo)]
        self.decoded_mrz["given_name"] = given_name.strip()

        # line_2 decoding
        passport_number = line_2[0:9]
        passport_check_digit = int(line_2[9])
        country_code = line_2[10:13]
        birth_date = line_2[13:19]
        birth_date_check_digit = int(line_2[19])
        sex = line_2[20]
        expiration_date = line_2[21:27]
        expiration_date_check_digit = int(line_2[27])
        personal_number = re.findall(r"(.*?)\<+", line_2[28:len(line_2)])[0]
        personal_number_check_digit = int(re.findall(r"\<+(\d+)$", line_2)[0])

        if (
            self.is_check_digit_valid(field=passport_number, check_digit=passport_check_digit, field_identifier="Passport") and
            self.is_check_digit_valid(field=birth_date, check_digit=birth_date_check_digit, field_identifier="Birth Date") and
            self.is_check_digit_valid(field=expiration_date, check_digit=expiration_date_check_digit, field_identifier="Expiration Date") and
            self.is_check_digit_valid(field=personal_number, check_digit=personal_number_check_digit, field_identifier="Personal Number")
        ):
            self.decoded_mrz["passport_number"] = passport_number
            self.decoded_mrz["country_code"] = country_code
            self.decoded_mrz["birth_date"] = birth_date
            self.decoded_mrz["sex"] = sex
            self.decoded_mrz["expiration_date"] = expiration_date
            self.decoded_mrz["personal_number"] = personal_number
        
        return self.decoded_mrz

    """
    Method to take given JSON payload for passport holder
    and convert it into MRZ compatible format
    """
    def encode_mrz_input(self, decoded_mrz: dict) -> str:
        # validate dict() input from json file is formatted correctly
        if 'line1' in decoded_mrz and 'line2' in decoded_mrz:
            line_1 = decoded_mrz['line1']
            line_2 = decoded_mrz['line2']
        else:
            raise KeyError('The decoded MRZ data provided does not contain the key-value pairs expected. Aborting operation.')
        
        exception_string = 'The expected field \'{}\' was not found in line {} of the decoded MRZ Input. Aborting operation.'

        # validate presence of each expected field
        if 'issuing_country' not in line_1:
            raise Exception(exception_string.format('issuing_country', 1))
        if 'last_name' not in line_1:
            raise Exception(exception_string.format('last_name', 1))
        if 'given_name' not in line_1:
            raise Exception(exception_string.format('given_name', 1))
        
        if 'passport_number' not in line_2:
            raise Exception(exception_string.format('passport_number', 2))
        if 'country_code' not in line_2:
            raise Exception(exception_string.format('country_code', 2))
        if 'birth_date' not in line_2:
            raise Exception(exception_string.format('birth_date', 2))
        if 'sex' not in line_2:
            raise Exception(exception_string.format('sex', 2))
        if 'expiration_date' not in line_2:
            raise Exception(exception_string.format('expiration_date', 2))
        if 'personal_number' not in line_2:
            raise Exception(exception_string.format('personal_number', 2))

        issuing_country = line_1['issuing_country']
        last_name = line_1['last_name']
        given_name = line_1['given_name']
        passport_number = line_2['passport_number']
        passport_number_check_digit = self.generate_check_digit(passport_number)
        country_code = line_2['country_code']
        birth_date = line_2['birth_date']
        birth_date_check_digit = self.generate_check_digit(birth_date)
        sex = line_2['sex']
        expiration_date = line_2['expiration_date']
        expiration_date_check_digit = self.generate_check_digit(expiration_date)
        personal_number = line_2['personal_number'] if 'personal_number' in line_2 else None
        personal_number_check_digit = self.generate_check_digit(personal_number) if personal_number is not None else None
        
        encoded_line_1 = "P<" + issuing_country.upper() + last_name.upper() + "<<" + given_name.upper().replace(" ", "<")
        encoded_line_1 += '<' * (MAX_MRZ_LENGTH - len(encoded_line_1))
        
        encoded_line_2 = passport_number.upper() + str(passport_number_check_digit) \
            + country_code.upper() + birth_date + str(birth_date_check_digit) + sex.upper() + expiration_date + str(expiration_date_check_digit)
        if personal_number is not None:
            encoded_line_2 += personal_number.upper()
            encoded_line_2 += '<' * ((MAX_MRZ_LENGTH - 1) - len(encoded_line_2))
            encoded_line_2 += str(personal_number_check_digit)
        else:
            encoded_line_2 += '<' * (MAX_MRZ_LENGTH - len(encoded_line_2))

        self.encoded_mrz = encoded_line_1 + ';' + encoded_line_2
        return self.encoded_mrz

    """
    helper function to determine validity of provided check digit for a given field
    @param field_identifier: provides useful information about which field the value is coming from
    """
    def is_check_digit_valid(self, field: str, check_digit: int, field_identifier: str) -> bool:
        valid = self.generate_check_digit(field) == check_digit
        if not valid:
            print("The check digit ({}) for the field {}, with value {} does not match.\
                 The MRZ for this Travel Document is invalid."\
                .format(check_digit, field_identifier, field))
        return valid

    """
    helper function to generate check digit for a given field
    """
    def generate_check_digit(self, field: str) -> int:
        total = 0
        for index, val in enumerate(field):
            if val not in self.cmap:
                raise Exception('The provided character {} does not conform to the ICAO standard alpha-numeric character values. \
                    The MRZ for this Travel Document is invalid.'.format(val))
            value = self.cmap[val]
            weight = 0
            if index % 3 == 0: # weight 7
                weight = 7
            elif index % 3 == 1: # weight 3
                weight = 3
            elif index % 3 == 2: # weight 1
                weight = 1
            total += (value * weight)
        return total % 10
