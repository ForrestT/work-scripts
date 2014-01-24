import os, datetime, bz2
from shutil import copyfileobj

syslog_root = '/var/log/asa'
age_cutoff = 5

def get_dirs_and_files(path):
	d = []
	f = []
	for (dirpath, dirnames, filenames) in os.walk(path):
		d.extend(dirnames)
		f.extend(filenames)
		break
	return d,f

def get_date_last_modified(filepath):
	fstat = os.stat(filepath)
	return datetime.date.fromtimestamp(fstat.st_mtime)

def is_older_than_cutoff(fdate, age_cutoff):
	return fdate + datetime.timedelta(days=age_cutoff) < datetime.date.today()

def compress_bz2(filepath):
	with open(filepath, 'rb') as infile:
		with bz2.BZ2File(filepath + '.bz2', 'wb') as outfile:
				copyfileobj(infile,outfile)



os.chdir(syslog_root)
dirs,_ = get_dirs_and_files(os.getcwd())

for d in dirs:
	os.chdir(d)
	_,files = get_dirs_and_files(os.getcwd())
	for f in files:
		if f[-4:] != '.bz2':
			fdate = get_date_last_modified(f)
			if is_older_than_cutoff(fdate, age_cutoff):
				#compress_bz2(f)
				print 'creating %s.bz2' % f
				#os.remove(f)
				print 'removing %s' % f
	os.chdir(syslog_root)
