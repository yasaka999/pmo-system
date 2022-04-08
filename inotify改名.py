#! /usr/bin/python -u
# encoding:utf-8
import os
import shutil
import time

from pyinotify import (
    IN_ACCESS,
    IN_ATTRIB,
    IN_CREATE,
    IN_DELETE,
    IN_MODIFY,
    Notifier,
    ProcessEvent,
    WatchManager,
)


class EventHandler(ProcessEvent):
    """事件处理"""

    def process_IN_CREATE(self, event):
        print (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            + ": Create file: %s " % os.path.join(event.path, event.name)
        )
        src_name = event.name
        if src_name.endswith(".txt"):
            map2 = mapping(map_file)
            dst_name = map2[src_name.split(".")[0]]
            shutil.copy(src_dir + "/" + src_name, dst_dir + "/" + dst_name + ".txt")
            #            print ("copy  to " + dst_dir + " success")
            shutil.copy(src_dir + "/" + src_name, dst_dir + "/" + dst_name + ".txt.ok")
            shutil.move(src_dir + "/" + src_name, bak_dir + "/" + src_name)
            #            print ("backup to " + bak_dir + " success")
            print (
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                + ": convert "
                + src_name
                + " to "
                + dst_name
                + ".txt success"
            )


def FSMonitor(path="."):
    wm = WatchManager()
    mask = IN_DELETE | IN_CREATE | IN_MODIFY | IN_ACCESS | IN_ATTRIB
    notifier = Notifier(wm, EventHandler())
    wm.add_watch(path, mask, rec=True)
    print "now starting monitor %s" % (path)
    while True:
        try:
            notifier.process_events()  # 绑定处理event方法
            if notifier.check_events():  # 检查是否有有可读取的新event
                notifier.read_events()  # 读取event，交给EventHandler处理
        except KeyboardInterrupt:
            notifier.stop()
            break


def mapping(map_file):
    map1 = {}
    with open(map_file, "r") as f:
        for line in f.readlines():
            line = line.strip("\n")
            b = line.split(",")
            map1[b[0]] = b[1]
    return map1


if __name__ == "__main__":
    map_file = "/opt/xhan/map.txt"
    src_dir = "/opt/xhan/schedule"
    dst_dir = "/opt/xhan/tvadapter"
    bak_dir = "/opt/xhan/schedule_bak"

    FSMonitor(src_dir)
