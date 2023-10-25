from parsing import *
from graph import *

ORIGINAL_SET_PATH = "../original/c3465dad3864bb1e373891fdcfbfcca5f974db6a9e0b646584e07c5f554d7df7"
ANONYMIZED_SET_PATH = "../data/autofill_444_files/S_user_34_c046155c388437412a8755d2f980efb443817bc322e454409e6eeea89714302c"

data_frame = parse(ORIGINAL_SET_PATH, 100)
data_frame = add_week_number(data_frame)
save_per_week(data_frame)
#data_frame = parse(ANONYMIZED_SET_PATH, 100)