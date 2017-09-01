from django.db import models
from clubSetup.models import *
from datetime import datetime
import pickle as f
import csv


# Create your models here.

def updateStudentClubs(club,studRecord):
	
	stud = studRecord.student
	path = stud.clubFile.name
	clubList = {}
	fp = openFile(path,"","rb")
	#Read list of student clubs
	try:
		clubList = f.load(fp)
	except:
		pass
		
	#If the club is present overwrite dictionary data with new studRecord
	clubList[club.pk] = studRecord
	
	fp.close()
	
	#Rewrite List to file
	fp = openFile(path,"","wb")

	f.dump(clubList,fp,-1)
	

def updateMemberList(club,path,masterFileName,memberFileName):
	studRecordList = []
	memberList = []
	#Gets records on club master list
	studRecordList = readMasterFile(path,masterFileName)
	
	currentYear = getCurrentAcademicYear()
	
	attendanceRequirement = currentYear.getAttendanceRequirement()
	numberOfMeetings = club.countDates()
	minAttendance = attendanceRequirement * numberOfMeetings
	
	#If student meets attendance requirement add to membership file
	
	for studRecord in studRecordList:
		if studRecord.attendance >= minAttendance:
			memberList.append(studRecord)
			updateStudentClubs(club,studRecord)
			
	#Rewrite member file
	fp = openFile(path,memberFileName,"wb")
	for member in memberList:
		f.dump(member,fp,-1)
		
	fp.close()
	
	#Update The Student Club Membership List
	
	updateStudentMembership()
	
def openStudentMembershipFile():
	
	#Make filename for csv
	currentTerm = Term.objects.get(isCurrentTerm=True)
	year = getCurrentAcademicYear()
	fileName = "membershiplist" + currentTerm.name + str(year) + ".csv"
	
	#check if file exists
	fp = openFile(membershipStorage.location,fileName,"w")
	
	#Create csv file if it does not exist
	if fp==None:
		createFolderByPath(membershipStorage.location,"")
		
		#writeStudentsToCSV(fp)
		
		fp = openFile(membershipStorage.location,fileName,"w")
	
	
	return fp
	
def writeStudentsToCSV(fp):
	
	fieldnames = ['First Name','Last Name','Form','Clubs']

	writer = csv.DictWriter(fp,fieldnames = fieldnames,delimiter=",",lineterminator = '\n')
	writer.writeheader()
	
	studList = Student.objects.all()
	
	for stud in studList:
		writer.writerow({'First Name':stud.firstName,'Last Name':stud.lastName,'Form':stud.form})

def getStudentClubList(stud):
	fp = openFile(stud.clubFile.name,"","rb")
	clubDict = None
	
	try:
		clubDict = f.load(fp)
	except:
		pass
		
	if clubDict == None:
		return ""
	else:
		clubList = ""
		for key in clubDict:
			clubList+= Club.objects.get(pk=key).name + ", "

	return clubList
	
def updateStudentMembership():
	#Create csv file if it does not exist
	fp = openStudentMembershipFile()
	
	
	#Get the List of students
	studList = Student.objects.all()
	
	#Get list of clubs for each student
	fieldnames = ['First Name','Last Name','Form','Clubs']
	writer = csv.DictWriter(fp,fieldnames = fieldnames,delimiter=",",lineterminator = '\n')
	writer.writeheader()
	
	for stud in studList:
		clubList = getStudentClubList(stud)
		writer.writerow({'First Name':stud.firstName,'Last Name':stud.lastName,'Form':stud.form,"Clubs":clubList})
	path = fp.name
	fp.close()
	return path

def updateAvailableDate(club):
	updatedDateList = []
	
	#Updates the available dates for a club by comparing it to the current date
	#And dates which already exist
	path = os.path.join(clubInfoStorage.location,"%s" % club.name,"attendance/dates")
	fp = openFile(path,"available.df","wb")
	dateList = club.getDates()
	now = datetime.now().date()
	
	for date in dateList:
		if date<now and readDateData(club,date)==None:
			f.dump(date,fp,-1)
		
	
