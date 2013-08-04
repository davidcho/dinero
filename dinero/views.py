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
	# clearDatabase()
	# organize()
	# parse()
	return render(request, 'home.html', { 'rawtext' : read() })
	# parse()
	# errors = {}
	# if 'submit' in request.POST:
	# 	# Doing server side validation of the form
	# 	if not errors:
	# 		try:
	# 			country = request.POST['country'].title()
	# 			denom = int(request.POST['denomination'])
	# 			quantity = int(request.POST['quantity'])

	# 			entry = Entry.objects.get(country=country, denomination=denom)
	# 			entry.quantity += quantity
	# 			entry.save()
	# 		except Entry.DoesNotExist:
	# 			entry = Entry(country=country, denomination=denom, quantity=quantity)
	# 			entry.save()
	# elif 'save-changes' in request.POST:
	# 	# Should read the textfield info and determine what to add/change
	# 	print 'saving changes now'
	# 	if request.POST.get('text', ''):
	# 		data = request.POST['text']
	# 	else:
	# 		print 'nothing'

	
	# response = []
	# for entry in entries:
	# 	obj = {}
	# 	obj['currency'] = entry.country
	# 	obj['denomination'] = entry.denomination
	# 	obj['quantity'] = entry.quantity
	# 	response.append(obj)
	# string = json.dumps(response)

	# return render(request, 'home.html', {
	# 	'entries' : entries,
	# 	'rawtext' : read(),
	# 	# 'errors' : errors,
	# 	})

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
					Entry.objects.get(country=country, denomination=denomination, quantity=quantity)
				except Entry.DoesNotExist:
					entry = Entry(country=country, denomination=denomination, quantity=quantity)
					entry.save()
				except:
					pass

def read():
	with open('static/txt/database.txt', 'r') as myfile:
		return myfile.read()

def validate(request):
	errors = {}
	country = request.POST['country']
	if not country or not re.match("^\D+$", country):
		errors['country'] = True

	if request.POST['denomination']:
		try:
			denom = int(request.POST['denomination'])
		except ValueError:
			errors['denom'] = True
	else:
		errors['denom'] = True

	if request.POST['quantity']:
		try:
			quantity = int(request.POST['quantity'])
		except ValueError:
			errors['quantity'] = True
	else:
		errors['quantity'] = True

	return errors

def getEntries(request):
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
	if request.POST.has_key('client_response'):
		# Get entry from the client
		# Validate first!
		entry = json.loads(request.POST['client_response'])
		currency = entry['currency']
		denom = int(entry['denomination'])
		quantity = int(entry['quantity'])
		# Write to the database and append to text file
		try:
			entry = Entry.objects.get(country=currency, denomination=denom)
			entry.quantity += quantity
			entry.save()
		except Entry.DoesNotExist:
			entry = Entry(country=currency, denomination=denom, quantity=quantity)
			entry.save()
			# check if there is already a newline or not
			with open('static/txt/database.txt', 'r+a') as myfile:
				last = myfile.readlines()[-1]
				print '\n' in last
			    # myfile.write("\n%s;%s;%s\n" % (currency, denom, quantity))
		return HttpResponse('success')
	return HttpResponse('failure')

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
	myset = {}
	with open('static/txt/database.txt', 'r') as myfile:
		myset = {line for line in myfile}
	with open('static/txt/database.txt', 'w') as myfile:
		mylist = list(myset)
		mylist.sort()
		for line in mylist:
			myfile.write(line)

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