#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
检查第二天的节目单是否正常
"""
import json
import os
import sys
from datetime import datetime, timedelta
reload(sys)
sys.setdefaultencoding("utf8")
# 计算总时长
def calc_schedule(file):
    with open(file) as f:
        data = json.load(f)
    schedules = data["schedules"]
    channel = data["channel"]["title"]
    duration = 0
    for j in range(len(schedules)):
        start_time = datetime.strptime(schedules[j]["starttime"], "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(schedules[j]["endtime"], "%Y-%m-%d %H:%M:%S")
        duration += (end_time - start_time).days * 24 * 3600 + (
            end_time - start_time
        ).seconds
    return (file, channel, duration / 3600.0)


# 取文件路径
def get_all_path(open_file_path):
    rootdir = open_file_path
    path_list = []
    list = os.listdir(rootdir)
    for i in range(0, len(list)):
        com_path = os.path.join(rootdir, list[i])
        # print(com_path)
        if os.path.isfile(com_path):
            path_list.append(com_path)
        if os.path.isdir(com_path):
            path_list.extend(get_all_path(com_path))
    return path_list


def main():
    path = raw_input("Please input schedule dir: ")
    if path == "":
        path = "/opt/wacos/domain/epgwwwroot/schedules"
    print "Please wait ... ,see the schedule_nc.txt"
    file_list = get_all_path(path)
    date = "_" + (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
    log = open("schedule_nc.txt", "w")
    for i in range(len(file_list)):
        if date in file_list[i]:
            file, channel, duration = calc_schedule(file_list[i])
            if duration < 23:
                print >> log, file, channel, duration, "hours"
    log.close()


if __name__ == "__main__":
    main()
