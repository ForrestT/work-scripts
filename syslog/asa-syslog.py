import argparse, os

def get_files_from_dir(path):
	f = []
	for (dirpath, dirnames, filenames) in os.walk(path):
		f.extend(filenames)
		break
	return f

def get_file_list_from_args(arg):
	if arg.file:
		files = [arg.file]
	elif arg.dir:
		files = [args.dir + '\\' + f for f in get_files_from_dir(arg.dir)]
	return files

def build_dict(dct, key, value):
	if key in dct:
		dct[key].append(value)
	else:
		dct[key] = [value]

parser = argparse.ArgumentParser()

group1 = parser.add_mutually_exclusive_group()
group1.add_argument('-f', '--file', help='path of file to analyze')
group1.add_argument('-d', '--dir', help='path of directory containing files to analyze')
parser.add_argument('-v', '--vpn', help='set to analyze vpn history', action='store_true')
parser.add_argument('-i', '--inet', help='set to analyze intenet traffic history', action='store_true')
parser.add_argument('-o', '--output', help='path to output summary results')
parser.add_argument('-b', '--brief', help='outputs brief summary only', action='store_true')

args = parser.parse_args()

files = get_file_list_from_args(args)

if args.vpn:
	vpn_s_d = {}
	vpn_c_d = {}
if args.inet:
	inet_d = {}

for f in files:
	print '\nProcessing: %s' % f
	with open(f, 'r') as log:
		prev_time, prev_id = '',''
		for line in log:
			if args.vpn:
				if line.count('ASA-5-713049') != 0:
					time = line[:15]
					temp = line.split('Group = ')[1].split(', ')
					if (time == prev_time) and (temp[0] == prev_id): continue
					if temp[1][:8] == 'Username':
						build_dict(vpn_c_d, temp[0], [time, temp[1]])
					else:
						build_dict(vpn_s_d, temp[0], time)
					prev_time, prev_id = time, temp[0]
			if args.inet:
				pass

with open(args.output,'w') as f:
	# Output File Header
	f.write('Summary generated from file(S):\n')
	for fi in files:
		f.write('%s\n' % fi)
	f.write('\n\n\n')
	# Output Brief Summary
	f.write('Brief Info - VPNs Last Use\n')
	for key in vpn_s_d:
		f.write('\t%s\n\t\tHits: %i\n\t\tLast Hit:%s\n' % (key, len(vpn_s_d[key]), vpn_s_d[key][-1]))
	for key in vpn_c_d:
		f.write('\t%s\n\t\tHits: %i\n\t\tLast Hit:%s\n' % (key, len(vpn_c_d[key]), vpn_c_d[key][-1][0]))
	f.write('\n\n\n')
	# Output All Site-2-Site VPN Info, unless --brief flag is set
	if args.brief == False:
		f.write('Detailed Info - All entries from all VPNs\n')
		for key in vpn_s_d:
			f.write('\n%s - hits: %i\n' % (key, len(vpn_s_d[key])))
			for time in vpn_s_d[key]:
				f.write('\t%s\n' % time)
		# Output All Client VPN Info
		for key in vpn_c_d:
			f.write('\n%s - hits: %i\n' % (key, len(vpn_c_d[key])))
			for time in vpn_c_d[key]:
				f.write('\t%s , %s\n' % (time[0],time[1]))

print 'done'
