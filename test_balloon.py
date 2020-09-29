from unittest import TestCase
from unittest import mock
from balloon import *
from pprint import pprint
import subprocess


class BalloonTest(TestCase):
    def test_aprs_single_callsign(self):
        """
        Tests that a single callsign is processed correctly
        """
        with mock.patch("requests.get") as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.text = '{"command":"get","result":"ok","what":"loc","found":1,"entries":[{"class":"a","name":"S2351703","type":"o","time":"1601173260","lasttime":"1601173260","lat":"58.12467","lng":"11.25903","altitude":671.4744,"course":265,"speed":46.3,"symbol":"\\/O","srccall":"SM6OWJ","dstcall":"APRARX","comment":"Clb=-3.4m\\/s t=-273.0C 405.300 MHz Type=RS41 Radiosonde auto_rx v1.3.2","path":"TCPIP*,qAC,SQ6KXY-1"}]}'
            response = APRS(callsign_entry="hello", aprs_apikey="gibberish")
            expected_response = {
                "altitude": 671.4744,
                "class": "a",
                "comment": "Clb=-3.4m/s t=-273.0C 405.300 MHz Type=RS41 Radiosonde auto_rx "
                "v1.3.2",
                "course": 265,
                "dstcall": "APRARX",
                "lasttime": "1601173260",
                "lat": "58.12467",
                "lng": "11.25903",
                "name": "S2351703",
                "path": "TCPIP*,qAC,SQ6KXY-1",
                "speed": 46.3,
                "srccall": "SM6OWJ",
                "symbol": "/O",
                "time": "1601173260",
                "type": "o",
            }
            assert response == expected_response

    def test_aprs_multiple_callsigns(self):
        """
        Tests that multiple callsigns are processed correctly
        """
        with mock.patch("requests.get") as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.text = '{"command":"get","result":"ok","what":"loc","found":2,"entries":[{"class":"a","name":"S2351703","type":"o","time":"1601173260","lasttime":"1601173260","lat":"58.12467","lng":"11.25903","altitude":671.4744,"course":265,"speed":46.3,"symbol":"\\/O","srccall":"SM6OWJ","dstcall":"APRARX","comment":"Clb=-3.4m\\/s t=-273.0C 405.300 MHz Type=RS41 Radiosonde auto_rx v1.3.2","path":"TCPIP*,qAC,SQ6KXY-1"},{"class":"a","name":"S2410312","type":"o","time":"1599078280","lasttime":"1599078280","lat":"57.57366","lng":"11.71236","altitude":"70.41","course":"263","speed":"28","symbol":"\\/O","srccall":"SM6OWJ","dstcall":"APRARX","comment":"Clb=-2.7m\\/s t=16.6C 405.301 MHz Type=RS41-SG Radiosonde auto_rx v1.3.2","path":"SONDEGATE,TCPIP,qAR,SM6OWJ"}]}'
            response = APRS(callsign_entry="hello", aprs_apikey="gibberish")
            expected_response = {
                "altitude": "70.41",
                "class": "a",
                "comment": "Clb=-2.7m/s t=16.6C 405.301 MHz Type=RS41-SG Radiosonde auto_rx "
                "v1.3.2",
                "course": "263",
                "dstcall": "APRARX",
                "lasttime": "1599078280",
                "lat": "57.57366",
                "lng": "11.71236",
                "name": "S2410312",
                "path": "SONDEGATE,TCPIP,qAR,SM6OWJ",
                "speed": "28",
                "srccall": "SM6OWJ",
                "symbol": "/O",
                "time": "1599078280",
                "type": "o",
            }
            assert response == expected_response

    def test_aprs_failure_apikey(self):
        """
        Tests that function behaves correctly with invalid API Key
        """
        response = APRS(callsign_entry="hello", aprs_apikey="gibberish")
        assert response == None

    @mock.patch("requests.post")
    def test_send_slack(self, mock_post):
        """
        Tests successful curl to send a slack dm and channel message
        """
        payload = {
            "username": "Predictions Bot",
            "text": "test message",
            "icon_emoji": ":ghost:",
        }
        return_val = send_slack("test message", "big_long_slack_url")
        mock_post.assert_called_with(url="big_long_slack_url", data=json.dumps(payload))

    def test_send_slack_failure(self):
        """
        Tests error handling in send_slack function
        """
        with mock.patch("requests.post") as mock_request:
            mock_request.return_value.status_code = 404
            mock_request.return_value.text = "error"
            output = send_slack("some message", "hi")
        self.assertFalse(output)
        output = send_slack("some message", "hi")
        self.assertFalse(output)
