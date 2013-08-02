from django.shortcuts import render
from entry.models import Entry
import re

def home(request):
	# parse()
	errors = {}
	if 'submit' in request.POST:
		# Doing server side validation of the form
		country = request.POST['country']
		if not country or not re.match("^\D+$", country):
			errors['country'] = True
		else:
			country = country.title()

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

		if not errors:
			try:
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
			print data
		else:
			print 'nothing'

	entries = Entry.objects.all().order_by('country', 'denomination')
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