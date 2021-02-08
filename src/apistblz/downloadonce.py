import pickle
import os
import copy
import shutil
import datetime
from .exceptions import *


# External Variables
dumpdir = '.dlo_dump'
force_on_disk = False
reportmode = None

# Internal Variables
dlo_memory = {}
prefix_list = []


# Internal Functions
def _check_disk(keystring):
    return os.path.isfile(_dumptarget(keystring))


def _dumptarget(keystring):
    if not os.path.isdir(dumpdir):
        os.makedirs(dumpdir)
    return os.path.join(dumpdir, "{}".format(keystring))


def _dump_to_disk(keystring, data):
    with open(_dumptarget(keystring), 'wb') as f:
        pickle.dump(data, f)


def _load_from_disk(keystring):
    with open(_dumptarget(keystring), 'rb') as f:
        data = pickle.load(f)
    return data


def _report(line):
    if reportmode == 'stdout':
        print(line)


# External Functions
def clear():
    if os.path.isdir(dumpdir):
        shutil.rmtree(dumpdir)


def cache(keystring):
    if kestring in dlo_memory.keys():
        _dump_to_disk(keystring, dlo_memory[keystring])


def uncache(keystring):
    global dlo_memory

    if kestring in dlo_memory.keys():
        del dlo_memory[keystring]
    if os.path.isfile(_dumptarget(keystring)):
        os.remove(_dumptarget(keystring))


def dump():
    ctime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    for k, v in dlo_memory.items():
        _dump_to_disk(k, v)


def downloadonce(prefix, on_disk=False, is_method=False):
    """Decorator to download data through API or from cache.

    Args:
      prefix(str): prefix for on disk cache data.
      on_disk: Save and load cached returns on disk. Default: False.
      is_method: For cache on disk, name cache data with Args strings.
          For method in class, need to ignore first Args(self or cls) for
          cache data name. Set True for class instance method and set
          False for non-class instance method.
          Default: False(Non-class instance method).

    Note:
      Add following additional kwargs for original function.
        force_run(bool): Ignore cached data and run the function again.
            Cached data will be overridden by new Returns. Default: False
        not_save_on_disk(bool): Load cached data or run and save cache
            in memory, but never save on disk. Default: False
        dlo_cmd(str): Special command.
            is_cached_in_memory:
              Check returns is cashed in memory or not(bool).
            is_cached_on_disk:
              Check returns is cashed on disk or not(bool).
            uncache_in_memory: Delete returns in memory(bool).
            uncache_on_disk: Delete returns on disk(bool).
            cache_on_disk: Cache data in memory to disk(bool).
    """
    special_args = ['force_run', 'not_save_on_disk', 'dlo_cmd']

    def dlo_deco(func):
        def _generate_keystring(is_method, prefix, args, kwargs):
            if is_method:
                keystring = '_'.join(
                    [prefix] +
                    [str(x) for x in args[1:]] +
                    ['{}_{}'.format(x, y) for x, y in sorted(
                        kwargs.items(), key=lambda x:x[0])]
                )
            else:
                keystring = '_'.join(
                    [prefix] +
                    [str(x) for x in args] +
                    ['{}_{}'.format(x, y) for x, y in sorted(
                        kwargs.items(), key=lambda x:x[0])]
                        )
            return keystring

        def _get(keystring, force_run, not_save_on_disk, *args, **kwargs):
            global dlo_memory

            # Get output
            output = None
            if force_run:
                _report("[downloadonce] Download {}".format(keystring))
                output = func(*args, **kwargs)
            elif keystring in dlo_memory.keys():
                _report(
                    "[downloadonce] Return from memory {}".format(keystring))
                output = dlo_memory[keystring]
            elif (on_disk or force_on_disk) and _check_disk(keystring):
                _report("[downloadonce] Return from disk {}".format(keystring))
                output = _load_from_disk(keystring)
            else:
                _report("[downloadonce] Download {}".format(keystring))
                output = func(*args, **kwargs)

            # Save output as cache
            dlo_memory[keystring] = output
            if (force_on_disk or on_disk) and not not_save_on_disk:
                _dump_to_disk(keystring, output)

            return copy.deepcopy(output)

        def decorated_func(*args, **kwargs):
            # Check special args.
            for argname in ['force_run', 'not_save_on_disk', 'dlo_cmd']:
                if argname in func.__code__.co_varnames:
                    raise DownloadOnceDuplexArgs(argname)
            force_run = kwargs.pop('force_run', None)
            not_save_on_disk = kwargs.pop('not_save_on_disk', None)
            dlo_cmd = kwargs.pop('dlo_cmd', None)
            keystring = _generate_keystring(is_method, prefix, args, kwargs)

            # Switch with special arguments.
            if not dlo_cmd:
                return _get(keystring, force_run, not_save_on_disk,
                            *args, **kwargs)
            if dlo_cmd == 'is_cached_in_memory':
                return keystring in dlo_memory.keys()
            if dlo_cmd == 'is_cached_on_disk':
                return _check_disk(keystring)
            if dlo_cmd == 'uncache_in_memory':
                if keystring in dlo_memory.keys():
                    del dlo_memory[keystring]
                    return True
                return False
            if dlo_cmd == 'uncache_on_disk':
                if _check_disk(keystring):
                    os.remove(_dumptarget(keystring))
                    return True
                return False
            if dlo_cmd == 'cache_on_disk':
                if keystring in dlo_memory.keys():
                    _dump_to_disk(keystring, dlo_memory[keystring])
                    return True
                return False
            raise DownloadOnceInvalidCmd(argname)

        return decorated_func

    global prefix_list
    if prefix in prefix_list:
        raise DownloadOnceDuplexPrefix(prefix)
    prefix_list.append(prefix)

    return dlo_deco
