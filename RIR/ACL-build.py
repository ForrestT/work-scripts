#Forrest Throesch	2013/02/08
#
#Joke script that downloads the latest available RIR doc from ARIN,
#parses it for US networks, and builds a huge ACL in a text file.
#
#Eventually could add functionality to telnet/ssh to device and
#add/replace the ACL each time script is run. But since this is 
#such a terrible idea in the first place, that will likely not be
#added. It may be fun, however...

from math import log
slash32 = 2**32 - 1
oct1 = 0b11111111 << 24
oct2 = 0b11111111 << 16
oct3 = 0b11111111 << 8
oct4 = 0b11111111

def get_latest_arin(outfile):
	"""downloads the latest RIR from ARIN's public FTP repo.
	downloads to location specified via arg"""
	from ftplib import FTP
	ftp = FTP('ftp.arin.net')
	ftp.login()
	ftp.cwd('pub/stats/arin')
	ftp.retrbinary('RETR delegated-arin-latest', open(outfile, 'wb').write)
	ftp.quit()

def build_block_list(file):
	"""builds a list of tuples from RIR doc. Pulls the needed fields
	from only lines containing US ipv4 networks. Tuples are of format:
	['ip address','number of IP addresses in network']"""
	f = open(filename, 'r')
	list = [line.split('|')[3:5] for line in f if 'US|ipv4' in line]
	f.close()
	return list

def get_mask(netmask):
	"""Given a subnet mask in RIR form (num of ip addresses in net),
	returns subnet mask in 255.255.0.0 form"""
	mask_bin = slash32 ^ (int(netmask) - 1)
	mask_str = "%i.%i.%i.%i" % ((mask_bin & oct1) >> 24, 
								(mask_bin & oct2) >> 16, 
								(mask_bin & oct3) >> 8, 
								mask_bin & oct4)
	return mask_str

def ip_to_bin(net):
	"""converts IP address to integer/binary and returns value"""
	t = [int(x) for x in net.split('.')]
	return ((t[0]<<24) + (t[1]<<16) + (t[2]<<8) + t[3])

def can_summarize(net1,net2):
	"""Evaluates whether or not the current network and the next network
	in the list are able to be summarized."""
	na1, na2 = ip_to_bin(net1[0]), ip_to_bin(net2[0])
	if log(float(net1[1]),2) % 1 == 0:
		sm1, sm2 = (int(net1[1])*2 - 1) ^ slash32, (int(net2[1])*2 - 1) ^ slash32
		if na1 & sm1 == na2 & sm1 and sm1 == sm2: return True
	else: return False

def summarize_block_list(blocks):
	"""Loops through block list summarizing any networks that eval TRUE 
	from the can_summarize() function. Continues to loop until one full
	loop is completed without a single summarization.
	Outputs status of each loop to console."""
	print len(blocks), ' starting subnets'
	while True:
		i = 0
		count = 0
		while True:
			if i >= len(blocks) - 1: break
			if can_summarize(blocks[i],blocks[i+1]):
				blocks[i][1] = str(int(blocks[i][1]) * 2)
				del blocks[i+1]
				count += 1
			i += 1
		print count, ' summarizations'
		print len(blocks), ' subnets left'
		if count == 0: break
		
def format_acl(block_list):
	""" creates Cisco extended ACL from ARIN network list
		ip access-list extended Permit_US
			permit ip 10.0.0.0 255.0.0.0 host 167.73.100.100"""
	acl = ['ip access-list extended Permit_US_Networks\n']
	for line in block_list:
		netmask = get_mask(line[1])
		rule = '\tpermit ip %s %s host 167.73.110.51\n' % (line[0],netmask)
		acl.append(rule)
	return acl

def write_acl(acl,outfile):
	"""Writes ACL out to text file"""
	f = open(outfile, 'w')
	for line in acl:
		f.write(line)
	f.close()

filename = 'C:\\ftproot\\RIR\\arin-latest.txt'
# get_latest_arin(filename)	#comment out if only testing the ACL build
block_list = build_block_list(filename)
summarize_block_list(block_list)
acl = format_acl(block_list)
write_acl(acl, 'C:\\ftproot\\RIR\\US-only-acl-bin.txt')