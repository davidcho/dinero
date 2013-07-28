from django.shortcuts import render
from entry.models import Entry
import re

def home(request):
	parse()
	entries = Entry.objects.all().order_by('country', 'denomination')
	return render(request, 'home.html', {
		'entries' : entries,
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