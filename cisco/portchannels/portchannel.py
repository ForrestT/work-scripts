import argparse,getpass
from tnet import Tnet

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--switches', help='file containing list of switches')
parser.add_argument('-o', '--output', help='file to output logging info')
parser.add_argument('-t', '--template', help='specify template file with variable definitions')
parser.add_argument('-w', '--writemode', help='will NOT write changes to switches without this option', action='store_true')
args = parser.parse_args()

if args.switches:
	with open(args.switches) as f:
		switches = [line.strip() for line in f.readlines()]
	if switches[-1] == '':
		switches.pop(-1)
else:
	print('No list of switches provided, see -s, --switches option\n')
	switches = []

if args.output:
	output_file = args.output
else:
	output_file = 'python-script-output.txt'


def check_for_portchannel(port_channels):
	for line in port_channels:
		if 'Po1' in line:
			return False
	return True

def build_portchannel(vlans):
	native, data, voice = '', '', ''
	for line in vlans:
		if 'native' in line.lower():
			native = line.split()[0]
		if 'data' in line.lower():
			data = line.split()[0]
		if 'voice' in line.lower():
			voice = line.split()[0]
			break
	po_config = ['int po1',
				'desc to bl-sw-dist-vss-1',
				'switchport trunk encapsulation dot1q',
				'switchport trunk native vlan {N}'.format(N=native),
				'switchport trunk allowed vlan {D},{V}'.format(D=data,V=voice),
				'switchport mode trunk']
	return po_config

def check_for_uplinks(cdp):
	primary, secondary = '', ''
	for line in cdp:
		if 'HC-SW-DIST-A844-1' in line:
			i = cdp.index(line)
			primary = cdp[i+1].split()[1]
		elif 'HC-SW-DIST-1081-1' in line:
			i = cdp.index(line)
			secondary = cdp[i+1].split()[1]
	return primary, secondary

def build_EEM_script(primary, secondary):
	if primary == '':
		pri_EEM = 'No Primary Uplink found, No Primary EEM script generated'
	else:
		pri_EEM = ['event manager applet MovePrimary',
				'event syslog pattern "%LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet{}, changed state to down"'.format(primary),
				'action 1.0 cli command "enable"',
				'action 2.0 cli command "conf t"',
				'action 3.0 cli command "interface Gi{}"'.format(primary),
				'action 4.0 cli command "channel-group 1 mode active"',
				'action 5.0 cli command "no shut"',
				'action 6.0 cli command "end"']
	if secondary == '':
		sec_EEM = 'No Secondary Uplink found, No Secondary EEM script generated'
	else:
		sec_EEM = ['event manager applet MoveSecondary',
				'event syslog pattern "%LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet{}, changed state to down"'.format(secondary),
				'action 1.0 cli command "enable"',
				'action 2.0 cli command "conf t"',
				'action 3.0 cli command "interface Gi{}"'.format(secondary),
				'action 4.0 cli command "channel-group 1 mode active"',
				'action 5.0 cli command "no shut"',
				'action 6.0 cli command "end"']
	return pri_EEM, sec_EEM

def output_config_segment(conf_header, conf_seg, filename):
	filename.write('\t' + conf_header + '\n')
	for line in conf_seg:
		filename.write('\t\t'+line+'\n')
	filename.write('\n')

def output_to_testrun_file(device, filename, po_config='', pri_EEM='', sec_EEM=''):
	filename.write('\n{}\n'.format(device))
	output_config_segment('Port-Channel Config', po_config, filename)
	output_config_segment('Primary EEM Script', pri_EEM, filename)
	output_config_segment('Secondary EEM Script', sec_EEM, filename)
	filename.write('\n\n\n\n')
	
def write_command_block(session, commands):
	results = []
	results.append(session.run_command('conf t'))
	for command in commands:
		output = session.run_command(command)
		results.append(output)
	results.append(session.run_command('exit'))
	return results

def update_writelog(writelog, command_logs):
	for log in command_logs:
		for line in log:
			writelog.append(line)


if not args.writemode:
	testrun_file = open('testrun-output.txt', 'w')

username = input('Username: ')
password = getpass.getpass()
enablepw = getpass.getpass('Enable: ')
session = Tnet(username, password, enablepw)

for switch in switches:
	print('\nLogging onto: {S}'.format(S=switch))
	session.login(switch)
	# print('\tGetting CDP neighbors')
	# cdp = session.run_command('show cdp neighbors')
	print('\tGetting VLANS')
	vlans = session.run_command('show vlan')
	print('\tGetting Port-Channels')
	port_channels = session.run_command('show etherchannel summary')
	if check_for_portchannel(port_channels):
		po_config = build_portchannel(vlans)
		# primary, secondary = check_for_uplinks(cdp)
		# pri_EEM, sec_EEM = build_EEM_script(primary, secondary)
	else:
		po_config = ['Po1 already exists. No Port-Channel config generated']
		# pri_EEM = ['Unable to create Port-Channel. No Primary EEM script generated']
		# sec_EEM = ['Unable to create Port-Channel. No Secondary EEM script generated']
	if args.writemode:
		writelog = []
		#update_writelog(writelog, session.run_command('conf t'))
		update_writelog(writelog, write_command_block(session, po_config))
		# update_writelog(writelog, write_command_block(session, pri_EEM))
		# update_writelog(writelog, write_command_block(session, sec_EEM))
		#update_writelog(writelog, session.run_command('end'))
		with open(switch + '-writelog.txt','w') as f:
			for line in writelog:
				f.write(line+'\n')
	else:
		print('\nWriting results of test run to file: testrun-output.txt')
		output_to_testrun_file(switch, testrun_file, po_config)
	# print('\n\tGetting running configuration\n')
	# running_config = session.run_command('show run', wait_time=10)
	# filename = switch + '-output.txt'
	# print('\n\tWriting file: {F}\n'.format(F=filename))
	# with open(filename, 'w') as f:
	# 	for command in [cdp, vlans, running_config]:
	# 		f.write('\n\n\n')
	# 		for line in command:
	# 			f.write(line + '\n')
	# print('\n\t{F} created successfully\n'.format(F=filename))
	session.logout()

if not args.writemode:
	testrun_file.close()

