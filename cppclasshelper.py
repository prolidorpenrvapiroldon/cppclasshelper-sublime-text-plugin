import sublime, sublime_plugin
from .template import Template

class CreateCppClassCommand(sublime_plugin.WindowCommand):
	'''
	class for create a C++ class with a sourcefile and headerfile
	'''
	def run(self, **kwargs):

		# plugin settings
		self.plugin_name = 'cppclasshelper-sublime-text-plugin'
		self.template_dir_name = 'templates'
		self.plugin_dir = "{}/{}".format(sublime.packages_path(), self.plugin_name)
		print(self.plugin_dir)
		self.template_dir = "{}/{}/".format(self.plugin_dir, self.template_dir_name)

		# global settings
		self.settings = sublime.load_settings("cppclasshelper.sublime-settings")
		self.vars = self.window.extract_variables()
		self.view = self.window.active_view()

		self.header_file_extension = self.settings.get('header_file_extension')

		# directory where files will be created
		self.create_directory = self.vars['file_path']

		# get folder from sidebar
		if "paths" in kwargs:
			self.create_directory = kwargs['paths'][0]

		# user enter a class name to create the class
		self.window.show_input_panel("Enter class name: ", "", self.create_class, None, None)


	def create_class(self, class_name):

		# set source file and header file
		self.source_file_name = "{}.cpp".format(class_name)
		self.header_file_name = "{}.{}".format(class_name, self.header_file_extension)

		source_file_template = Template("C++ Source File")
		header_file_template = Template("C++ Header File")

		try:
			source_file_template.load(self.template_dir + 'sourcefile.template')
			header_file_template.load(self.template_dir + 'headerfile.template')
		except OSError as e:
			sublime.error_message("Error while loading class template: {}".format(str(e)))
			return


		# render the template
		source_file_template.render(class_name=class_name, header_file_extension=self.header_file_extension)
		header_file_template.render(class_name=class_name)

		# file names to create
		self.source_file = "{}/{}".format(self.create_directory, self.source_file_name)
		self.header_file = "{}/{}".format(self.create_directory, self.header_file_name)

		# write files
		try:

			# write header file
			header_file_obj = open(self.header_file, "w+")
			header_file_obj.write(header_file_template.template)
			header_file_obj.close()
			self.view.set_status('class_create_progress_header_file', 'Successfully created {}'.format(self.header_file_name))

			# write source file
			source_file_obj = open(self.source_file, "w+")
			source_file_obj.write(source_file_template.template)
			source_file_obj.close()
			self.view.set_status('class_create_progress_source_file', 'Successfully created {}'.format(self.source_file_name))

			# clear status bar
			sublime.set_timeout(self._erase_status, 5000)

			if self.settings.get('open_after_creation'):
				self.open_files()


		except Exception as e:
			sublime.error_message("Error while creating class: {}".format(str(e)))


	
	def open_files(self):
		'''
		open files after creation
		'''
		self.window.open_file(self.header_file)


	# helper methods
	def _erase_status(self):
		self.view.erase_status('class_create_progress_header_file')
		self.view.erase_status('class_create_progress_source_file')
		
		