from django.shortcuts import render
from django.http import HttpResponse
from entry.models import Entry
import re
import django.utils.simplejson as json

def home(request):
	# parse()
	errors = {}
	if 'submit' in request.POST:
		# Doing server side validation of the form
		errors = validate(request)
		if not errors:
			try:
				country = request.POST['country'].title()
				denom = int(request.POST['denomination'])
				quantity = int(request.POST['quantity'])

				entry = Entry.objects.get(country=country, denomination=denom)
				entry.quantity += quantity
				entry.save()
			except Entry.DoesNotExist:
				entry = Entry(country=country, denomination=denom, quantity=quantity)
				entry.save()
	elif 'save-changes' in request.POST:
		# Should read the textfield info and determine what to add/change
		print 'saving changes now'
		if request.POST.get('text', ''):
			data = request.POST['text']
		else:
			print 'nothing'

	entries = Entry.objects.all().order_by('country', 'denomination')
	response = []
	for entry in entries:
		obj = {}
		obj['currency'] = entry.country
		obj['denomination'] = entry.denomination
		obj['quantity'] = entry.quantity
		response.append(obj)
	string = json.dumps(response)

	return render(request, 'home.html', {
		'entries' : entries,
		'rawtext' : read(),
		'errors' : errors,
		})

def parse():
	"""
		Parses the text file for entries and adds them to the database 
		if it's not already in it
	"""
	regex = re.compile('(\D+);(\d+);(\d+)')
	for line in open('static/txt/database.txt'):
		result = regex.match(line)
		country = result.group(1)
		# assumes that next two are ints
		denomination = int(result.group(2))
		quantity = int(result.group(3))
		# print '%s %s %s' % (country, denomination, quantity)
		try:
			Entry.objects.get(country=country, denomination=denomination, quantity=quantity)
		except Entry.DoesNotExist:
			entry = Entry(country=country, denomination=denomination, quantity=quantity)
			entry.save()

def read():
	f = open('static/txt/database.txt')
	string = f.read()
	f.close()
	return string

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

def entries(request):
	response = []
	entries = Entry.objects.all()#.order_by('country', 'denomination')
	for entry in entries:
		obj = {}
		obj['currency'] = entry.country
		obj['denomination'] = entry.denomination
		obj['quantity'] = entry.quantity
		response.append(obj)
	return HttpResponse(json.dumps(response), content_type="application/json")

# from django.shortcuts import render_to_response
# from django.template import RequestContext
# from django.utils import simplejson
# import socket
 
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