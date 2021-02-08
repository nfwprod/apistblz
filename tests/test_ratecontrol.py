import pytest
import datetime
from apistblz import ratecontrol
from apistblz import exceptions


class TestRateControl(object):
    @ratecontrol.ratecontrol(threshold=0.5)
    def func_notag(self):
        return datetime.datetime.now()

    @ratecontrol.ratecontrol(threshold=0.5, tag='tag01')
    def func_tag01(self):
        return datetime.datetime.now()

    @ratecontrol.ratecontrol(threshold=0.5, tag='tag02')
    def func_tag02(self):
        return datetime.datetime.now()

    @ratecontrol.ratecontrol(threshold=0.5, tag='tag03')
    def func_tag03(self):
        return datetime.datetime.now()

    def test_default(self):
        result01 = self.func_notag()
        result02 = self.func_notag()
        assert (result02 - result01).seconds == 2

    def test_tag01(self):
        result01 = self.func_tag01()
        result02 = self.func_tag02() # Other tag, no wait.
        assert (result02 - result01).seconds < 2

    def test_clear(self):
        result01 = self.func_tag03()
        ratecontrol.clear('tag03')
        result02 = self.func_tag03() # tag cleared, no wait.
        assert (result02 - result01).seconds < 2
