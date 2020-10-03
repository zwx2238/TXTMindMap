from flask import Flask, request
import sys

sys.path.insert(0, '..')
from node import *

app = Flask('mindmap')

search_box = """
<form role="search" method="get" id="searchform" action="http://127.0.0.1:5000/search">
  <input type="search" name="q" autocomplete="off" placeholder="Search" required class="center">
</form>
<br>
	"""

with open('css.css') as fp:
	css_file = fp.read()
css = "<style>" + css_file + "</style>"


@app.route('/search/')
def search_detail_page():
	q = request.args.get('q')
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
		return css + search_box + result.html_header() + result.to_links(result)

	elif len(results) == 0:
		return css + search_box + '<br>没找到'

	elif len(results) > 1:
		string = css + search_box
		for result in results:
			string += '<br>' * 2 + """<a href="http://127.0.0.1:5000/search/?q={0}+-f">{1}</a>""".format(
				result.full_path,
				result.full_path)
		return string


@app.route('/')
def search_home_page():
	return css + search_box

app.debug=True
if __name__ == '__main__':
	app.run()
