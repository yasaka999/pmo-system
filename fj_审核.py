import sqlite3
import requests
import json

url = "http://172.16.20.128:8100/v2/vcr/media"

querystring = {"taskId": "pcckdy3t1grh5nxxd62"}

response = requests.request("GET", url, params=querystring)

messages = json.loads(response.text)

# 连接到 SQLite 数据库
conn = sqlite3.connect("example.db")
try:
    c = conn.cursor()

    task = messages.copy()
    taskId = task["taskId"]
    c.execute(
        """INSERT  INTO Task (taskId, userName, source, description,preset,  status, label, duration, notification, createTime,startTime, finishTime,streamId,callbackType)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?)""",
        (
            taskId,
            task["userName"],
            task["source"],
            task["description"],
            task["preset"],
            task["status"],
            task["label"],
            task["duration"],
            task["notification"],
            task["createTime"],
            task["startTime"],
            task["finishTime"],
            task["streamId"],
            task["callbackType"],
        ),
    )

    # 插入数据
    for result in task.get("results", []):
        c.execute(
            """INSERT OR IGNORE INTO Result (taskId, type) 
                        VALUES (?, ?)""",
            (taskId, result["type"]),
        )
        resultId = c.lastrowid
        for item in result.get("items", []):
            c.execute(
                """INSERT OR IGNORE INTO Item (resultId, taskId, label, subType, confidence, extra, target, timeInSeconds, startTimeInSeconds, endTimeInSeconds) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?)""",
                (
                    resultId,
                    taskId,
                    item["label"],
                    item["subType"],
                    item["confidence"],
                    item.get("extra", ""),
                    item["target"],
                    item.get("timeInSeconds", 0),
                    item["startTimeInSeconds"],
                    item["endTimeInSeconds"],
                ),
            )
            itemId = c.lastrowid
            evidence = item.get("evidence", {})
            c.execute(
                """INSERT OR IGNORE INTO Evidence (itemId,taskId, thumbnail, leftOffsetInPixel, topOffsetInPixel, widthInPixel, heightInPixel, text) 
                        VALUES (?, ?, ?, ?, ?, ?, ?,?)""",
                (
                    itemId,
                    taskId,
                    evidence.get("thumbnail", ""),
                    evidence.get("location", {}).get("leftOffsetInPixel", 0),
                    evidence.get("location", {}).get("topOffsetInPixel", 0),
                    evidence.get("location", {}).get("widthInPixel", 0),
                    evidence.get("location", {}).get("heightInPixel", 0),
                    evidence.get("text", ""),
                ),
            )

    conn.commit()
except sqlite3.IntegrityError as e:
    # 捕获UNIQUE constraint failed异常
    print("Error: ", e)
    print("Task with this ID already exists.")
    # 回滚事务
    conn.rollback()
else:
    print("Task added successfully.")
finally:
    # 关闭数据库连接
    conn.close()

'''
    c.execute(
        """CREATE TABLE IF NOT EXISTS Task
                (taskId text PRIMARY KEY, userName text, source text, description text,preset text,  status text, label text, duration int,notification text, createTime timestamp, startTime timestamp,finishTime timestamp, streamId text, callbackType text)"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS Result
                (resultId INTEGER PRIMARY KEY AUTOINCREMENT, taskId text, type text, FOREIGN KEY (taskId) REFERENCES Task(taskId))"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS Item
                (itemId INTEGER PRIMARY KEY AUTOINCREMENT, resultId int, taskId text, label text, subType text, confidence real, extra text, target text, timeInSeconds int, startTimeInSeconds int, endTimeInSeconds int, FOREIGN KEY (resultId) REFERENCES Result(resultId))"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS Evidence
                (evidenceId INTEGER PRIMARY KEY AUTOINCREMENT, itemId int, taskId text, thumbnail text, leftOffsetInPixel int, topOffsetInPixel int, widthInPixel int, heightInPixel int, text text, FOREIGN KEY (itemId) REFERENCES Item(itemId))"""
    )
'''
