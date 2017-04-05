#!/usr/bin/python

import os
import sys
import shutil
import json
import StringIO

def handler(action, name):
    if action == 'list':
        listall()
    elif action == 'update':
        update()
    elif action == 'repos':
        repositories()
    elif action == 'add':
        add(name)
    elif action == 'remove':
        remove(name)
    elif action == 'run':
        run(name)
    elif action == 'install':
        install(name)
    elif action == 'log':
        log()
    else:
        print('Command not found, available commands are : \nlist, update, '
              'repos, add, remove, run, install, log')


if len(sys.argv) > 3:
    print('Too many arguments')
elif len(sys.argv) > 2:
    handler(sys.argv[1], str(sys.argv[2]).replace('/', '#'))
elif len(sys.argv) > 1:
    handler(sys.argv[1], '')
else:
    print('Please deploy an action')


def log():
    os.system('cat /usr/local/share/liman/log')


def add(name):
    # Creating repository folder with right permissions

    os.system('mkdir -p /usr/local/share/liman/repos/' + str(name))
    os.chdir('/usr/local/share/liman/repos/' + str(name))

    # Initializing git and enabling sparse checkout
    os.system('git init >> /usr/local/share/liman/log && git remote add origin https://github.com/' + str(
        name.replace('#', '/')) + '.git >> /usr/local/share/liman/log')
    os.system('echo \'scripts/*\' >> .git/info/sparse-checkout && git config core.sparsecheckout true ')
    os.system('exit')
    print(str(name) + ' added!')

    # Finally update
    update()


def update():
    # First get list of repositories initialized
    repos = os.listdir('/usr/local/share/liman/repos')

    for current in repos:
        # Updating repository with sparsecheckout
        os.chdir('/usr/local/share/liman/repos/' + str(current))
        os.system('git pull --depth=2 origin master >> /usr/local/share/liman/log ')
        os.chmod('/usr/local/share/liman/repos/' + str(current) + '/scripts/', 744)
        print(str(current) + ' updated!')
    print('All repositories updated.')


def remove(name):
    # Simply removing folder

    name = name.replace('/', '#')
    shutil.rmtree('/usr/local/share/liman/repos/' + str(name))
    os.system('exit')
    print(str(name) + ' removed!')


def listall():
    # Listing files in all directories (repositories) under liman.

    os.chdir('/usr/local/share/liman/repos/')
    os.system('find . -iname *.sh')
    os.system('exit')


def install(name):
    # Let's create the installed folder
    try:
        os.mkdir('/usr/local/share/liman/installed')
    except OSError:
        print('Installing ' + str(name))

    # Now find the script location (in which repository)
    repos = os.listdir('/usr/local/share/liman/repos')
    found = False
    for current in repos:
        # Now that we have a list of our repositories, check each of them
        try:
            scriptlist = os.listdir('/usr/local/share/liman/repos/' + str(current) + '/scripts/')
        except OSError:
            print('Find installed folder!')
        for script in scriptlist:
            print(script)
            if script == str(name) + '.sh':
                found = True
                shutil.copyfile('/usr/local/share/liman/repos/' + str(current) + '/scripts/' + str(script),
                                '/usr/local/share/liman/installed/' + str(name) + '.sh')
                print(str(name) + ' is installed.')
                run(name)
    if not found:
        print(str(name) + ' is not found.')


def run(name):
    # Basic if statement to add .sh extension to the name
    name = str(name) + '.sh' if not name.endswith('.sh') else name

    # Check if file exist
    if os.path.isfile('/usr/local/share/liman/installed/' + str(name) + '.sh'):
        os.system('sh /usr/local/share/liman/installed' + str(name) + '.sh')
    else:
        print('File not found or not installed')


def repositories():
    repos = os.listdir('/usr/local/share/liman/repos')
    for current in repos:
        print(current)


def readdb(reponame):
    if not os.path.isfile('/usr/local/share/liman/db/repo.json'):
        index = open('/usr/local/share/liman/db/' + reponame + '.json')
    print(index)


def createdb(type):
    if type == 'repolist':
        print('')
    elif type.startswith('repo:'):
        print('')
