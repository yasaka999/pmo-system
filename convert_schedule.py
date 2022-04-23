#! /usr/bin/python -u
# encoding:utf-8
import os
import shutil
import time


def mapping(map_file):
    map1 = {}
    with open(map_file, "r") as f:
        for line in f.readlines():
            line = line.strip("\n")
            b = line.split(",")
            map1[b[0]] = b[1]
    return map1


def checkSchedule(rootdir):
    for src_name in os.listdir(rootdir):
        if src_name.endswith(".txt"):
            map2 = mapping(map_file)
            if map2.has_key(src_name.split(".")[0]):
                dst_name = map2[src_name.split(".")[0]] + ".txt"
                shutil.copy(src_dir + "/" + src_name, dst_dir + "/" + dst_name)
                shutil.copy(src_dir + "/" + src_name, dst_dir + "/" + dst_name + ".ok")
                os.chmod(dst_dir + "/" + dst_name, 0777)
                os.chmod(dst_dir + "/" + dst_name + ".ok", 0777)
                shutil.move(src_dir + "/" + src_name, bak_dir + "/" + src_name)
                print(
                    "%s: Convert %s to %s success"
                    % (
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        src_name,
                        dst_name,
                    )
                )
            else:
                shutil.move(src_dir + "/" + src_name, bak_dir + "/" + src_name)
                print(
                    "%s: ERROR: channel:%s not exist, please add to map.txt"
                    % (
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        src_name.split(".")[0],
                    )
                )


def run(rootdir, interval):
    print("Start monitor %s") % src_dir
    while True:
        try:
            time.sleep(interval)
            checkSchedule(rootdir)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    interval = 10  # second
    map_file = "/opt/xhan/map.txt"
    src_dir = "/opt/xhan/schedule"
    dst_dir = "/opt/xhan/tvadapter"
    bak_dir = "/opt/xhan/schedule_bak"

    run(src_dir, interval)
