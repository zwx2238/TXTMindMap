import sublime
import sublime_plugin
import os
from .node import *

init()

class TxtMindMapCommand(sublime_plugin.WindowCommand):
    def run(self):
        sublime.active_window().show_input_panel('', '', self.on_entered, None, None)

    def on_entered(self, query):
        self.window.active_view().run_command('search', {'query': query})


class SearchCommand(sublime_plugin.TextCommand):
    def run(self, edit, query):
        q=query
        if q.endswith('-v'):
            results = search(q[:-2], mode='vague')
        elif q.endswith('-f'):
            results = [search(q[:-2], mode='full_path')]
        else:
            results = search(q, mode='strict')
            if not results:
                results = search(q, mode='vague')

        if len(results) == 1:
            result = results[0]

        elif len(results) == 0:
            error_message='没找到'
            sublime.error_message(error_message)
            raise Exception(error_message)

        elif len(results) > 1:
            error_message = "\n".join([result.full_path for result in results])
            sublime.error_message(error_message)
            raise Exception(error_message)

        text = result.full_path + '\n' + result.to_txt_string(recursion=False)

        view = sublime.active_window().new_file()
        view.insert(edit, 0, text)
        view.set_scratch(True)


class SaveChangeCommand(sublime_plugin.EventListener):
    def on_pre_close(self, view):
        if not view.is_scratch():
            return
        changed_text = view.substr(sublime.Region(0, view.size()))

        full_path, *changed_text = changed_text.split('\n')
        changed_text = "\n".join(changed_text)
        changed = to_tree(changed_text)

        changed.full_path = full_path
        new_root = alter(changed)
        new_root.save_to_txt(ROOT_PATH)

        print('Successfully Saved!')


if __name__ == '__main__':
    pass