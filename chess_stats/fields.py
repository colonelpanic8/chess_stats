from django.db import models
import simplejson


class JSONField(models.TextField):

	__metaclass__ = models.SubfieldBase

	dumps = simplejson.dumps
	loads = simplejson.loads

	def to_python(self, value):
		if isinstance(value, basestring):
			# TODO: Add log if this fails.
			return self.loads(value)

	def get_prep_value(self, value):
		self.dumps(value)
