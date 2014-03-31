import socket, re, argparse


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
data_list = []
voice_list = []
# nexus_list = []
ons_list = []
ucs_list = []
wifi_list = []
raw_list = []
ipv4_regex = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\Z')



def resolve_name(name):
	ip = ''
	try:
		ip = socket.gethostbyname(name)
	except socket.gaierror:
		return "ERROR: Could not resolve name."
	except socket.error:
		return "ERROR: Host failed to respond."
	return ip


def get_device_info(line):
	if ipv4_regex.match(line[0]):
		ip = line[0]
		name = line[2].rstrip('.spectrum-health.org')
	else:
		ip = resolve_name(line[0])
		name = line[0].rstrip('.spectrum-health.org')
	code = line[-1].strip()
	return ip, name, code

def format_raw(ip, name, comment=''):
	temp1 = '{:<30}'.format(ip)
	temp2 = '{:<30}'.format(name)
	final = temp1 + temp2 + comment + '\n'
	return final


def sort_into_list(line):
	ip, name, code = get_device_info(line)
	name_seg = name.split('-')
	if 'ERROR' in ip:
		raw_list.append(format_raw(ip, name, 'Does Not Exist?'))
	elif name_seg[0] == site_code:
		if name_seg[2] in ['cvg', 'ipt']:
			voice_list.append(ip + '/32')
			raw_list.append(format_raw(ip, name, 'voice'))
		elif name_seg[2] in 'ons':
			ons_list.append(ip + '/32')
			raw_list.append(format_raw(ip, name, 'ons'))			
		elif name_seg[2] in 'ucs':
			ucs_list.append(ip + '/32')
			raw_list.append(format_raw(ip, name, 'ucs'))
		elif 'wifi' in name_seg[2] or 'wism' in name_seg[2]:
			wifi_list.append(ip + '/32')
			raw_list.append(format_raw(ip, name, 'wifi'))
		else:
			data_list.append(ip + '/32')
			raw_list.append(format_raw(ip, name, 'data'))
	else:
		raw_list.append(format_raw(ip, name, 'Invalid Formatting'))
			

def output_ACS_format(out_file, ip_list, list_name):
	out_file.write('\n%s - %i hosts\n\n' % (list_name, len(ip_list)))
	out_file.write(';'.join(ip_list))
	out_file.write('\n\n')


# Creates list of DNS names / IP Addresses from Cisco-Works exported CSV
with open(fname,'r') as f:
	devices = [line.lower().split(',') for line in f]

#Sorts names-to-be-resolved and IP addresses into respective lists
for line in devices:
	a = ip_prefix_data in line[0]
	b = ip_prefix_voice in line[0]
	c = (site_code + '-') in line[0][:len(site_code) + 1]
	d = site_code == line[-1].strip()
	if a or b or c or d:
		sort_into_list(line)

#Writes out the IP addresses in the proper format for importing into ACS
with open(site_code + '.txt', 'w') as f:
	if len(data_list) > 0: output_ACS_format(f, data_list, 'Data')
	if len(voice_list) > 0: output_ACS_format(f, voice_list, 'Voice')
	if len(ucs_list) > 0: output_ACS_format(f, ucs_list, 'UCS')
	if len(ons_list) > 0: output_ACS_format(f, ons_list, 'ONS')
	if len(wifi_list) > 0: output_ACS_format(f, wifi_list, 'Wireless')
	f.write('\n\n\n\nRaw Device List from source - %i hosts\n\n' % len(raw_list))
	for d in raw_list:
		f.write(d)
