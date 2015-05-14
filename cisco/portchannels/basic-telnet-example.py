import telnetlib,getpass

host = 'tis-sw-acc-1lab-1'

username = input('Username: ')
username = bytes(username + '\n', 'UTF8')
password = getpass.getpass()
password = bytes(password + '\n', 'UTF8')
enablepw = getpass.getpass()
enablepw = bytes(enablepw + '\n', 'UTF8')

session = telnetlib.Telnet()
session.open(host)

output = session.read_until(b'Username:',2)
print(output)
session.write(username)

output = session.read_until(b'Password:',2)
print(output)
session.write(password)

output = session.read_until(b'>',2)
print(output)
session.write(b'terminal length 0\n')

output = session.read_until(b'>',2)
print(output)
session.write(b'show vlan\n')

b_vlans = session.read_until(b'>',2)
session.write(b'exit\n')
session.close()

vlans = b_vlans.decode().split('\r\n')




