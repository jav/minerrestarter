import unittest
from mock import patch, Mock

import minerrestarter

class TestStringMethods(unittest.TestCase):

    @patch('mod_a.urllib2.urlopen')
    def testGetHashrate(mock_urlopen):
        a = Mock()
        a.read.side_effect = hashrateResponse
        mock_urlopen.return_value = a
        hashrate = minerrestarter.get_hashrate(1234, "10s")
        print hashrate
        assert hashrate == 1957.6


if __name__ == '__main__':
    unittest.main()




#10s    60s     15m
#1957.6	1981.9	1971.8
hashrateResponse="<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width' /><link rel='stylesheet' href='style.css' /><title>Hashrate Report</title></head><body><div class='all'><div class='header'><span style='color: rgb(255, 160, 0)'>XMR</span>-Stak-AMD</div><div class='flex-container'><div class='links flex-item'><a href='/h'><div><span class='letter'>H</span>ashrate</div></a></div><div class='links flex-item'><a href='/r'><div><span class='letter'>R</span>esults</div></a></div><div class='links flex-item'><a href='/c'><div><span class='letter'>C</span>onnection</div></a></div></div><h4>Hashrate Report</h4><div class=data><table><tr><th>Thread ID</th><th>10s</th><th>60s</th><th>15m</th><th rowspan='5'>H/s</td></tr><tr><th>0</th><td> 1025.4</td><td> 1036.2</td><td> 1035.7</td></tr><tr><th>1</th><td> 932.2</td><td> 945.7</td><td> 936.1</td></tr><tr><th>Totals:</th><td> 1957.6</td><td> 1981.9</td><td> 1971.8</td></tr><tr><th>Highest:</th><td> 2028.0</td><td colspan='2'></td></tr></table></div></div></body></html>"
