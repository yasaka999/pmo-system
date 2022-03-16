from __future__ import print_function
mapping={'0':'w','1':'m','2':'i','3':'p','4':'t','5':'v','6':'c','7':'s','8':'x','9':'j'}
s_file="b.log"
d_file="c.log"
log= open(d_file, 'w')
with open(s_file,'r') as sfile:
    for l in sfile.readlines():
        s=l.split(',')
        if (s[3][0:11].isdigit() and len(s[3][0:11])==11):
                s[3]=mapping[s[3][0]]+mapping[s[3][1]]+mapping[s[3][2]]+s[3][3:]
        print (','.join(s),end='',file=log)
log.close