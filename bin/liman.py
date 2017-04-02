#!/usr/bin/python

import os
import sys
import shutil

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
    else:
        print('Command not found')


def add(name):
    # Creating repository folder with right permissions
    os.system('mkdir -p /usr/local/liman/' + str(name))
    os.chdir('/usr/local/liman/' + str(name))

    # Initializing git and enabling sparse checkout
    os.system('git init && git remote add origin https://github.com/' + str(name.replace('#', '/')) + '.git ')
    os.system('echo \'scripts/*\' >> .git/info/sparse-checkout && git config core.sparsecheckout true ')
    print(str(name) + ' added!')

    # Finally update
    update()


def update():
    # First get list of repositories initialized
    repos = os.listdir('/usr/local/liman')

    for current in repos:
        # Updating repository with sparsecheckout
        os.chdir('/usr/local/liman/' + str(current))
        os.system('git pull --depth=2 origin master')
        os.chmod('/usr/local/liman/' + str(current) + '/scripts/', 744)
        print(str(current) + ' updated!')
    print('All repositories updated.')


def remove(name):
    # Simply removing folder
    name = name.replace('/', '#')
    shutil.rmtree('/usr/local/liman/' + str(name))
    print(str(name) + ' removed!')


def listall():
    # Listing files in all directories (repositories) under liman2.
    os.chdir('/usr/local/liman/')
    os.system('find . -iname *.sh')


def run(name):
    # Basic if statement to add .sh extension to the name
    name = str(name) + '.sh' if not name.endswith('.sh') else name

    # Give permission to run the script
    os.chmod('/usr/local/liman/liman#liman-depo/scripts/' + str(name), 100)
    os.system('bash /usr/local/liman/liman#liman-depo/scripts/' + str(name))


def repositories():
    repos = os.listdir('/usr/local/liman')

    for current in repos:
        print(current)


if len(sys.argv) > 2:
    handler(sys.argv[1], str(sys.argv[2]).replace('/', '#'))
elif len(sys.argv) > 1:
    handler(sys.argv[1], '')
else:
    print('Please deploy an action')


