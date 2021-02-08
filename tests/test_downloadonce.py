import pytest
import os
import datetime
from apistblz import downloadonce
from apistblz import exceptions

dumpdir = "/tmp/dlo_dump"
downloadonce.dumpdir =  dumpdir


class TestDownloadOnce(object):
    @downloadonce.downloadonce('default', is_method=True)
    def func_default(self, arg01):
        return str(datetime.datetime.now())

    @downloadonce.downloadonce('multiargs01', is_method=True)
    def func_multiargs01(self, arg01, arg02):
        return str(datetime.datetime.now())

    @downloadonce.downloadonce('multiargs02', is_method=True)
    def func_multiargs02(self, arg01, arg02=True):
        return str(datetime.datetime.now())

    @downloadonce.downloadonce('noarg', is_method=True)
    def func_noarg(self):
        return str(datetime.datetime.now())

    @downloadonce.downloadonce('on_disk', on_disk=True, is_method=True)
    def func_on_disk(self, arg01):
        return str(datetime.datetime.now())

    @pytest.fixture(scope='class', autouse=True)
    def scope_function(self):
        downloadonce.clear()
        yield
        downloadonce.clear()

    # Tests
    def test_default(self):
        result01 = self.func_default(1)
        assert not os.path.isfile(os.path.join(dumpdir, "default_1"))
        result02 = self.func_default(1)
        assert result01 == result02

    def test_multiargs01(self):
        result01 = self.func_multiargs01(1, 2)
        result02 = self.func_multiargs01(1, 2)
        assert result01 == result02

    def test_multiargs02(self):
        result01 = self.func_multiargs02(1, arg02=False)
        result02 = self.func_multiargs02(1, arg02=False) 
        assert result01 == result02

    def test_noarg(self):
        result01 = self.func_noarg()
        result02 = self.func_noarg()
        assert result01 == result02

    def test_on_disk(self):
        assert not os.path.isfile(os.path.join(dumpdir, "on_disk_1"))
        result01 = self.func_on_disk(1)
        assert os.path.isfile(os.path.join(dumpdir, "on_disk_1"))
        result02 = self.func_on_disk(1)
        assert result01 == result02

    # Test for Exceptions
    def test_duplex_kwargs(self):
        try:
            @downloadonce.downloadonce('duplex_kwargs')
            def func_duplex_kwargs(not_save_on_disk=True):
                return True
            func_duplex_kwargs()
        except exceptions.DownloadOnceDuplexArgs as e:
            assert True
        except Exception as e:
            raise e

    def test_duplex_prefix(self):
        try:
            @downloadonce.downloadonce('prefix01')
            def func_prefix_01():
                return True
            @downloadonce.downloadonce('prefix01')
            def func_prefix_02():
                return True
            func_prefix_01()
            func_prefix_02()
        except exceptions.DownloadOnceDuplexPrefix as e:
            assert True
        except Exception as e:
            raise e

    # Test for Special Args
    def test_is_cached_in_memory(self):
        result01 = self.func_default("in_memory")
        assert self.func_default("in_memory", dlo_cmd='is_cached_in_memory')
        assert not self.func_default("in_memory", dlo_cmd='is_cached_on_disk')

    def test_is_cached_on_disk(self):
        result01 = self.func_on_disk("on_disk")
        assert self.func_on_disk("on_disk", dlo_cmd='is_cached_in_memory')
        assert self.func_on_disk("on_disk", dlo_cmd='is_cached_on_disk')

    def test_uncache_in_memory(self):
        self.func_default("uncache_in_memory")
        assert self.func_default("uncache_in_memory", dlo_cmd="is_cached_in_memory")
        assert self.func_default("uncache_in_memory", dlo_cmd="uncache_in_memory")
        assert not self.func_default("uncache_in_memory", dlo_cmd="is_cached_in_memory")

    def test_uncache_on_disk(self):
        self.func_on_disk("uncache_on_disk")
        assert self.func_on_disk("uncache_on_disk", dlo_cmd="is_cached_in_memory")
        assert self.func_on_disk("uncache_on_disk", dlo_cmd="is_cached_on_disk")
        assert self.func_on_disk("uncache_on_disk", dlo_cmd="uncache_on_disk")
        assert self.func_on_disk("uncache_on_disk", dlo_cmd="is_cached_in_memory")
        assert not self.func_on_disk("uncache_on_disk", dlo_cmd="is_cached_on_disk")

    # Test Advanced Settings
    def test_on_disk_no_save(self):
        result01 = self.func_on_disk("on_disk_no_save", not_save_on_disk=True)
        assert self.func_on_disk("on_disk_no_save", dlo_cmd='is_cached_in_memory')
        assert not self.func_on_disk("on_disk_no_save", dlo_cmd='is_cached_on_disk')

    def test_force_run(self):
        result01 = self.func_default('force_run')
        result02 = self.func_default('force_run', force_run=True)
        assert not result01 == result02
