s_file = "/Users/hanxiong/Downloads/index_xhan.txt"
with open(s_file, "r") as sfile:
    for l in sfile.readlines():
        l = l.strip("\n")
        s = l.split(",")
        for i in range(1, len(s)):
            if "_" in s[i]:
                s_id = s[i][0:32]
                if s.count(s_id) == 0:
                    print(s)
