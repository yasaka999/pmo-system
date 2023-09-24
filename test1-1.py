a ='2023-07-30 19:00:09.000 [rtc-task-6] - result 2023-07-30_19:00:07 recived: 876 error: 0 discard: 0 fix: 526 queueDiscard: 0 handled: 876 sent: 876'

parts = a.split()
print (parts)
b = parts[0]+' '+parts[1][:8]
print (b)

# 写一段冒泡排序算法，用python
# 冒泡排序
# 冒泡排序是一种简单的排序算法。它重复地走访过要排序的数列,一次比较两个元素,如果他们的顺序错误就把他们交换过来。
# 走访数列的工作是重复地进行直到没有再需要交换,也就是说该数列已经排序完成。
# 用python编写
for i in range(len(a)):
    for j in range(len(a)-i-1):
        if a[j] > a[j+1]:
            a[j],a[j+1] = a[j+1],a[j]
                
