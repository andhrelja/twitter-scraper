#%%

import os 
import time 
import modin.pandas as pd 
import matplotlib.pyplot as plt

start = time.time()
df = pd.read_csv('/home/milky/infocov/dataset/all_hashtags_counts_2020.csv', index_col=0)

print(len(df))
print(time.time() - start)  

# xticks=[i for i in range(0,len(df))] 
#logy=True
#df[["counts", "retweet_count"]].plot(kind="bar",stacked=True)

#%%


