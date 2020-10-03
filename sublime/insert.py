import sublime
import sublime_plugin


class InsertGreaterThanCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.insert(edit, self.view.sel()[0].begin(), " >")
