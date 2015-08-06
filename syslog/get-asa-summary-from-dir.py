"""
Meant to pull required info from ASA syslogs and provide summary info

Relevent Syslog IDs:
	5-713049 	VPN - IPsec Security Negotiation Complete
	6-716001	WEBVPN - Webvpn session started (AnyConnect)
	6-302013	TCP - Built connection
	6-302014	TCP - Teardown connection
	6-302015	UDP - Built connection
	6-302016	UDP - Teardown connection
	6-106100	ACL - hit on ACL, first packet only
"""

import argparse, os

def get_files_from_dir(path):
	f = []
	for (dirpath, dirnames, filenames) in os.walk(path):
		f.extend(filenames)
		break
	return f

def get_file_list_from_args(arg):
	if arg.dir:
		files = [args.dir + '\\' + f for f in get_files_from_dir(arg.dir)]
	else:
		cwd = os.getcwd()
		files = [cwd + '\\' + f for f in get_files_from_dir(cwd)]
	return files

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dir', help='path of directory containing files to analyze')
parser.add_argument('-o', '--output', help='path to output summary results')
args = parser.parse_args()

files = get_file_list_from_args(args)
summary = []

if args.output:
	if args.output[-8:] == '.summary':
		output = args.output:
	else:
		output = args.output + '.summary'
else:
	output = 'asa-vpn-logs.summary'

for f in files:
	if f[-4:] != '.log':
		continue
	elif:
		print '\nProcessing: %s' % f
		with open(f, 'r') as log:
			for line in log:
				if 'ASA-6-106100' in line:
					summary.append(line)
				elif 'ASA-5-713049' in line:
					summary.append(line)
				elif 'ASA-6-716001' in line:
					summary.append(line)

with open(output,'w') as f:
	for line in summary:
		f.write(line)

print '\nOutput File Created: %s' % output
