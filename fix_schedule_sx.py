# -*- coding: utf-8 -*-
import sys
from cyberbrain import trace
@trace
def fix_schedule(schedule):
    # 以 Date: 为分隔符，分割文本
    schedules = schedule.strip().split('Date:')
    schedules = [entry.strip() for entry in schedules if entry.strip()]
    #print(schedules)

    # 存储修正后的节目单条目
    corrected_entries = []

    # 存储错误日志
    error_log = []

    # 遍历每个节目单条目，执行时间错误修正
    for entry in schedules:
        # 分割每个条目成行
        lines = entry.split('\n')

        # 提取 Channel 行
        channel_line = lines[0]
        #print(channel_line)

        # 遍历每一行，修正数据
        for i in range(1, len(lines)-1):  # 从第2行开始，因为第一行不需要处理
            current_line = lines[i]
            next_line = lines[i + 1]  # 下一行

            current_time_range = current_line.split('|')[0]
            next_time_range = next_line.split('|')[0]

            current_end_time = current_time_range.split('-')[1]
            next_start_time = next_time_range.split('-')[0]

            # 如果当前行的结束时间大于下一行的开始时间，则修正当前行的结束时间
            if int(current_end_time) > int(next_start_time):
                corrected_end_time = next_start_time
                corrected_time_range = current_time_range.split('-')[0] + "-" + corrected_end_time
                lines[i] = corrected_time_range + "|" + current_line.split('|')[1]

                # 记录错误日志
                error_log.append(schedules[0] + channel_line + " Fixed: " + current_line + " -> " + lines[i])

        # 重新构建修正后的节目单条目，包括 Channel: 行
        corrected_entry = "\n".join([channel_line] + lines[1:])
        corrected_entries.append(corrected_entry)

    # 返回修正后的节目单条目和错误日志
    return "\nDate:".join(corrected_entries), "\n".join(error_log)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python program_fixer.py input_file output_file")
        sys.exit(1)

    input_file_name = sys.argv[1]
    output_file_name = sys.argv[2]
    error_log_file_name = "error.log"  # 错误日志文件名

    # 打开输入文件进行读取
    with open(input_file_name, 'r') as input_file:
        schedule = input_file.read()

    # 调用函数修正节目单并获取错误日志
    corrected_schedule, error_log = fix_schedule(schedule)

    # 打开输出文件进行写入
    with open(output_file_name, 'w') as output_file:
        # 将修正后的结果写入输出文件
        output_file.write(corrected_schedule)

    # 打开错误日志文件进行写入
    with open(error_log_file_name, 'a') as error_log_file:
        # 将错误日志写入文件
        error_log_file.write(error_log+"\n")
    if error_log:
        # 打开错误日志文件进行写入
        with open(error_log_file_name, 'w') as error_log_file:
            # 将错误日志写入文件
            error_log_file.write(error_log)
        print("Program guide has been fixed. Error log saved in error.log.")
    else:
        print("Schedules all correct, nothing change.")
