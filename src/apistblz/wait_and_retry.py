import time
from apistblz import exceptions

# External Variables
reportmode = None


class Retry(Exception):
    """Exception to call retry from wrapped func.

    Args:
      wait(int): Wait seconds, default=5.

    """
    def __init__(self, wait=5):
        super().__init__()
        self.wait = wait


# Internal Functions
def _report(line):
    if reportmode == 'stdout':
        print(line)


# External Functions
def wait_and_retry(retry=5):
    """Decorator to do retry if needed.

    Args:
      retry(int): Max retry times.
                  If try to do retry more, raise Exception and stop.

    Note:
      To retry, raise "Retry" in wrapped function.
      Wait seconds is defined by Retry's argument.

    """

    def deco(func):
        def run(*args, **kwargs):
            count = 0
            result = None
            while True:
                try:
                    result = func(*args, **kwargs)
                except Retry as r:
                    if count >= retry:
                        raise exceptions.WaitAndRetryMaxRetryOver()
                    wait = r.wait
                    _report(('[wait_and_retry] Retry, '
                             'wait for {} seconds and retry.').format(wait))
                    count += 1
                    time.sleep(wait)
                except Exception as e:
                    raise e
                else:
                    break
            return result
        return run
    return deco
