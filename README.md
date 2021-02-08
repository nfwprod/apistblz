# apistblz
Utility tools for stable api access.

Features
--------

- Cache returns for functions with API accesses(DownloadOnce).
- Handle API access and do retry if failed(WaitAndRetry).
- Control access rate(RateControl).

Download Once
-------------
Cache returns for functions with API accesses.
When @downloadonce decorated function is called at the first time, returns are chacned in memory.
Second time, don't run the function but read returns from memory.
Returns can be cashed on disk, too.

Settings
--------
- Global Settings
  - dumpdir: Directory path for on disk cached files. Default: "./.dlo_dump".
  - force_on_disk: Overide on_disk settings for each functions. Default: False.
  - reportmode: Log report mode. In the current version, stdout only. Default: 'stdout'.
- Decorator Arguments
  - on_disk: Save and load cached returns on disk. Default: False.
  - is_method: Name cache data on disk with Args strings. For method in class, need to ignore first Args(self or cls) for cache data name. Set True for class instance method and set False for non-class instance method. Default: False(Non-class instalce method).
- Additional Args for function
  - force_run: Ignore cached data and run the function again. Cached data will be overiden by new Returns. Default: False.
  - not_save_on_disk: Load cached data or run but don't cashe returns in memory nor on disk. Default: False.

Usage
-----
- Functions with not stable returns, different returns for same args every time.
  - Don't use download once decorator.
- Functions with not stable returns, but stable at least during the script is running.
  - Default settings.
- Functions with stable returns. Always return same returns for same args.
  - on_disk: True.
- Functions with unknown returns, stable or not will be turned out after execution.
  - on_disk: True, not_save_on_disk: True
  - If returns are stable, run function again without "not_save_on_disk: True".
- Returns are not stable, but no need to update everytime for staging.
  - force_on_disk: True
- Functions with stable returns, but need to update for some reasons.
  - force_run: True
  - Even with force_run, functions with "not_save_on_disk: True" never save returns.

On Disk Priority: not_save_on_disk > force_on_disk > on_disk.

Usage(Advanced)
---------------
Functions has special features with "dlo_cmd" argument.

- dlo_cmd='is_cached_in_memory': Check returns is cashed in memory or not(bool).
- dlo_cmd='is_cached_on_disk': Check returns is cashed on disk or not(bool).
- dlo_cmd='uncache_in_memory': Delect returns in memory(bool).
- dlo_cmd='uncache_on_disk': Delect returns on disk(bool).
- dlo_cmd='cache_on_disk': Cache data in memory to disk(bool).

Example
--------

```python
from apitools import downloadonce

# Global Settings
downloadonce.dumpdir = './.dlo_dump'

# Cached in memory
@downloadonce.downloadonce('func01')
def func_in_memory(arg01):
    return True

# Cached in memory and on disk
@downloadonce.downloadonce('func01', on_disk=True)
def func_on_disk(arg01):
    return True

# Basically cached in memory and on disk, but not for once.
func_on_disk(arg01, not_save_on_disk=True)

# Check cache is in memory or not, result is contained in 'result'.
result = func_on_disk(arg01, dlo_cmd='is_cached_in_memory')
```

Rate Control
------------
Wait if decorated function runs quicker than threthold rate.

Settings
--------
- Global Settings
  - reportmode: Log report mode. In the current version, stdout only. Default: 'stdout'.
- Decorator Arguments
  - threshold: Max rate, function run times per second. Default: 1.0
  - tag: Tag for function, rates are counted per tags.

Example
-------

```python
from apitools import ratecontrol

# Restrict 1 times per sec
@ratecontrol.ratecontrol()
def func_01():
    return True

func_01()
func_01() # Wait for 1 sec and run.

# Restrict 1 times per 2sec
@ratecontrol.ratecontrol(threthold=0.5)
def func_02():
    return True

func_02()
func_02() # Wait for 2 sec and run.

# Restrict with tags.
#   func_03 and func_04 are rate controled simultaneously.
@ratecontrol.ratecontrol(threthold=0.5, tag="3 and 4")
def func_03():
    return True

@ratecontrol.ratecontrol(threthold=0.5, tag="3 and 4")
def func_04():
    return True

func_03()
func_04() # Wait for 2 sec and run.

# Global Function
func_03()
ratecontrol.clear("3 and 4") # Clear count history.
func_04() # Run right after func_03.
```

Wait and Retry
--------------
Retry decorated function if failed.
To retry, raise Retry in decorated function.

Settings
--------
- Global Settings
  - reportmode: Log report mode. In the current version, stdout only. Default: 'stdout'.
- Decoretor Arguments
  - retry: Max retry. Default: 5(times)
- Raise Argument
  - wait: Wait seconds before retry. Default 5(seconds).

Example
-------

```python
from apitools import wait_and_retry

# Wait 5 seconds if failed, retry 5 times.
# After max retry, raise WaitAndRetryMaxRetryOver exception.
@wait_and_retry.wait_and_retry()
def func_01():
    # Process
    if <Failed and want to retry>:
        raise wait_and_retry.Retry()
    else:
        return <Expected returns>

# Wait 10 seconds if failed, retry 2 times.
# After max retry, raise WaitAndRetryMaxRetryOver exception.
@wait_and_retry.wait_and_retry(retry=2)
def func_02():
    # Process
    if <Failed and want to retry>:
        raise wait_and_retry.Retry(wait=10)
    else:
        return <Expected returns>
```
