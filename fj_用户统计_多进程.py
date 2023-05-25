import time
import multiprocessing

file_path = '/Users/hanxiong/temp/Contentviewlog_20230228.log'

def process_line(line):
    userid = line.split('|')[0]
    return userid

if __name__ == '__main__':
    start_time = time.time()
    unique_users = set()

    with open(file_path, 'r', encoding='latin-1') as file:
        # 创建进程池，根据 CPU 核心数自动确定进程数量
        with multiprocessing.Pool() as pool:
            # 使用进程池并发处理文件的每一行
            results = pool.map(process_line, file)

            # 遍历并行处理的结果
            for userid in results:
                unique_users.add(userid)

    unique_user_count = len(unique_users)
    end_time = time.time()
    print("Unique User Count:", unique_user_count)
    print("Time taken:", end_time - start_time)
