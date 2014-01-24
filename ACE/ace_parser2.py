import re

class Ace_Parser:

	def __init__(self,vip,config):
		self.vip = vip
		self.config = config

	def find_line(self, search_str, cfg, opt_str=' '):
		for line in cfg:
			if (search_str in line) and (opt_str in line):
				return cfg.index(line)

	def get_section(self, start, end, cfg, line):
		section_found = False
		temp_cfg = []
		while section_found is False:
			if start in cfg[line]:
				temp_cfg.append(cfg[line])
				line += 1
				while section_found is False:
					if end in cfg[line] or start in cfg[line]:
						section_found = True
					else:
						temp_cfg.append(cfg[line])
						line += 1
			else:
				line += -1
		return temp_cfg
	
	def get_vip_config(self):
		mastercfg = [] #Ultimate cfg to be output
		last_word = re.compile('\s[^\s]+\n')

		# Get the class-map
		line_number = self.find_line(self.vip, self.config)
		cfg_class_map = self.get_section('class-map', 'policy-map', self.config, line_number)
		mastercfg.append(cfg_class_map)

		# Extract the class name from class-map, Get the VIP-POLICY class
		temp = last_word.search(cfg_class_map[0])
		name_class = temp.group(0)
		line_number = self.find_line(name_class, self.config, 'class ')
		cfg_class = self.get_section('class ', 'interface', self.config, line_number)
		mastercfg.append(cfg_class)

		# Extract Policy name from class, Get the policy-map
		line_number = self.find_line('loadbalance policy ', cfg_class)
		temp = last_word.search(cfg_class[line_number])
		name_policy_map = temp.group(0)
		line_number = self.find_line(name_policy_map, self.config, 'policy-map ')
		cfg_policy_map = self.get_section('policy-map ', 'multi-match', self.config, line_number)
		mastercfg.append(cfg_policy_map)

		# Extract serverfarm name from policy-map, Get the serverfarm config
		line_number = self.find_line('serverfarm ', cfg_policy_map)
		temp = last_word.search(cfg_policy_map[line_number])
		name_serverfarm = temp.group(0)
		line_number = self.find_line(name_serverfarm, self.config, 'serverfarm host ')
		cfg_serverfarm = self.get_section('serverfarm host', 'ssl-proxy', self.config, line_number)
		mastercfg.append(cfg_serverfarm)

		# Extract the probes and rservers from the serverfarm config
		cfg_probe = []
		cfg_rserver = []
		for line in cfg_serverfarm:
			if 'probe' in line:
				temp = last_word.search(line)
				cfg_probe.append(temp.group(0))
			elif ' rserver' in line:
				temp = last_word.search(line)
				cfg_rserver.append(temp.group(0))

		# Get the probe configs
		for probe in cfg_probe:
			line_number = self.find_line(probe, self.config, 'probe')
			cfg_probe_configs = []
			tempcfg = self.get_section('probe', 'parameter-map', self.config, line_number)
			for line in tempcfg:
				cfg_probe_configs.append(line)
		mastercfg.append(cfg_probe_configs)
			
		# Get the rserver configs
		for rserver in cfg_rserver:
			line_number = self.find_line(rserver, self.config, 'rserver ')
			cfg_rserver_configs = []
			tempcfg = self.get_section('rserver ', 'action-list', self.config, line_number)
			for line in tempcfg:
				cfg_rserver_configs.append(line)
		mastercfg.append(cfg_rserver_configs)

		# Output all cfgs/configs
		return mastercfg
