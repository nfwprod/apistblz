import pytest
import datetime
from apistblz import wait_and_retry
from apistblz import exceptions

class UnexpextedException(Exception):
    pass


class TestWaitAndRetry(object):
    @wait_and_retry.wait_and_retry()
    def func_default(self):
        return datetime.datetime.now()

    @wait_and_retry.wait_and_retry()
    def func_fail_once_and_ok(self, ctime):
        dtime = (datetime.datetime.now() - ctime).total_seconds()
        if dtime < 1:
            raise wait_and_retry.Retry(wait=2)
        return True

    @wait_and_retry.wait_and_retry()
    def func_alwaysfail(self):
        raise wait_and_retry.Retry(wait=0)

    @wait_and_retry.wait_and_retry()
    def func_unexpected_exception(self):
        raise UnexpextedException()

    # Test
    def test_default(self):
        result01 = self.func_default()
        assert True

    def test_retry(self):
        ctime = datetime.datetime.now()
        result01 = self.func_fail_once_and_ok(ctime)
        assert True

    def test_retry_over(self):
        try:
            result01 = self.func_alwaysfail()
        except exceptions.WaitAndRetryMaxRetryOver as e:
            assert True
        except Exception as e:
            assert False
        else:
            assert False

    def test_unexpected_error(self):
        try:
            self.func_unexpected_exception()
        except UnexpextedException as e:
            assert True
        except Exception as e:
            assert False
        else:
            assert False


