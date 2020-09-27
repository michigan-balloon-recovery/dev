from unittest import TestCase
from balloon import APRS

class BalloonTest(TestCase):
    def test_aprs_single_callsign(self):
        callsign = 'hello'
        aprs_apikey = 'gibberish'
        result = APRS(callsign, aprs_apikey)
        assert result == 'hello'
