import sqlite3
# import requests
# import json

messages = {
    "userName":
    "default",
    "taskId":
    "pbyk32sxjybak4swz1p",
    "source":
    "http://172.16.20.128:8086/webupload/ad_brand___ygtkwy27yg.mp4",
    "description":
    "",
    "preset":
    "default",
    "status":
    "SUCCESS",
    "label":
    "REJECT",
    "duration":
    14,
    "notification":
    "",
    "results": [{
        "type":
        "ad_brand",
        "items": [{
            "subType": "brand",
            "target": "thumbnail",
            "timeInSeconds": 0,
            "startTimeInSeconds": 0,
            "endTimeInSeconds": 15,
            "confidence": 99.46,
            "label": "REJECT",
            "extra": "湖南卫视",
            "evidence": {
                "thumbnail":
                "http://172.16.20.128:8086/videoai/563c3dd19a7e7c7d24a377a87d8aee73/pbyk32sxjybak4swz1p/thumbnails/00000.jpg",
                "location": {
                    "leftOffsetInPixel": 49,
                    "topOffsetInPixel": 29,
                    "widthInPixel": 67,
                    "heightInPixel": 53
                }
            }
        }, {
            "subType": "brand",
            "target": "thumbnail",
            "timeInSeconds": 7,
            "startTimeInSeconds": 7,
            "endTimeInSeconds": 8,
            "confidence": 91.91,
            "label": "REVIEW",
            "extra": "百事可乐",
            "evidence": {
                "thumbnail":
                "http://172.16.20.128:8086/videoai/563c3dd19a7e7c7d24a377a87d8aee73/pbyk32sxjybak4swz1p/thumbnails/00007.jpg",
                "location": {
                    "leftOffsetInPixel": 303,
                    "topOffsetInPixel": 359,
                    "widthInPixel": 208,
                    "heightInPixel": 60
                }
            }
        }]
    }, {
        "type":
        "ad_marketing",
        "items": [{
            "subType": "commercial",
            "target": "character",
            "timeInSeconds": 0,
            "startTimeInSeconds": 0,
            "endTimeInSeconds": 1,
            "confidence": 100.0,
            "label": "REJECT",
            "evidence": {
                "thumbnail":
                "http://172.16.20.128:8086/videoai/563c3dd19a7e7c7d24a377a87d8aee73/pbyk32sxjybak4swz1p/thumbnails/00000.jpg",
                "location": {
                    "leftOffsetInPixel": 590,
                    "topOffsetInPixel": 470,
                    "widthInPixel": 307,
                    "heightInPixel": 41
                },
                "text": "思美人和氏璧风 adzop.com"
            }
        }, {
            "subType": "watermark",
            "target": "thumbnail",
            "timeInSeconds": 7,
            "startTimeInSeconds": 7,
            "endTimeInSeconds": 13,
            "confidence": 90.45,
            "label": "REVIEW",
            "evidence": {
                "thumbnail":
                "http://172.16.20.128:8086/videoai/563c3dd19a7e7c7d24a377a87d8aee73/pbyk32sxjybak4swz1p/thumbnails/00007.jpg",
                "location": {
                    "leftOffsetInPixel": 581,
                    "topOffsetInPixel": 345,
                    "widthInPixel": 321,
                    "heightInPixel": 167
                }
            }
        }]
    }],
    "createTime":
    "2023-02-23T02:41:36Z",
    "startTime":
    "2023-02-23T02:41:36Z",
    "finishTime":
    "2023-02-23T02:42:06Z",
    "streamId":
    "",
    "callbackType":
    "vcr"
}

# 连接到 SQLite 数据库
conn = sqlite3.connect("example.db")

# 创建表
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS Task
             (taskId text PRIMARY KEY, userName text, source text, description text,preset text,  status text, label text, duration int,notification text, createTime timestamp, startTime timestamp,finishTime timestamp, streamId text, callbackType text)"""
          )

c.execute("""CREATE TABLE IF NOT EXISTS Result
             (resultId INTEGER PRIMARY KEY AUTOINCREMENT, taskId text, type text, FOREIGN KEY (taskId) REFERENCES Task(taskId))"""
          )

c.execute("""CREATE TABLE IF NOT EXISTS Item
             (itemId INTEGER PRIMARY KEY AUTOINCREMENT, resultId int, label text, subType text, confidence real, extra text, target text, timeInSeconds int, startTimeInSeconds int, endTimeInSeconds int, FOREIGN KEY (resultId) REFERENCES Result(resultId))"""
          )

c.execute("""CREATE TABLE IF NOT EXISTS Evidence
             (evidenceId INTEGER PRIMARY KEY AUTOINCREMENT, itemId int, thumbnail text, leftOffsetInPixel int, topOffsetInPixel int, widthInPixel int, heightInPixel int, text text, FOREIGN KEY (itemId) REFERENCES Item(itemId))"""
          )

task = messages.copy()
task.pop("results")
taskId = task["taskId"]
c.execute(
        """INSERT OR IGNORE INTO Task (taskId, userName, source, description,preset,  status, label, duration, notification, createTime,startTime, finishTime,streamId,callbackType)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?)""",
        (taskId, task["userName"], task["source"], task["description"], task["preset"],
        task["status"], task["label"], task["duration"],task["notification"], task["createTime"],task["startTime"],task["finishTime"],task["streamId"],task["callbackType"])
)

# 插入数据
for result in messages.get("results", []):
    c.execute(
            """INSERT OR IGNORE INTO Result (taskId, type) 
                       VALUES (?, ?)""",
            (taskId, result["type"]),
        )
    resultId = c.lastrowid
    for item in result.get("items", []):
        c.execute(
            """INSERT OR IGNORE INTO Item (resultId, label, subType, confidence, extra, target, timeInSeconds, startTimeInSeconds, endTimeInSeconds) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (resultId, item["label"], item["subType"], item["confidence"],
             item.get("extra", ""), item["target"], item["timeInSeconds"],
             item["startTimeInSeconds"], item["endTimeInSeconds"]),
        )
        itemId = c.lastrowid
        evidence = item.get("evidence", {})
        c.execute(
            """INSERT OR IGNORE INTO Evidence (itemId, thumbnail, leftOffsetInPixel, topOffsetInPixel, widthInPixel, heightInPixel, text) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (itemId, evidence.get("thumbnail", ""), evidence.get(
                "location", {}).get("leftOffsetInPixel", 0),
             evidence.get("location", {}).get(
                 "topOffsetInPixel", 0), evidence.get("location", {}).get(
                     "widthInPixel", 0), evidence.get("location", {}).get(
                         "heightInPixel", 0), evidence.get("text", "")),
        )

conn.commit()
conn.close()
