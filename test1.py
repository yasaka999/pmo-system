lst = [ 3, 6, 9, 12, 3, 30, 15, 9, 45, 36]
dupItems = []
uniqItems = {}
for x in lst:
   if x not in uniqItems:
      uniqItems[x] = 1
   else:
      if uniqItems[x] == 1:
         dupItems.append(x)
      uniqItems[x] += 1
print(dupItems)