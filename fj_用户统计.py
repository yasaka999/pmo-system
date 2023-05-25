import time
file_path = '/Users/hanxiong/temp/Contentviewlog_20230228.log'

start_time = time.time()
# 使用集合(set)进行去重
unique_users = set()

# 逐行读取文件并提取userid进行去重
with open(file_path, 'r', encoding='latin-1') as file:
    for line in file:
        userid = line.split('|',1)[0]
        unique_users.add(userid)
unique_user_count = len(unique_users)
end_time = time.time()
print("Unique User Count:", unique_user_count)
print("Time taken:", end_time - start_time)