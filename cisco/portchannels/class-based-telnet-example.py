import telnetlib,getpass
from tnet import Tnet

hostname = 'tis-sw-acc-1lab-1'
username = input('Username: ')
password = getpass.getpass()
enablepw = getpass.getpass()

session = Tnet(username, password, enablepw)
session.login(hostname)

vlans = session.run_command('show vlan')
running_config = session.run_command('show run', wait_time=10)
cdp = session.run_command('show cdp neighbors')

with open('test.txt', 'w') as f:
	for block in [vlans, cdp, running_config]:
		f.write('\n\n\n\n')
		for line in block:
			f.write(line + '\n')

