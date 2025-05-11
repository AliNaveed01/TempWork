import time
import random
import os
import pandas as pd
import os
import shutil
from datetime import datetime
import logging


def random_delay(min_sec=0.2, max_sec=1.0):
    """Introduces a random delay to avoid bans."""
    delay = random.uniform(min_sec, max_sec)
    # print(f"Sleeping for {delay:.2f} seconds to avoid detection.")
    time.sleep(delay)
    return delay