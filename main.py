import os
from time import time

from melody_comparison import run_comparison

global_humming_path = 'dataset/hummings/'

hummings = os.listdir(global_humming_path)

for humming in hummings:
    start_time = time()
    print('Humming file: ' + humming)
    run_comparison(humming)
    print('################################################')
    print('################################################')
