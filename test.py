import pandas as pd
import numpy as np
import datetime
from upload_data import *
import tempfile

temp_dir = tempfile.TemporaryDirectory()
print(temp_dir.name)
print(type(temp_dir.name))
# use temp_dir, and when done:
# temp_dir.cleanup()
