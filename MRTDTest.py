import unittest
import json
from MRTD import MachineReadableTravelDocument
from unittest.mock import patch

class TestMachineReadableTravelDocument(unittest.TestCase):
    """
    setUp method for the test class; defines behaviors to be specified before running tests cases
    """
    def setUp(self) -> None:
        self.mrtd = MachineReadableTravelDocument()
        return super().setUp()
    
    """
    tearDown method to stop patcher and kill all active objects after executing test cases
    """
    def tearDown(self) -> None:
        return super().tearDown()
    
    """
    method to test whether data coming from hardware scanner is returning the correct encoded output string
    """
    @patch('MRTD.MachineReadableTravelDocument.scan_mrz', return_value = "P<CIVLYNN<<NEVEAH<BRAM<<<<<<<<<<<<<<<<<<<<<<;W620126G54CIV5910106F9707302AJ010215I<<<<<<6")
    def test_scan_mrz_returns_encoded_mrz_from_document(self, mock_scan_mrz):
        # assemble
        # act
        result = mock_scan_mrz()
        # assert
        self.assertEqual(type(result), str)
        self.assertEqual(result, "P<CIVLYNN<<NEVEAH<BRAM<<<<<<<<<<<<<<<<<<<<<<;W620126G54CIV5910106F9707302AJ010215I<<<<<<6")
        
    """
    test to see whether the correct fields are being returned from DB transaction
    """
    @patch('MRTD.MachineReadableTravelDocument.get_fields_for_user', return_value = {
            "line1": {
                "issuing_country": "CIV",
                "last_name": "LYNN",
                "given_name": "NEVEAH BRAM"
            },
            "line2": {
                "passport_number": "W620126G5",
                "country_code": "CIV",
                "birth_date": "591010",
                "sex": "F",
                "expiration_date": "970730",
                "personal_number": "AJ010215I"
            }
        })
    def test_get_fields_for_user_returns_dict_from_db(self, mock_get_fields):
        # assemble
        last_name = 'LYNN'
        given_name = 'NEVEAH BRAM'
        personal_number = 'AJ010215I'
        # act
        result = mock_get_fields(last_name, given_name, personal_number)
        # assert
        self.assertEqual(result, {
            "line1": {
                "issuing_country": "CIV",
                "last_name": "LYNN",
                "given_name": "NEVEAH BRAM"
            },
            "line2": {
                "passport_number": "W620126G5",
                "country_code": "CIV",
                "birth_date": "591010",
                "sex": "F",
                "expiration_date": "970730",
                "personal_number": "AJ010215I"
            }
        })
        self.assertEqual(type(result), dict)


    """
    Check whether MRTD contains instance of CharacterMap
    """
    def test_mrtd_contains_character_map_dict(self):
        msg = "MRTD does not contain an instance of CharacterMap dictionary"
        self.assertIsInstance(self.mrtd.cmap, dict, msg)
    
    """
    test generate_check_digit returns correct check digit when field provided
    """
    def test_generate_check_digit_returns_correct_digit_when_passportNo_provided(self):
        # assemble
        field = 'L898902C3'
        check_digit = 6
        # act
        generated = self.mrtd.generate_check_digit(field)
        # assert
        self.assertEqual(generated, check_digit, 'Check digit matched expected value!')
    
    """
    test exception is raised when illegal character provided
    """
    def test_generate_check_digit_raises_exception_when_illegal_character_in_field(self):
        # assemble
        field = '420;69.1'
        check_digit = None
        with self.assertRaises(Exception) as ex:
            # act
            generated = self.mrtd.generate_check_digit(field)
            # assert
            self.assertEqual(str(ex.exception), generated, 'Exception raised when illegal character provided.')
    
    """
    test is_check_digit_valid() returns true when valid check digit provided for field
    """
    def test_is_check_digit_valid_returns_true_when_correct_input_provided(self):
        # assemble
        field = 'L898902C3'
        check_digit = 6
        # act
        is_valid = self.mrtd.is_check_digit_valid(field=field, check_digit=check_digit, field_identifier="TestIdentifier")
        # assert
        self.assertTrue(is_valid, 'Check digit for test value is valid')

    """
    test is_check_digit_valid() returns false when incorrect value provided for given DOB field
    """
    def test_is_check_digit_valid_returns_false_when_incorrect_input_provided(self):
        # assemble
        field = '740812'
        check_digit = 3 # should be 2
        # act
        is_valid = self.mrtd.is_check_digit_valid(field=field, check_digit=check_digit, field_identifier="TestDOB")
        # assert
        self.assertFalse(is_valid, 'Check digit for test DOB is not valid')

    """
    test to check whether encode_mrz_input is returning the correct MRZ string for the scanner
    """
    def test_encode_mrz_input_returns_correct_string_when_input_provided(self):
        # assemble
        encoded_output = "P<CIVLYNN<<NEVEAH<BRAM<<<<<<<<<<<<<<<<<<<<<<;W620126G54CIV5910106F9707302AJ010215I<<<<<<6"
        with open('resources/decoded_3.json', 'r') as file:
            d = json.load(file)
        decoded_input = d.get('records_decoded')[0]
        # act
        self.mrtd.encode_mrz_input(decoded_input)
        # assert
        self.assertEqual(self.mrtd.encoded_mrz, encoded_output, 'Encoded MRZ generated was correct.')
    
    """
    test to see whether KeyError is raised when encode_mrz_input is called with invalid formatted JSON
    """
    def test_encode_mrz_input_raises_keyerror_when_incorrect_input_format(self):
        # assemble
        encoded_output = ""
        with open('resources/records_decoded_all.json', 'r') as file:
            d = json.load(file)
        decoded_input = d.get('records_decoded')[0]
        # act
        with self.assertRaises(KeyError) as ke:
            # assert
            self.assertEqual(str(ke), self.mrtd.encode_mrz_input(decoded_input), 'KeyError because correct format not found for input')

    """
    test to see whether exception is thrown when issuing country field is missing
    """
    def test_encode_mrz_input_raises_exception_issuing_country_missing(self):
        with open('resources/records_decoded.json','r') as file:
            d = json.load(file)
        decoded_inp = d.get('records_decoded')[0]
        with self.assertRaises(Exception) as err:
            self.assertEqual(str(err), self.mrtd.encode_mrz_input(decoded_inp))

    """
    test to see whether exception is thrown when last name field is missing
    """
    def test_encode_mrz_input_raises_exception_last_name_missing(self):
        with open('resources/decoded_incorrect.json','r') as file:
            d = json.load(file)
        decoded_inp = d.get('records_decoded')[0]
        with self.assertRaises(Exception) as err:
            self.assertEqual(str(err), self.mrtd.encode_mrz_input(decoded_inp))

    """
    test to see whether exception is thrown when given name is missing
    """
    def test_encode_mrz_input_raises_exception_given_name_missing(self):
        with open('resources/records_decoded_gn.json','r') as file:
            d = json.load(file)
        decoded_inp = d.get('records_decoded')[0]
        with self.assertRaises(Exception) as err:
            self.assertEqual(str(err), self.mrtd.encode_mrz_input(decoded_inp))

    """
    test to see whether exception is thrown when passport number field is missing
    """
    def test_encode_mrz_input_raises_exception_passport_number_missing(self):
        with open('resources/records_decoded_passport.json','r') as file:
            d = json.load(file)
        decoded_inp = d.get('records_decoded')[0]
        with self.assertRaises(Exception) as err:
            self.assertEqual(str(err), self.mrtd.encode_mrz_input(decoded_inp))

    """
    test to see whether exception is thrown when country code field is missing
    """
    def test_encode_mrz_input_raises_exception_country_code_missing(self):
        with open('resources/records_decoded_countryCode.json','r') as file:
            d = json.load(file)
        decoded_inp = d.get('records_decoded')[0]
        with self.assertRaises(Exception) as err:
            self.assertEqual(str(err), self.mrtd.encode_mrz_input(decoded_inp))

    """
    test to see whether exception is thrown when birth date field is missing
    """
    def test_encode_mrz_input_raises_exception_birth_date_missing(self):
        with open('resources/records_decoded_birthdate.json','r') as file:
            d = json.load(file)
        decoded_inp = d.get('records_decoded')[0]
        with self.assertRaises(Exception) as err:
            self.assertEqual(str(err), self.mrtd.encode_mrz_input(decoded_inp))

    """
    test to see whether exception is thrown when sex field is missing
    """
    def test_encode_mrz_input_raises_exception_sex_missing(self):
        with open('resources/records_decoded_sexmissing.json','r') as file:
            d = json.load(file)
        decoded_inp = d.get('records_decoded')[0]
        with self.assertRaises(Exception) as err:
            self.assertEqual(str(err), self.mrtd.encode_mrz_input(decoded_inp))

    """
    test to see whether exception is thrown when expiration date field is missing
    """
    def test_encode_mrz_input_raises_exception_expiration_date_missing(self):
        with open('resources/records_decoded_expirationdate.json','r') as file:
            d = json.load(file)
        decoded_inp = d.get('records_decoded')[0]
        with self.assertRaises(Exception) as err:
            self.assertEqual(str(err), self.mrtd.encode_mrz_input(decoded_inp))

    """
    test to see whether exception is thrown when personal number field is missing
    """

    def test_encode_mrz_input_raises_exception_personal_number_missing(self):
        with open('resources/records_decoded_expirationdate.json', 'r') as file:
            d = json.load(file)
        decoded_inp = d.get('records_decoded')[0]
        with self.assertRaises(Exception) as err:
            self.assertEqual(str(err), self.mrtd.encode_mrz_input(decoded_inp))

    """
    test to check the validity of the dict returned when encoded string provided to MRTD system
    """
    def test_decode_mrz_input_returns_correct_dict_when_input_str_provided(self):
        # assemble
        encoded_mrz = "P<CIVLYNN<<NEVEAH<BRAM<<<<<<<<<<<<<<<<<<<<<<;W620126G54CIV5910106F9707302AJ010215I<<<<<<6"
        decoded_mrz = {
            'document_type': 'P', 
            'issuing_country': 'CIV', 
            'last_name': 'LYNN', 
            'given_name': 'NEVEAH BRAM', 
            'passport_number': 'W620126G5', 
            'country_code': 'CIV', 
            'birth_date': '591010', 
            'sex': 'F', 
            'expiration_date': '970730', 
            'personal_number': 'AJ010215I'
        }
        # act
        self.mrtd.decode_mrz_input(encoded_mrz)
        # assert
        self.assertEqual(self.mrtd.decoded_mrz, decoded_mrz, 'decoded mrz for provided encoded string is correct')

if __name__ == '__main__':
    print('Running unit tests for MachineReadableTravelDocument')
    unittest.main(exit=False, verbosity=2)
