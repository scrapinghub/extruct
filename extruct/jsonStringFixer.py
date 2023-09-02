def addMissingQuotesInJsonString(s):

	s = s.split("\n")
	finalstring=''
	for i in range(len(s)):
		s1 = s[i]
		s2 = ''
		startflag=0
		j=0
		while j<len(s1):
			if startflag==0:
				while True:
					if j==len(s1):
						break
					if (ord(s1[j])>=48 and ord(s1[j])<=57) or (ord(s1[j])>=65 and ord(s1[j])<=90) or (ord(s1[j])>=97 and ord(s1[j])<=122):
						s2=s2+'"'+s1[j]
						j=j+1
						startflag=1
						break
					elif s1[j]=='"':
						s2=s2+s1[j]
						j=j+1
						startflag=1
						break
					else:
						s2=s2+s1[j]
						j=j+1


			elif startflag==1:
				while True:
					if j==len(s1):
						s2=s2+'"'
						startflag=0
						break
					if s1[j]=="]" or s1[j]==";" or s1[j]=="," or (s1[j]==":" and s1[j+1]!="/") or s1[j]=="}" :
						s2=s2+'"'+s1[j]
						j=j+1
						startflag=0
						break
					elif s1[j]=='"':
						s2=s2+s1[j]
						j=j+1
						startflag=0
						break
					else:
						s2=s2+s1[j]
						j=j+1
		if startflag==1 and j==len(s1):
			s2=s2+'"'
			startflag=0

		finalstring = finalstring + s2 +'\n'

	s = finalstring.split("\n")
	finalstring=''
	for i in range(len(s)):
		s1 = s[i]
		s2 = ''
		colonflag=0
		j=0
		while j<len(s1):
			if colonflag==0:
				while True:
					if j==len(s1):
						break
					elif s1[j]==":":
						s2=s2+s1[j]
						j=j+1
						colonflag=1
						break
					else:
						s2=s2+s1[j]
						j=j+1


			elif colonflag==1:
				while True:
					if j==len(s1):
						s2 =s2+'null'
						colonflag=0
						break
					if s1[j]=="]" or s1[j]==";" or s1[j]=="," :
						s2=s2+'null'+s1[j]
						j=j+1
						colonflag=0
						break
					elif s1[j]!=" ":
						s2=s2+s1[j]
						j=j+1
						colonflag=0
						break
					else:
						s2=s2+s1[j]
						j=j+1
		if colonflag==1 and j==len(s1):
			s2 =s2+'null'
			colonflag=0

		finalstring = finalstring + s2 +'\n'
	return finalstring