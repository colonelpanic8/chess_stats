class Extractor(object):

	def extract(self, identifier):
		raise NotImplemented()


class Transformer(object):

	def transform(self, raw_data):
		raise NotImplemented()


class Loader(object):

	def load(self, transformed):
		raise NotImplemented()


class ETL(object):

	# `extractor` should be an object that knows how to fetch data to be
	# transformed from a single argument.
	extractor = None

	# `transformers` should be a dictionary of transformation objects that should be
	# applied to extracted data.
	transformers = None

	# `loader` should be a loader instance. It should operate on a dictionary of
	# transformed values

	def __init__(self, identifier):
		self.identifier = identifier
		self.raw_data = None
		self.transformed = {}

	def execute(self):
		self.extract()
		self.transform()
		return self.load()

	def extract(self):
		self.raw_data = self.extractor.extract(self.identifier)
		return self.raw_data

	def transform(self):
		self.transformed.update(
			{
				key: transformer.transform(self.raw_data)
				for key, transformer in self.transformers.iteritems()
			}
		)

	def load(self):
		return self.loader.load(self.transformed)


class ModelLoader(Loader):

	def __init__(self, model_class):
		self.model_class = model_class

	def load(self, transformed):
		model_creation_arguments = {
			field_name: transformed[field_name]
			for field_name in self.model_class._meta.get_all_field_names()
			if field_name != 'id'
		}
		return self.model_class(**model_creation_arguments)
