import telnetlib, getpass, socket

class Tnet:
	def __init__(self):
		self.session = telnetlib.Telnet()
		self.t = 'test'

	def login(self, hostname):
		try:
			self.session.open(hostname)
		except socket.gaierror:
			print "\nERROR: Could not resolve Host.\n"
		except socket.error:
			print "\nERROR: Host failed to respond.\n"

	def fill_field(self, input_value, expected):
		self.session.write(input_value + '\n')
		prompt = self.session.read_until(expected, 2)
		if expected in prompt:
			return [True, prompt]
		else:
			return [False, prompt]

	def show_command(self, command):
		self.session.write(command)
		finished, output = 0, ''
		while finished == 0:
			output = output + self.session.read_until('--More--',3)
			if '--More--' in output[-20:]:
				self.session.write(' ')
			else:
				finished = 1
		return output
			
	def authenticate(self):
		authcheck = True
		prompt = self.session.read_until(':', 2)
		if ('Username:' in prompt) or ('login:' in prompt):
			authcheck, prompt = self.fill_field(raw_input('username: '), 'Password:')
		if ('Password:' in prompt) and authcheck: 
			authcheck, prompt = self.fill_field(getpass.getpass(), '>')
		if ('>' in prompt) and authcheck:
			self.session.write('en\n')
			authcheck, prompt = self.fill_field(getpass.getpass(), '#')
		if '#' in prompt:
			return True
		return False

	def logout(self):
		self.session.write('exit\n')
		self.session.close()		
