import time
import datetime

# External Variables
reportmode = None

# Internal Variables
ratehistory = {}


# Internal Functions
def _report(line):
    if reportmode == 'stdout':
        print(line)


# External Functions
def ratecontrol(threshold=1.0, tag=""):
    """Wait if access rate is high.

    Args:
      threshold(float): Max rate, function run times per second.
      tag(string): Tag for function, rates are counted per tags.

    Note:
      Calcurate current rate as follows.
        Count lines from ratehistory in last <duration> seconds.
        Divide the count by <duration>.
      If rate >= threshold, wait for <duration> seconds.

    """
    def deco(func):
        def run(*args, **kwargs):
            global ratehistory

            # Calcurate latest rate
            timestep = 1.0 / threshold * 1000  # msec
            current = datetime.datetime.now()
            lasttime = ratehistory.get(
                tag, current - datetime.timedelta(milliseconds=timestep))
            nexttime = lasttime + datetime.timedelta(milliseconds=timestep)

            # Wait if needed
            if nexttime > current:
                ratehistory[tag] = nexttime
                waittime = (nexttime - current).total_seconds()
                _report("[ratecontrol] Rate is too high,"
                        " wait for {} msec.".format(waittime))
                time.sleep(waittime)
            else:
                ratehistory[tag] = current

            return func(*args, **kwargs)
        return run
    return deco


def clear(tag):
    """Clear rate control hitory.

    Args:
      tag(str): Tag for function.

    """
    global ratehistory
    if tag in ratehistory.keys():
        del(ratehistory[tag])
