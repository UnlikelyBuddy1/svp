from parsing import *
from graph import *
import pandas as pd
from poi import *

# data_frame = parse('../data/original/set', True)
# data_frame = add_week_number(data_frame)
# save_per_week(data_frame)

week_frame = pd.read_csv('./output/original/weeks/data_2015_10.csv', sep=',')
tiled_week_frame = create_lat_lon_tiles(week_frame, 0.1, 0.1)
users = separate_users(tiled_week_frame)
a_specifique_user = users[1]
print(a_specifique_user)
matrix = generate_markov_chain(a_specifique_user, time_interval=30)
plot_markov_chain_simple(matrix, threshold=0.5)
plot_markov_chain_heatmap(matrix)
# plot_image(tiled_week_frame)