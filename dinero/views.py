from django.shortcuts import render, redirect
from django.http import HttpResponse
from entry.models import Entry
import re
import django.utils.simplejson as json
import socket
from django.contrib.auth import authenticate, login, logout



def home(request):
	"""
		Renders the home page and provides a set of entries 
		as well as the raw text file associated with it. May
		also do some cleanup in the database and text file.
	"""
	if 'log-in' in request.POST:
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None and user.is_active:
			login(request, user)
	elif 'save-changes' in request.POST:
		if request.POST.get('text', ''):
			# Overwrite text file with new text
			with open('static/txt/database.txt', 'w') as myfile:
				myfile.write(request.POST.get('text', ''))
			clearDatabase()
			parse()
			organize(True)
	return render(request, 'home.html', {'request' : request})

def parse():
	"""
		Parses the text file for entries and adds them to the database 
		if it's not already in it
	"""
	regex = re.compile('(\D+);(\d+);(\d+)')
	with open('static/txt/database.txt', 'r') as myfile:
		for line in myfile:
			result = regex.match(line)
			if result:
				try:
					country = result.group(1)
					denomination = int(result.group(2))
					quantity = int(result.group(3))
					entry = Entry.objects.get(country=country, denomination=denomination)
				except Entry.DoesNotExist:
					entry = Entry(country=country, denomination=denomination, quantity=quantity)
					entry.save()
				except:
					pass


def clearDatabase():
	"""
		Removes every entry from the database
	"""
	for entry in Entry.objects.all():
		entry.delete()

def organize(alphabetize=False):
	"""
		Removes duplicates from the text file 
		and then sorts them alphabetically
	"""
	if alphabetize:
		entries = Entry.objects.all().order_by('country', 'denomination')
		for entry in entries:
			entry.country = entry.country.title()
			entry.save()
	entries = Entry.objects.all().order_by('country', 'denomination')
	with open('static/txt/database.txt', 'w') as myfile:
		bufferstring = ''
		for entry in entries:
			bufferstring = '%s\n%s;%s;%s' % (bufferstring, entry.country, entry.denomination, entry.quantity)
		if (bufferstring.startswith('\n')):
			myfile.write(bufferstring[1:])
		else:	
			myfile.write(bufferstring)

def getEntries(request):
	"""
		Returns the json representation of all the entries in the database.
	"""	
	response = []
	entries = Entry.objects.all().order_by('country', 'denomination')
	for entry in entries:
		obj = {}
		obj['currency'] = entry.country
		obj['denomination'] = entry.denomination
		obj['quantity'] = entry.quantity
		response.append(obj)
	return HttpResponse(json.dumps(response), content_type="application/json")

def newEntry(request):
	"""
		Grabs the information for the new entry, adds 
		it to the database, and updates the text file.
	"""
	if request.POST.has_key('client_response'):
		# Get entry from the client
		entry = json.loads(request.POST['client_response'])
		# Validate first
		if validates(entry):
			currency = entry['currency'].title()
			denom = int(entry['denomination'])
			quantity = int(entry['quantity'])
			# Write to the database and append to text file
			try:
				entry = Entry.objects.get(country=currency, denomination=denom)
				entry.quantity += quantity
				entry.save()
				string = "%s;%s;" % (currency, denom)
				# Find line in text file and update quantity
				mylist = []
				with open('static/txt/database.txt', 'r') as myfile:
					for line in myfile:
						if line.startswith(string):
							line = "%s;%s;%s\n" % (currency, denom, entry.quantity)
							print 'found old line'
						mylist.append(line)
				with open('static/txt/database.txt', 'w') as myfile:
					for line in mylist:
						myfile.write(line)
			except Entry.DoesNotExist:
				entry = Entry(country=currency, denomination=denom, quantity=quantity)
				entry.save()
				with open('static/txt/database.txt', 'r+a') as myfile:
					last = myfile.readlines()[-1]
					# Check if the file ended in a newline
					string = '' if '\n' in last else '\n'
					myfile.write("%s%s;%s;%s\n" % (string, currency, denom, quantity))
			organize(False)
			return HttpResponse('success')
	return HttpResponse('failure')

def validates(entry):
	"""
		Returns whether the entry has a valid currency, denomination, and quantity
	"""
	try:
		currency = entry['currency']
		denom = int(entry['denomination'])
		quantity = int(entry['quantity'])
		return currency and denom and quantity
	except:
		return False

def rawText():
	"""
		Returns the raw string version of the database
	"""
	with open('static/txt/database.txt', 'r') as myfile:
		return myfile.read()

def allEntries(request):
	"""
		Returns the json representation of the raw text file
	"""
	obj = {}
	obj['text'] = rawText()
	return HttpResponse(json.dumps(obj), content_type="application/json")

def logout_view(request):
	logout(request)
	return redirect("/")	