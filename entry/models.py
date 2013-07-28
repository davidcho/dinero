from django.db import models

class Entry(models.Model):
	country = models.CharField(max_length=30)
	denomination = models.IntegerField()
	quantity = models.IntegerField()

	def __unicode__(self):
		return "From: %s, denomination: %d, quantity %d" % (self.country, self.denomination, self.quantity)