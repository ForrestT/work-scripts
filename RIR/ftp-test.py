from ftplib import FTP

ftp = FTP('ftp.arin.net')
ftp.login()
ftp.cwd('pub/stats/arin')
ftp.retrbinary('RETR delegated-arin-latest', open('c:\\ftproot\\RIR\\arin-latest.txt', 'wb').write)
ftp.quit()
