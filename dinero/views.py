from django.shortcuts import render
from django.http import HttpResponse
from entry.models import Entry
import re
import django.utils.simplejson as json
import socket

def home(request):
	"""
		Renders the home page and provides a set of entries 
		as well as the raw text file associated with it. May
		also do some cleanup in the database and text file.
	"""
	rawtext = rawText()
	if 'save-changes' in request.POST:
		if request.POST.get('text', ''):

			# # Contains new text
			# new = {x[:-1] for x in request.POST['text'].split('\n')}
			# # Contains old text
			# old = {x for x in rawtext.split('\n')}

			# for line in new:
			# 	print 'new; %s' % line

			# for line in old:
			# 	print 'old; %s' % line	

			# # Check what is in new but not in old - additions
			# for line in new:
			# 	if line not in old:
			# 		regex = re.compile('(\D+);(\d+);(\d+)')
			# 		result = regex.match(line)
			# 		if result:
			# 			try:
			# 				country = result.group(1).title()
			# 				denomination = int(result.group(2))
			# 				quantity = int(result.group(3))
			# 				entry = Entry.objects.get(country=country, denomination=denomination)
			# 				entry.quantity += quantity
			# 				entry.save()
			# 			except Entry.DoesNotExist:
			# 				entry = Entry(country=country, denomination=denomination, quantity=quantity)
			# 				entry.save()
			# 			except:
			# 				pass

			# # Check what is in old but not in new - deletions
			# for line in old:
			# 	if line not in new:
			# 		# print 'deleting %s' % line
			# 		regex = re.compile('(\D+);(\d+);(\d+)')
			# 		result = regex.match(line)
			# 		if result:
			# 			try:
			# 				country = result.group(1)
			# 				denomination = int(result.group(2))
			# 				quantity = int(result.group(3))
			# 				entry = Entry.objects.get(country=country, denomination=denomination)
			# 				entry.delete()
			# 			except:
			# 				pass

			# Overwrite text file with new text
			with open('static/txt/database.txt', 'w') as myfile:
				myfile.write(request.POST.get('text', ''))
			
	# clearDatabase()
	
	parse()
	organize()
	return render(request, 'home.html')

	# elif 'save-changes' in request.POST:
	# 	# Should read the textfield info and determine what to add/change
	# 	print 'saving changes now'
	# 	if request.POST.get('text', ''):
	# 		data = request.POST['text']
	# 	else:
	# 		print 'nothing'

# def addEntry(currency, denomination, quantity, text=False):
# 	try:
# 		currency = currency.title()
# 		denomination = int(denomination)
# 		quantity = int(quantity)
# 		Entry.objects.get(country=currency, denomination=denomination)
# 	except Entry.DoesNotExist:
# 		entry = Entry(country=currency, denomination=denomination, quantity=quantity)	
# 	except:
# 		pass

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
					entry.quantity += quantity
					entry.save()
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

def organize():
	"""
		Removes duplicates from the text file 
		and then sorts them alphabetically
	"""
	# myset = {}
	# with open('static/txt/database.txt', 'r') as myfile:
	# 	myset = {line for line in myfile}
	# with open('static/txt/database.txt', 'w') as myfile:
	# 	mylist = list(myset)
	# 	mylist.sort()
	# 	for line in mylist:
	# 		myfile.write(line)
	entries = Entry.objects.all().order_by('country', 'denomination')
	for entry in entries:
		entry.country = entry.country.title()
		entry.save()
	entries = Entry.objects.all().order_by('country', 'denomination')
	with open('static/txt/database.txt', 'w') as myfile:
		bufferstring = ''
		for entry in entries:
			bufferstring = '%s\n%s;%s;%s' % (bufferstring, entry.country, entry.denomination, entry.quantity)
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
	with open('static/txt/database.txt', 'r') as myfile:
		return myfile.read()

def allEntries(request):
	obj = {}
	obj['text'] = rawText()
	return HttpResponse(json.dumps(obj), content_type="application/json")

# from django.shortcuts import render_to_response
# from django.template import RequestContext
# from django.utils import simplejson

# def main(request):
# 	return render_to_response('ajaxexample.html', context_instance=RequestContext(request))
 
# def ajax(request):
# 	if request.POST.has_key('client_response'):
# 		x = request.POST['client_response']                 
# 		y = "hello %s!" % x                         
# 		response_dict = {}                                         
# 		response_dict.update({'server_response': y })                                                                  
# 		return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
# 	else:
# 		return render_to_response('ajaxexample.html', context_instance=RequestContext(request))