from datetime import datetime

import util


class Extractor(object):

	def extract(self, raw_data):
		"""Extract a data element from `raw_data`"""
		raise NotImplemented()


class Transformer(object):

	transform_arguments = None
	return_names = None

	def __init__(
		self,
		extracted_to_argument_name_map=None,
		return_name_map=None
	):
		self.return_name_map = None
		if extracted_to_argument_name_map:
			self.extracted_to_argument_name_map = extracted_to_argument_name_map
		else:
			self.extracted_to_argument_name_map = {
				argument: argument for argument in self.transform_arguments
			}

	def get_return_name(self, internal_name):
		if self.return_name_map is None:
			return internal_name
		return self.return_name_map[internal_name]

	def transform(self):
		"""Transform the data that is passed to this function. Returns a list of
		tuples of name, value pairs."""
		raise NotImplemented()


class SingleElementTransformer(Transformer):

	def __init__(self, element_name=None, input_name=None, output_name=None):
		if element_name:
			input_name = element_name
			output_name = element_name
		argument_name = iter(self.transform_arguments).next()
		return_name = iter(self.return_names).next()
		super(SingleElementTransformer, self).__init__(
			extracted_to_argument_name_map={input_name: argument_name},
			return_name_map={return_name: output_name}
		)

	def transform(self, **kwargs):
		return [(
			self.get_return_name(iter(self.return_names).next()),
			self._transform(**kwargs)
		)]

	def _transform(self, **kwargs):
		pass


class Loader(object):

	# `extractors` should be a dictionary mapping attribute names to extractor
	# instankces.
	extractors = None

	# `transformers` should be a list of transformation objects that should be
	# applied to extracted data.
	transformers = None

	def __init__(self):
		self.extracted = None
		self.transformed = {}
		self.loaded = {}

	def __getattr__(self, attr):
		for object_store in (self.loaded, self.transformed, self.extracted):
			try:
				return object_store[attr]
			except (KeyError, TypeError):
				continue
		raise AttributeError()

	def load_objects(self):
		raise NotImplemented()

	def execute(self, raw_data):
		self.extracted = {
			key: extractor.extract(raw_data)
			for key, extractor in self.extractors.iteritems()
		}

		for transformer in self.transformers:
			self.transformed.update(
				transformer.transform(
					**util.remap_keys_with_dict(
						self.extracted,
						transformer.extracted_to_argument_name_map
					)
				)
			)

		self.load_objects()


class DateTransformer(SingleElementTransformer):

	transform_arguments = set(['date_string'])
	return_names = set(['date'])

	DEFAULT_DATE_FORMAT = '%Y.%m.%d'

	def __init__(self, date_format=None, **kwargs):
		super(DateTransformer, self).__init__(**kwargs)

		if date_format:
			self.date_format = date_format
		else:
			self.date_format = self.DEFAULT_DATE_FORMAT

	def transform(self, date_string=None):
		return [(self.get_return_name('date'), datetime.strptime(date_string, self.date_format))]


class IntegerTransformer(SingleElementTransformer):

	transform_arguments = set(['string'])
	return_names = set(['int'])

	def transform(self, string=None):
		return [self.get_return_name('int'), int(string)]
