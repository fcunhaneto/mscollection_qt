import os

from install import install_db, texts_install as texts

path = os.getcwd()

# Insert shebang in file principal.py
shebang = '#!' + path + '/venv/bin/python\n'

with open('mscollection.py', 'r') as old_file:
    save_text = old_file.read()
with open('mscollection.py', 'w') as new_file:
    new_file.write(shebang)
with open('mscollection.py', 'a') as new_file:
    new_file.write(save_text)

# Change file principal.py permission for running in terminal
os.system('chmod +x mscollection.py')

install_db.main()

