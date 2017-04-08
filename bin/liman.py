#!/usr/bin/python

import os
import sys
import shutil


def handler(action, name):
    # Action's without root
    if action == 'list':
        scriptslist()
    elif action == 'repos':
        repositories()
    elif action == 'log':
        log()
    elif action == 'search':
        search(name)
    # Action's that require root
    elif action == 'update':
        update(name)
    elif action == 'add':
        add(name)
    elif action == 'remove-repository':
        remove_repository(name)
    elif action == 'remove-script':
        remove_script(name)
    elif action == 'install':
        install(name)
    elif action == 'installed':
        installed()
    else:
        print('Command not found, available commands are : \nlist, repos, '
              'log, search, update, add, remove-repository, remove-script',
              'install', 'installed')


# Side functions to make Liman work.

def log():
    os.system('cat /usr/local/share/liman/log')


def root():
    if not os.geteuid() == 0:
        return False
    else:
        return True


def permission(repo):
    if not os.path.exists('/usr/local/share/liman/repos/' + str(repo)):
        sys.exit()
    os.system('chmod -R 755 /usr/local/share/liman/')


def details(name, index):
    if not search(name):
        sys.exit()
    script = open(name, 'r')
    try:
        return script.readlines()[index]
    except IndexError:
        return 'Nothing'


# Main functions of Liman

def add(name):
    # Check if user is root, otherwise it can't work.
    if not root():
        sys.exit('You must run Liman as root')

    # Creating repository folder with right permissions
    if not os.path.isfile('/usr/local/share/liman/repos/' + str(name)):
        os.system('mkdir -p /usr/local/share/liman/repos/' + str(name))
        os.chdir('/usr/local/share/liman/repos/' + str(name))

    # Initializing git and enabling sparse checkout
    print('Adding repository...')
    os.system('git init >> /usr/local/share/liman/log && git remote add origin https://github.com/' + str(
        name.replace('#', '/')) + '.git >> /usr/local/share/liman/log')
    os.system('echo \'scripts/*\' >> .git/info/sparse-checkout && git config core.sparsecheckout true ')

    # Finally update
    update(name)


def update(name):
    # Check if user is root, otherwise it can't work.
    if not root():
        sys.exit('You must run Liman as root')

    # Check if there's any repository or not.
    if not os.path.isdir('/usr/local/share/liman/repos'):
        sys.exit('There\'s no repository at all.')
    # First get list of repositories initialized
    repos = os.listdir('/usr/local/share/liman/repos')

    for current in repos:
        if current == name or name == '':
            # Updating repository with sparsecheckout
            os.chdir('/usr/local/share/liman/repos/' + str(current))
            os.system('git pull --depth=2 origin master')
            os.system('chmod -R o=rx /usr/local/share/liman/repos/' + str(current) + '/scripts/*')
            # os.chmod('/usr/local/share/liman/repos/' + str(current) + '/scripts/', 755)
            print(str(current) + ' updated!')
    permission(name)


def remove_repository(name):
    # Check if user is root, otherwise it can't work.
    if not root():
        sys.exit('You must run Liman as root')

    if name == '':
        sys.exit('You must write repository name')
    # Simply removing folder

    name = name.replace('/', '#')
    shutil.rmtree('/usr/local/share/liman/repos/' + str(name))
    print(str(name) + ' removed!')


def remove_script(name):
    # Check if user is root, otherwise it can't work.
    if not root():
        sys.exit('You must run Liman as root')
    if name == '':
        sys.exit('You must write script name')
    name = name + '.sh'
    os.remove('/usr/local/share/liman/installed/' + str(name) + '.sh')
    os.remove('/usr/bin/l-' + str(name))
    print(str(name) + ' removed.')


# Listing files in all directories (repositories) under liman.

def scriptslist():
    if not os.path.isdir('/usr/local/share/liman/repos'):
        sys.exit('There\'s no repository at all.')
    os.chdir('/usr/local/share/liman/repos/')
    repos = os.listdir('/usr/local/share/liman/repos')
    for repo in repos:
        scripts = os.listdir('/usr/local/share/liman/repos/' + str(repo) + '/scripts/')
        for script in scripts:
            print(str(script) + ' > ' + details('/usr/local/share/liman/repos/'
                                                + str(repo) + '/scripts/' + str(script), 2))


def installed():
    if not os.path.isdir('/usr/local/share/liman/installed'):
        sys.exit()
    # List the scripts under installed folder
    scripts = os.listdir('/usr/local/share/liman/installed')
    for script in scripts:
        print('l-' + script[:-3])


def install(name):
    if not root():
        sys.exit('You must run Liman as root')
    # Let's create the installed folder
    try:
        os.mkdir('/usr/local/share/liman/installed')
    except OSError:
        pass
    location = search(name)
    if not location:
        sys.exit()
    shutil.copyfile(location, '/usr/local/share/liman/installed/' + str(name))
    os.system('ln -sf ' + str(location) + ' /usr/bin/l-' + str(name[:-3]))
    os.system('chmod +x /usr/bin/l-' + str(name[:-3]))
    print('l-' + str(name[:-3]) + ' is installed.')


def repositories():
    if not os.path.isdir('/usr/local/share/liman/repos'):
        sys.exit('There\'s no repository at all.')

    repos = os.listdir('/usr/local/share/liman/repos')
    for current in repos:
        print(current)


def search(name):
    if not os.path.isdir('/usr/local/share/liman/repos'):
        sys.exit()
    if not name.endswith('.sh'):
            name = name + '.sh'
    repos = os.listdir('/usr/local/share/liman/repos')
    for current in repos:
        scripts = os.listdir('/usr/local/share/liman/repos/' + str(current) + '/scripts/')
        for script in scripts:
            if script in name:
                result = '/usr/local/share/liman/repos/' + str(current) + '/scripts/' + str(script)
                return result
    print(str(name) + ' not found.')
    return False

if len(sys.argv) > 3:
    print('Too many arguments')
elif len(sys.argv) > 2:
    handler(sys.argv[1], str(sys.argv[2]).replace('/', '#'))
elif len(sys.argv) > 1:
    handler(sys.argv[1], '')
else:
    print('Please deploy an action')
