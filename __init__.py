import os
import re
import shutil

root_path=os.path.abspath(".")+'\\'

with open('Note.vbs','w') as fp:
	fp.write('Set ws = CreateObject("Wscript.Shell")\nws.run "cmd /c {}",vbhide'.format(root_path+'Note.bat'))

with open('Note.bat','w') as fp:
	fp.write('@echo off\ncd {}\nset FLASK_APP=website\nflask run\npause'.format(root_path+'website'))

with open('website/Note.ini','w') as fp:
	fp.write('ROOT_PATH={}'.format(root_path))

with open('sublime/Note.ini','w') as fp:
	fp.write('ROOT_PATH={}'.format(root_path))

username=os.environ['USERNAME']
for file in os.listdir('sublime'):
	shutil.copy('sublime/'+file,'C:/Users/{}/AppData/Roaming/Sublime Text 3/Packages/User/{}'.format(username,file))
