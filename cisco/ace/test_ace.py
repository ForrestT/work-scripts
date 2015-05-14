from cisco import ACE

test = ACE('tis-slb-ace-dc-1-c2.config')

#INSITE - complicated, branching
print('\n\nTesting INSITE VIP - 10.201.26.201\n\n')
test.getVIPconfig('10.201.26.201')
print('\n')
test.displayVIP()

#HYPERSPACE - has a sticky-group and a redirect serverfarm
print('\n\nTesting HYPERSPACE VIP - 10.201.26.108\n\n')
test.getVIPconfig('10.201.26.108')
print('\n')
test.displayVIP()

