from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView
from django.http import HttpResponse
from clubSetup.models import *
from attendance.models import *
import datetime

# Create your views here.

def updateAttendance(request,clubID):
	club = get_object_or_404(Club,pk=clubID)
	studList = Student.objects.all()
	formList = Form.objects.all()
	
	#Date Handling
	
	monthList=["","January","February","March","April","May","June","July","August","September","October","November","December"]
	weekdayList=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
	updateAvailableDate(club)#Updates the list of possible dates
	dateList = readAvailableDate(club) #Reads all dates that are possible
	
	pkList = []
	criteriaList = []
	criteriaListRaw = Criteria.objects.filter(clubID = club)
	for criteria in criteriaListRaw:
		criteriaList.append(criteria)
		
	while len(criteriaList) < 3:
		criteriaList.append("None")	
	
	clubFilePath = clubInfoStorage.location + "/" + club.name + "/attendance"
	
	studentRecordList = readMasterFile(clubFilePath,"Master_File.ca")
	
	for studentRecord in studentRecordList:
		pkList.append(studentRecord.student.pk)
	
	context = {"studentRecordList":studentRecordList,"studList":studList,"formList":formList,"club":club,"dateList":dateList,"monthList":monthList,"clubDay":weekdayList[club.day],"criteriaList":criteriaList,"pkList":pkList}
	
	return render(request,"attendanceUpdate.html",context)
	

def attendedStudents(request,clubID):
	
	club = Club.objects.get(pk=clubID)
	studList = []
	studDictListRaw = request.POST
	
	#Skips the csrf token
	studDictList = iter(studDictListRaw)
	print(request.POST)
	next(studDictList)
	
	dateKey = next(studDictList)
	print(dateKey)
	
	
	
	#Creates list of students who have attended
	
	#stores student and criteria
	studDataList = []
	studList = []
	
	for studDict in studDictList:	
		crit = []
		
		stud = Student.objects.get(pk=studDict)
		studList.append(stud)
		 
		critKey = next(studDictList)
		crit += request.POST.getlist(critKey) #obtains a list of all student criteria
		
		studData = [stud,crit]
		studDataList.append(studData)
	
	#Processing of attended students
	
	
	clubFilePath = clubInfoStorage.location + "/" + club.name + "/attendance"
	studRecordList = addToMaster(clubFilePath,"Master_File.ca",club,studDataList)
	
	#Obtain the Date from the dictionary and convert to datetime object
	#NOTE : returned date as string value
	date = request.POST[dateKey]
	date = datetime.datetime.strptime(date, '%Y/%m/%d') 
	
	studsToday = getStudsToday(studList,studRecordList)
	writeDateData(club,date,studRecordList)
	
	#Update Member List 
	updateMemberList(club,clubFilePath,"Master_File.ca","Members.ca")
	#Criteria Output handling
	
	criteriaHeaders = Criteria.objects.filter(clubID=club)
	
	return render(request,"attended.html",{"studList":studsToday,"criteriaHeaders":criteriaHeaders})

