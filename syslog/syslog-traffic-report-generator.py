import argparse,re
from os import walk


parser = argparse.ArgumentParser()

option1 = parser.add_mutually_exclusive_group()
option1.add_argument('-f', '--file', help='file to be parsed')
option1.add_argument('-d', '--directory', help='directory containing files to be parsed')

args = parser.parse_args()

if args.file:
	files = [args.file]
elif args.directory:
	files = [f for _,_,f in walk(args.directory)]
	files = files[0]


for f in files:
	print 'opening %s' % f
	syslog = open(args.directory + '\\' + f)
	logs = {}
	event_id = re.compile('-6-30201[35]')
	for line in syslog:
		if event_id.search(line) is not None:
			temp = line.split('Built ')
			temp = re.split('[\s:/]', temp[1])
			if int(temp[7]) < int(temp[13]):
				prt = temp[7]
				dst_int = temp[5]
				dst_ip = temp[6]
				src_int = temp[11]
				src_ip = temp[12]
			else:
				prt = temp[13]
				dst_int = temp[11]
				dst_ip = temp[12]
				src_int = temp[5]
				src_ip = temp[6]
				
			key = "%s,%s,%s,%s,%s,%s/%s" % (temp[0], src_int, src_ip, dst_int, dst_ip, temp[1], prt)
		else:
			continue
		
		if logs.has_key(key):
			logs[key] = logs[key] + 1
		else:
			logs[key] = 1
	syslog.close()

output_file = open('traffic-report.csv', 'w')
output_file.write('direction,src int,src IP,dst int, dst IP,protocol,occurences')
for item in logs.iterkeys():
	out_line = "\n%s,%i" %  (item, logs[item])
	output_file.write(out_line)
output_file.close()