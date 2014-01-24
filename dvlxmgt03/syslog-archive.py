import os, datetime

syslog_root = '/var/log/asa'
today = datetime.date.today().strftime('%Y%m%d')

def get_dirs_and_files(path):
	d = []
	f = []
	for (dirpath, dirnames, filenames) in os.walk(path):
		d.extend(dirnames)
		f.extend(filenames)
		break
	return d,f

def move_file(path,dir,file):
	src = '%s/%s' % (path, file)
	dst = '%s/%s/%s' % (path, dir, file)
	os.rename(src, dst)

def archive_old_files(files,dirs):
	for dir in dirs:
		for file in files:
			if file[-12:-4] == today:
				continue
			elif dir == file[:-13]:
				move_file(syslog_root, dir, file)

dirs, files = get_dirs_and_files(syslog_root)
archive_old_files(files, dirs)
