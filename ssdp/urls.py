import requests

def get_xml(url):
	xml = requests.get(url)
	#xml = xml.text.split('\n')
	return xml

def get_uniques(l_raw):
	uniques = []
	for l in l_raw:
		if l in uniques:
			continue
		else:
			uniques.append(l)
	return uniques

s_InputFile = 'ssdp-list2.txt'
with open(s_InputFile) as f:
	l_ssdp = [line[10:].strip() for line in f if 'LOCATION: ' in line]
l_ssdp = get_uniques(l_ssdp)

with open('ssdp-xml-list.log', 'w') as f:
	count = 1
	total = len(l_ssdp)
	print '\nFound %i unique URLs to process\n' % total
	for url in l_ssdp:
		print 'Fetching URL %i of %i: %s\n' % (count, total, url)
		try:
			xml = get_xml(url)
		except:
			print 'Failed to get URL: %s\n' % url
		else:
			print '%s Retrieved, writing to file.\n' % url
			f.write(url + '\n')
			f.write(xml.text)
			f.write('\n\n\n')

print 'All %i URLs in %s have been processed.\n' % (total, s_InputFile)