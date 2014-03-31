import socket, re, argparse

def resolve_name(name):
	ip = ''
	try:
		ip = socket.gethostbyname(name)
	except socket.gaierror:
		return "ERROR: Could not resolve name."
	except socket.error:
		return "ERROR: Host failed to respond."
	return ip


parser = argparse.ArgumentParser()
parser.add_argument('sitecode', help='Site Code that identifies the network')
parser.add_argument('dataprefix', help='Prefix for data network: must be first two octects')
parser.add_argument('voiceprefix', help='Prefix for voice network: must be first two octects')
parser.add_argument('--filename', '-f', help='source filename conatining Cisco Works exported data')
args = parser.parse_args()


#setting arguments to variables
if args.filename:
	fname = args.filename
else:
	fname = 'C:\GitHub\work-scripts\ACS\Full Device Export With Site codes.csv'

site_code = args.sitecode.lower()

if args.dataprefix[-1:] == '.':
	ip_prefix_data = args.dataprefix
else:
	ip_prefix_data = args.dataprefix + '.'

if args.voiceprefix[-1:] == '.':		
	ip_prefix_voice = args.voiceprefix
else:
	ip_prefix_voice = args.voiceprefix + '.'


#Initializing lists and regex
unresolved_list = []
data_list = []
voice_list = []
raw_list = []
ipv4_regex = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')


# Creates list of DNS names / IP Addresses from Cisco-Works exported CSV
with open(fname,'r') as f:
	devices = [line.split(',') for line in f]

#Sorts names-to-be-resolved and IP addresses into respective lists
for d in devices:
	dn = d[0].rstrip('.spectrum-health.org')
	dc = d[-1].strip().lower()
	if (site_code + '-') in dn.lower()[:len(site_code)+1]:
		unresolved_list.append(dn)
		raw_list.append(dn)
	elif ip_prefix_data in dn:
		data_list.append(dn+'/32')
		raw_list.append('N/A\t%s' % dn)
	elif ip_prefix_voice in dn:
		voice_list.append(dn+'/32')
		raw_list.append('N/A\t%s' % dn)
	elif site_code == dc:
	 	raw_list.append("%s\tSite Code doesn't match Hostname" % dn)


#Resolves each name via DNS and puts into proper list
for name in unresolved_list:
	ip = resolve_name(name)
	i = raw_list.index(name)
	raw_list[i] = '%s\t%s' % (raw_list[i], ip)
	if ip[:6] == ip_prefix_data:
		data_list.append(ip+'/32')
	elif ip[:6] == ip_prefix_voice:
		voice_list.append(ip+'/32')


#Writes out the IP addresses in the proper format for importing into ACS
with open(site_code + '.txt', 'w') as f:
	f.write('\nData - %i hosts\n\n' % len(data_list))
	f.write(';'.join(data_list))
	f.write('\n\nVoice - %i hosts\n\n' % len(voice_list))
	f.write(';'.join(voice_list))
	f.write('\n\n\n\nRaw Device List from source - %i hosts\n\n' % len(raw_list))
	for d in raw_list:
		# f.write(d + '\n')
		dl = d.split('\t')
		temp1 = '{:<30}'.format(dl[0])
		temp2 = temp1 + dl[1] + '\n'
		f.write(temp2)
