#%%
import os 
import pandas as pd 

path = r'/home/milky/infocov/scrape_tweets/preproc_2021'

tweets_dict = {}

for r, d, f in os.walk(path):
    for file in f:
        if '.csv' in file:
            tweets_dict.update({file : os.path.join(r, file)})
                        
df_all = pd.DataFrame()
counter = 0
val = 0 

filenum=0
for file, path in tweets_dict.items():
    # if counter == 15: 
    #     val += 1
    #     df_all.to_csv('./preproc_2021/all_' + str(val) + '.csv', encoding="utf-8")
    #     df_all = pd.DataFrame()
    #     counter = 0

    try:     
        df = pd.read_csv(path,index_col=0, engine='python', encoding="utf-8")
        df_all = pd.concat([df_all,df], axis=0)
        counter += 1
        filenum+=1
        print(filenum)
    except:
        pass

df_all.to_csv('all_new.csv', encoding="utf-8")

#%%

# df_all.to_csv('all_2021_11.csv')
# df_all.to_pickle('/home/milky/infocov/dataset_main/files/all_2020_2.pkl')




# path = '/home/milky/infocov/dataset/tmp'

# tweets_dict = {}

# for r, d, f in os.walk(path):
#     for file in f:
#         if '.csv' in file:
#             tweets_dict.update({file : os.path.join(r, file)})
            
            
# df_all = pd.DataFrame()
# counter = 0
# val = 0 
# for file, path in tweets_dict.items():
#     # if counter == 40: 
#     #     val += 1
#     #     df_all.to_csv('/home/milky/infocov/dataset/tmp/all_' + str(val) + '.csv')
#     #     df_all = pd.DataFrame()
#     #     counter = 0
        
#     df = pd.read_csv(path,index_col=0, engine='python')
#     df_all = pd.concat([df_all,df], axis=0)
#     counter += 1
#     # except:
#     #     df = pd.DataFrame()
#     #     counter += 1
#     print(counter)

#df_all.to_csv('/home/milky/infocov/dataset/all_2020_1.csv')

#%%
df1 = pd.read_csv('/home/milky/infocov/dataset_twitter/Cro-Twitter.csv', index_col=0)
# df1 = df1.drop(['Unnamed: 0.1'], axis=1)
print(df1.columns)
df1 = df1.set_index('id_str')

print('len of df1 {} '.format(len(df1)))

df2 = pd.read_csv('all_new.csv', index_col=0)
print(df2.columns)
df2 = df2.set_index('id_str')
print('len of df2 {}'.format(len(df2)))

df_all = pd.concat([df1,df2], axis=0)
print('len df all {}'.format(len(df_all)))

df_all = df_all.drop_duplicates(keep='first')
print('len df all', len(df_all))

#%%

df_all.to_csv('all_new.csv')

#%%
# import time 
# import modin.pandas as pd

# start = time.time()

# df = pd.read_csv('/home/milky/infocov/dataset/hashtags/all_hashtags_2020.csv', index_col=0)  
# print(len(df))



# #? SECECT TWEETS THAT ARE RETWEETS
# retweets = df[~df['retweeted_status.id_str'].isnull()]
# # retweets.to_csv('/home/milky/infocov/dataset/original_2020.csv')

# #? SELECT ORIGINAL TWEETS
# original_tweets = df[df['retweeted_status.id_str'].isnull()]
# #original_tweets.to_csv('/home/milky/infocov/dataset/original_2020.csv')


# #%%
# #? COUNT OCCURENCIES IDS OF RETWEETED TWEETS
# from collections import Counter
# retweet_ids = retweets['retweeted_status.id_str'].tolist()

# df_res = pd.DataFrame(Counter(retweet_ids).keys(), columns=['id_str'])
# df_res['counts'] = Counter(retweet_ids).values()
# df_res = df_res.set_index('id_str')

# #%%
# #TAKE IDS OF RETWEETS THAT WE HAVE IN ORIGINAL TWEETS AND THEIR RETWEET COUNT
# start = time.time()
# indexes_list = df_res.index.to_list()
# #values = numpy.isin(original_tweets.index, indexes_list)

# values = original_tweets.index.isin(indexes_list)
# res = original_tweets.loc[values]
# res = res[['retweet_count']]

# #%%
# # final = res.join(df_res)
# # final = pd.concat([res, df_res], axis=1)

# final = df_res.merge(res, on='id_str', how='inner')
# final = final[final['retweet_count'].notna()]
# final = final.sort_values(by=['counts'], ascending=False)

# final.to_csv('/home/milky/infocov/dataset/retweets_in_original_inner_2020.csv')


#%%
# print(time.time() - start)
# print(final.index)
# print(final.columns)
# final.head(10)





#df_res = df_res.dropna(inplace=True)
#? SELECT ROWS FROM ORIGINAL TWEETS 


# retweets_ids = retweets_ids.to_dict()
# print(retweets_ids.index.get_level_values('retweeted_status.id_str'))

# retweets_count = retweets_ids
# print(retweets_count['retweeted_status.id_str'])

# retweets_ids = count[['retweeted_status.id_str']]
# selection = df[df.index.isin([retweets_ids])]

#subset = df.loc[[retweets_ids] ,['retweet_count'] ]
#retweet_count = df['retweet_count']

#%%
## COUNT OF RETWEETS IDS 
# count = retweet_val.value_counts() 

# print(count.sort_values(ascending=False))
# print(time.time() - start)   

# count = count.head(1000)

# 
# count = count.reset_index(drop=True)
# ax = count.plot.bar()

# for i, t in enumerate(ax.get_xticklabels()):
#     if (i % 50) != 0:
#         t.set_visible(False)

# print(time.time() - start)  
#%%

