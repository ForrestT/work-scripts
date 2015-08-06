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

def get_file_ext_from_file_list(ext, filelist):
	ext_len = 0 - len(ext)
	for filename in filelist:
		if filename[ext_len:] == ext:
			with open(filename, 'r') as f:
				contents = [line.strip() for line in f]
			return contents
	return [] 

def build_dict(dct, key, value):
	if key in dct:
		if value not in dct[key]:
			dct[key].append(value)
	else:
		dct[key] = [value]

def get_ip_and_port(snippet):
	tmp = snippet[snippet.index(':') + 1:].split('/')
	return tmp


parser = argparse.ArgumentParser()

parser.add_argument('-d', '--dir', help='path of directory containing files to analyze')
parser.add_argument('-o', '--output', help='path to output summary results')

args = parser.parse_args()

files = get_file_list_from_args(args)
config = get_file_ext_from_file_list('.config', files)
summary = get_file_ext_from_file_list('.summary', files)

if args.vpn:
	vpn_s_d = {}
	vpn_c_d = {}
	vpn_u_d = {}
if args.inet:
	inet_out_d = {}
	inet_in_d = {}

for f in files:
	print '\nProcessing: %s' % f
	with open(f, 'r') as log:
		# prev_time, prev_id = '',''
		for line in log:
			if args.vpn:
				if 'ASA-5-713049' in line:
					time = line[:15]
					temp = line.split('Group = ')[1].split(', ')
					# if (time == prev_time) and (temp[0] == prev_id): continue
					if temp[1][:8] == 'Username':
						username = temp[1].split('Username = ')[1]
						build_dict(vpn_c_d, temp[0], [time, username])
						build_dict(vpn_u_d, temp[0], username)
					else:
						build_dict(vpn_s_d, temp[0], time)
					# prev_time, prev_id = time, temp[0]
				elif 'ASA-6-716001' in line:
					time = line[:15]
					temp = line.split('<')
					groupname = temp[1].split('>')[0]
					username = temp[2].split('>')[0]
					build_dict(vpn_c_d, groupname, [time, username])
					build_dict(vpn_u_d, groupname, username)
			if args.inet:
				if ('ASA-6-302013' or 'ASA-6-302015') in line:
					temp = line.split('Built ')[1].split(' ')
					direction = temp[0]
					protocol = temp[1]
					outside = get_ip_and_port(temp[5])
					inside = get_ip_and_port(temp[8])
					if direction == 'outbound':
						build_dict(inet_out_d, inside[0], ','.join([outside[0], protocol, outside[1]]))
					elif direction == 'inbound':
						build_dict(inet_in_d, inside[0], ','.join([outside[0], protocol, inside[1]]))


with open(args.output,'w') as f:
	# Output File Header
	f.write('Summary generated from file(S):\n')
	for fi in files:
		f.write('%s\n' % fi)
	f.write('\n\n\n')
	if args.vpn:
		# Output Brief Summary
		f.write('Brief Info - VPNs Last Use\n')
		for key in vpn_s_d:
			f.write('\t%s\n\t\tHits: %i\n\t\tLast Hit:%s\n' % (key, len(vpn_s_d[key]), vpn_s_d[key][-1]))
		for key in vpn_c_d:
			f.write('\t%s\n\t\tHits: %i\n\t\tLast Hit:%s\n' % (key, len(vpn_c_d[key]), vpn_c_d[key][-1][0]))
		f.write('\n\n\nBrief Info - VPN User Summary\n')
		for key in vpn_u_d:
			f.write('\t%s - Unique Users: %i\n' % (key, len(vpn_u_d[key])))
			for u in vpn_u_d[key]:
				f.write('\t\t%s\n' % u)
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
			f.write('\n\n\n')
	if args.inet:
		f.write('Brief Info - Outbound Internet Connections\n')
		for key in inet_out_d:
			f.write('\n%s - Total Hits: %i\n' % (key, len(inet_out_d[key])))
			for item in set(inet_out_d[key]):
				f.write('\t%s\tHits: %i\n' % (item, inet_out_d[key].count(item)))
			#f.write('\t%s\t%s\t%s / %s\n' % (key, inet_out_d[key][0], inet_out_d[key][1], inet_out_d[key][2]))
		f.write('Brief Info - Inbound Internet Connections\n')
		for key in inet_in_d:
			f.write('\n%s - Total Hits: %i\n' % (key, len(inet_in_d[key])))
			for item in set(inet_in_d[key]):
				f.write('\t%s\tHits: %i\n' % (item, inet_in_d[key].count(item)))
			#f.write('\t%s\t%s\t%s / %s\n' % (key, inet_in_d[key][0], inet_in_d[key][1], inet_in_d[key][2]))


print '\nOutput File Created: %s' % args.output
