from django.db import models
import simplejson


class JSONField(models.TextField):

	__metaclass__ = models.SubfieldBase

	_dumps = staticmethod(simplejson.dumps)
	loads = staticmethod(simplejson.loads)

	def to_python(self, value):
		if isinstance(value, basestring):
			# TODO: Add log if this fails.
			return self.loads(value)
		return value

	def get_prep_value(self, value):
		return self._dumps(value)
