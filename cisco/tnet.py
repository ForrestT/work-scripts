import telnetlib, socket

class Tnet:

	def __init__(self,username,password,enablepw):
		self.session = telnetlib.Telnet()
		self.username = username	
		self.password = password
		self.enablepw = enablepw
			
	def run_command(self, command, end_char='#', wait_time=2):
		b_command = bytes(command + '\n', 'UTF8')
		b_end_char = bytes(end_char, 'UTF8')
		self.session.write(b_command)
		result = self.session.read_until(b_end_char, wait_time)
		return result.decode().split('\r\n')

	def __authenticate(self):
		try:
			self.session.read_until(b'Username:', 2)
			self.run_command(self.username, 'Password:')
			self.run_command(self.password, '>')
			self.run_command('enable', 'Password:')
			self.run_command(self.enablepw,)
			self.run_command('terminal length 0',)
		except:
			raise

	def login(self, hostname):
		try:
			self.session.open(hostname)
		except socket.gaierror:
			print("\nERROR: Could not resolve Host.\n")
		except socket.error:
			print("\nERROR: Host failed to respond.\n")
		self.__authenticate()

	def logout(self):
		self.session.write(b'exit\n')
		self.session.close()		
