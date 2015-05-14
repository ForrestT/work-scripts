from scapy.all import *

capture = rdpcap('/home/forrest/ssdp-responses.pcap')
f = open('/home/forrest/ssdp-summary.csv', 'w')
ip_list = []
f.write('SRC_IP,LOCATION,SERVER,USN\n')

for packet in capture:
  src_IP = packet[IP].src
  if src_IP in ip_list:
  	continue
  else:
  	ip_list.append(src_IP)
  temp = packet[Raw].load.split('\r\n')
  for t in temp:
  	if 'LOCATION: ' in t[:10]:		
  		location = t[10:]
  	elif 'SERVER: ' in t[:8]:	
  		server = t[8:].replace(',','')
  	elif 'USN: ' in t[:5]:
  		usn = t[5:].replace(',','')
  temp = '%s,%s,%s,%s\n' % (src_IP, location, server, usn)
  f.write(temp)
f.close()
