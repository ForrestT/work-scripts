class ACE:

	def __getConfig(self,config_file):
		with open(config_file) as f:
			config = [line.rstrip() for line in f.readlines()]
		return config


	def __getIndexes(self,keyword):
		indexes = []
		for line in self.config:
			if line[:len(keyword)] == keyword:
				indexes.append(self.config.index(line))
		indexes.append(self.config.index('',indexes[-1]))
		return indexes


	def __getSection(self,keyword):
		section = {}
		indexes = self.__getIndexes(keyword)
		for i in range(0,len(indexes) - 1):
			subSectionName = self.config[indexes[i]].split(' ')[-1]
			subSectionConfig = [line for line in self.config[indexes[i]:indexes[i+1]]]
			section[subSectionName] = subSectionConfig
		return section
	

	def __getSubIndexes(self,keyword,config):
		indexes = []
		for line in config:
			if line[:len(keyword)] == keyword:
				indexes.append(config.index(line))
		indexes.append(config.index('',indexes[-1]))
		return indexes


	def __getSubSection(self,sectionTitle,keyword):
		sectionStart = self.config.index(sectionTitle)
		sectionEnd = self.config.index('',sectionStart) + 1
		subSection = self.config[sectionStart:sectionEnd]
		section = {}
		indexes = self.__getSubIndexes(keyword,subSection)
		for i in range(0,len(indexes) - 1):
			subSectionName = subSection[indexes[i]].split(' ')[-1]
			subSectionConfig = [line for line in subSection[indexes[i]:indexes[i+1]]]
			section[subSectionName] = subSectionConfig
		return section


	def __separateFarms(self,farms):
		stickygroups = []
		serverfarms = []
		for farm in farms:
			if farm[-5:] == 'GROUP':
				stickygroups.append(farm)
			elif farm[-4:] == 'FARM':
				serverfarms.append(farm)
		return stickygroups,serverfarms


	def __buildVIPconfigAndGetNext(self,section,keywords,goalword):
			nextKeywords = []
			for key in section:
				for line in section[key]:
					for keyword in keywords:
						if keyword in line:
							for line in section[key]:
								self.vipConfig.append(line)
								if goalword in line:
									words = line.split(' ')
									nextKeywords.append(words[-1])
									if words[-2] == 'backup':
										nextKeywords.append(words[-3])
			return nextKeywords


	def __buildVIPconfig(self,section,keywords):
		for key in section:
			for line in section[key]:
				for keyword in keywords:
					if keyword in line:
						for line in section[key]:
							self.vipConfig.append(line)



	def getVIPconfig(self,vip):
		self.vip = vip
		self.vipConfig = []
		#Use IP address to find class-map names, 'class-map match-any XXXXX-VIP'
		namesOfClassmaps = self.__buildVIPconfigAndGetNext(self.classmaps,[vip],'class-map')
		#Use class-map names to find policy-map names, '    loadbalance policy XXXXX-POLICY'
		self.vipConfig.append('policy-map multi-match VIP-POLICY')
		namesOfPolicymaps = self.__buildVIPconfigAndGetNext(self.vippolicy,namesOfClassmaps,'loadbalance policy')
		#Use policy-map names to find serverfarm names, '    serverfarm XXXXX-FARM'
		# or to find sticky-group names, 				'    sticky-serverfarm XXXXX-GROUP'
		namesOfFarms = self.__buildVIPconfigAndGetNext(self.policymaps,namesOfPolicymaps,'serverfarm')
		namesOfStickygroups, namesOfServerfarms = self.__separateFarms(namesOfFarms)
		#Use any sticky-groups to find more serverfarms, '  serverfarm XXXXX-FARM'
		additionalServerfarms = self.__buildVIPconfigAndGetNext(self.stickygroups,namesOfStickygroups,'serverfarm')
		namesOfServerfarms += additionalServerfarms
		#Use serverfarm names to find rserver names, 	'  rserver XXXXX-SERVERNAME'
		#and to find probe names,						'  proe PROBENAME'
		namesOfRservers = self.__buildVIPconfigAndGetNext(self.serverfarms,namesOfServerfarms,'rserver')
		namesOfProbes = self.__buildVIPconfigAndGetNext(self.serverfarms,namesOfServerfarms,'probe')
		#Use rserver names to get all rservers
		self.__buildVIPconfig(self.rservers,namesOfRservers)
		#Use probe names to get all probes
		self.__buildVIPconfig(self.probes,namesOfProbes)


	def displayVIP(self):
		print(self.vip)
		for line in self.vipConfig:
			print(line)


	def __init__(self,config_file):
		self.vip = ''
		self.vipConfig = []
		with open(config_file) as f:
			self.config = self.__getConfig(config_file)
		self.probes = self.__getSection('probe')
		self.rservers = self.__getSection('rserver')
		self.serverfarms = self.__getSection('serverfarm')
		self.parametermaps = self.__getSection('parameter-map')
		self.stickygroups = self.__getSection('sticky')
		self.sslproxies = self.__getSection('ssl-proxy')
		self.classmaps = self.__getSection('class-map')
		self.policymaps = self.__getSection('policy-map type loadbalance')
		self.interfaces = self.__getSection('interface')
		self.domains = self.__getSection('domain')
		self.vippolicy = self.__getSubSection('policy-map multi-match VIP-POLICY','  class')