def readAvailableDate(club):
	#Read available dates from available.df
	dateList = []
	path = os.path.join(clubInfoStorage.location,"%s" % club.name,"attendance/dates")
	fp = openFile(path,"available.df","rb")
	
	try:
		while(1):
			dateList.append(f.load(fp))
	except:
		pass
		
	return dateList

def readDateData(club,date):
	#Read dates from the dates.df
	studList = []
	path = os.path.join(clubInfoStorage.location,"%s" % club.name,"attendance/dates")
	fp = openFile(path,(str(date) + ".df"),"rb")
	if fp==None:
		return None
	try:
		while(1):
			studList.append(f.load(fp))
	except:
		return studList
			



def writeDateData(club,date,studRecordList):
	#Writes all students who attended on a particular date to the respective df file
	path = os.path.join(clubInfoStorage.location,"%s" % club.name,"attendance/dates")
	fp = openFile(path,(str(date.date()) + ".df"),"wb")
	for stud in studRecordList:
		f.dump(stud,fp,-1)
	
def searchObjectList(instance,objectList):
	
	#Searches for object in list of object and returns index
	i = 0
	
	try:
		while(1):
			if(instance.pk == objectList[i].student.pk):
				return i
			else:
				i+=1
	except:
		return -1 #Object has not been found
	
def readMasterFile(path,fileName):
	fp = openFile(path,fileName,"rb")
	
	studRecordList = []

	try:
		
		while (1):
			
			studRecordList.append(f.load(fp))
					
	except EOFError:
		fp.close()
		return studRecordList	

def addToMaster(path,fileName,club,studDataList):
	#Adds students to the masterlist and updates their criteria on masterlist
	fp = openFile(path,fileName,"rb")
	
	studRecordList = []

	try:
		
		while (1):
			
			studRecordList.append(f.load(fp))
					
	except EOFError:
		
		fp.close()
		fp = openFile(path,fileName,"wb")
		
		
		for stud in studRecordList:
			print(stud.student.firstName)
				
		
		for studData in studDataList:
			
			i = searchObjectList(studData[0],studRecordList)
			print(studData[0].firstName + " " +str(i))
			if i != -1:
				studRecordList[i].incrementAttendance()
				studRecordList[i].updateCriteria(club,studData[1])
				print(studRecordList[i].student.firstName + " " + str(studRecordList[i].attendance))
			else:
 
				studRecordList.append(clubRecord(student = studData[0]))
				i = searchObjectList(studData[0],studRecordList)
				studRecordList[i].incrementAttendance()
				studRecordList[i].updateCriteria(club,studData[1])
				print("NEW!")
				print(studRecordList[i].student.firstName + " " + str(studRecordList[i].attendance))
				
				
	for stud in studRecordList:
		f.dump(stud,fp,-1)
	
	return studRecordList

