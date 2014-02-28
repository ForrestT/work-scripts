""" CheckPoint SmartLog R75.46
	Export to CSV = 56 columns, max 10000 lines
	Most columns useless (w/o add-in blades) or redundant
	Useful columns and re-mapped:
		0	0	Time
		1 	3	Origin (node)
		2 	4 	Action (Reject, Drop, Accept, etc)
		3 	5 	Source (either "IP" or "name(IP)" )
		4 	7 	Destination	(same as Source)
		5 	8	Service ( "name (protocol/port)" )
		6 	9	Rule (rule #, can be empty if IPS dropped)
		7 	13	Description (elaboration on Action + Rule)
		8 	14	Protocol ( "protocol (number)" )
		9 	20	Source Port (just port number)
		10 	21 	DestinationPort (just port number)

"""

def analyze_log(logs):
	total_lines = len(logs)
	unique_src = count_uniques_in_pos(logs,3)
	unique_dst = count_uniques_in_pos(logs,4)
	unique_act = count_uniques_in_pos(logs,2)
	return unique_src, unique_dst, unique_act


def count_uniques_in_pos(logs,pos):
	uniques = {}
	for line in logs:
		if line[pos] in uniques:
			uniques[line[pos]] += 1
		else:
			uniques[line[pos]] = 1
	uniques.pop(logs[0][pos])
	return uniques



import argparse

parser = argparse.ArgumentParser()
parser.add_argument('file', help='file to be read')
parser.add_argument('-o', '--output', help='output to filename with useless fields stripped')
parser.add_argument('-a', '--analysis', help='analyze logs and output analysis to filename')
args = parser.parse_args()

with open(args.file,'r') as f:
	log = [[l[0],l[3],l[4],l[5],l[7],l[8],l[9],l[13],l[14],l[20],l[21]] for l in [line.split(',') for line in f]]

if args.output:
	with open(args.output, 'w') as f:
		for line in log:
			f.write(','.join(line)+'\n')

if args.analysis:
	srcd, dstd, actd = analyze_log(log)
	with open(args.analysis, 'w') as f:
		f.write('Total number of entries in log: ' + str(len(log)-1) + '\n')
		f.write('\n\nSource IP addresses - %i unique\n__________________________________________________\n' % len(srcd))
		for key in srcd:
			f.write('%s\t%s\n' % (key, str(srcd[key])))
		f.write('\n\nDestination IP addresses - %i unique\n__________________________________________________\n' % len(dstd))
		for key in dstd:
			f.write('%s\t%s\n' % (key, str(dstd[key])))
		f.write('\n\nAction Taken - %i unique\n__________________________________________________\n' % len(actd))
		for key in actd:
			f.write('%s\t%s\n' % (key, str(actd[key])))
		