class clubRecord(models.Model):
	
	student = models.ForeignKey(Student,on_delete=models.CASCADE)
	attendance = models.IntegerField(default=0)
	dues = models.FloatField(default=0)
	criteria1 = models.CharField(default="",max_length = 250)
	criteria2 = models.CharField(default="",max_length = 250)
	criteria3 = models.CharField(default="",max_length = 250)

	def incrementAttendance(self):
		self.attendance = self.attendance + 1
		print(self.attendance)		
	
	def fixUploadedCriteria(self,uploadedCriteria,criteriaList):
		
		#Due to the fact checkboxes only submit when checked this module
		#Checks all criteria and provides a value.
	
		fixedUploadedCriteriaList=[]
		fixedUploadedCriteriaList.append(uploadedCriteria[0]) #First value is always Dues
		print(uploadedCriteria)
		i=1
		for criteria in criteriaList:
			
			if criteria.htmlType == "checkbox":
				try: #Accounts for when the checkbox is off and so is not in the list.
					if criteria.question == uploadedCriteria[i]:
						fixedUploadedCriteriaList.append("on")
						try: #Checks to see if index is at its maximum value
							i+=1
							test = uploadedCriteria[i]
						except:
							i-=1
					else:
						fixedUploadedCriteriaList.append("off")
						
				except:
					fixedUploadedCriteriaList.append("off")
					
			if criteria.htmlType == "number":
				fixedUploadedCriteriaList.append(uploadedCriteria[i])
				try: #Checks to see if index is at its maximum value
					i+=1
					test = uploadedCriteria[i]
				except:		
					i-=1	
			
					
		return fixedUploadedCriteriaList
				
	
	def updateCriteria(self,club,uploadedCriteria):

		i=0
		#Get list of criteria for the club
		criteriaList = club.getCriteria()
		uploadedCriteria = self.fixUploadedCriteria(uploadedCriteria,criteriaList)
		print(uploadedCriteria)
		#Updates all criteria. Exception handles when less than 3 updates are submitted by the form
		try:
			
			self.handleDues(uploadedCriteria[0])
			#Note that dues is the first item in uploadedCriteria
			for i in range(len(criteriaList)):
				criteriaType = criteriaList[i].criteriaID
				criteriaQuestion = criteriaList[i].question
				print(criteriaType)
				print(criteriaQuestion)
				if criteriaType == 0: #Boolean
					self.handleBoolean(criteriaList[i],uploadedCriteria[i+1],i+1) #Offset by one to account for dues being in the list
					
				if criteriaType == 1: #Number
					self.handleNumber(criteriaList[i],uploadedCriteria[i+1],i+1)
					
						
				if criteriaType == 2: #Accumulator
					self.handleAccumulator(criteriaList[i],uploadedCriteria[i+1],i+1)
					
				
		except:
			pass
		
		
		print("DUES       : " + str(getattr(self,"dues")))
		print("CRITERIA 1 : " + getattr(self,"criteria" + str(1)))
		print("CRITERIA 2 : " + getattr(self,"criteria" + str(2)))
		print("CRITERIA 3 : " + getattr(self,"criteria" + str(3)))
		
		return uploadedCriteria
		
	def convertCurrentValue(self,currentValue,criteria):

		if currentValue == "": 	#is the default of the criteria model. Resets it to the default value set by admin
			currentValue = int(criteria.criteriaDefault)
			
		else: #Translates the current value written as string to integer 
			currentValue = int(currentValue)
		return currentValue

	def handleDues(self,tempUploadedValue):
		#print(uploadedValue)
		#print("Uploaded Dues : ",uploadedValue)
		
		tempcurrentValue = getattr(self,"dues")
		currentValue = float(tempcurrentValue)
		uploadedValue = float(tempUploadedValue)
		updatedValue = currentValue + uploadedValue

		setattr(self,"dues",updatedValue)
		print(getattr(self,"dues"))
		
	def handleNumber(self,criteria,uploadedValue,i):
		
		#Adds the value submitted to the current value
		
		currentValue = getattr(self,"criteria" + str(i))

		currentValue = self.convertCurrentValue(currentValue,criteria)
		
		
		updatedValue = int(currentValue) + int(uploadedValue)

		
		setattr(self,"criteria" + str(i),str(updatedValue))
		
			
		
	def handleAccumulator(self,criteria,uploadedCriteria,i):
		
		#If seleceted will add 1 but if not selected will add 0 to current value of criteria
		
		if uploadedCriteria == "on":
			
			uploadedValue = 1
		
		else:
			uploadedValue = 0
		
		#Gets the current value of the criteria for the student
		currentValue = getattr(self,"criteria" + str(i))
		

		currentValue = self.convertCurrentValue(currentValue,criteria)
		
		updatedValue = currentValue + uploadedValue
				
		setattr(self,"criteria" + str(i),str(updatedValue)) #Sets the new value  
		
			
	
	def handleBoolean(self,criteria,uploadedCriteria,i):
		
		#Sets the boolean value to the value submitted
		print(uploadedCriteria)
		
		if uploadedCriteria == "on":
			
			uploadedValue = True
		
		else:
			
			uploadedValue = False
			
		setattr(self,"criteria" + str(i),str(uploadedValue))
			
def getStudsToday(originalList,allStudentsRegistered):
	
	studsToday=[]
	pkList = []
	for stud in originalList:
		for studentRecord in allStudentsRegistered:
			if stud.pk == studentRecord.student.pk:
				studsToday.append(studentRecord)
				pkList.append(studentRecord.student.pk)
			

	return studsToday
		
	
	

		
	 
	
	
