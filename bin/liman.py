#!/usr/bin/env python3
"""
    Liman Script Manager
    https://github.com/liman/liman
    http://liman.space
"""

import os
import sys
import shutil
import platform

BINARY = '/usr/bin/liman'
DATA_FOLDER = '/usr/local/share/liman/'
VERSION = 'Alpha 0.3'


def main():
    """
        Main handler for liman.
    """
    commandlist = {'list': [scriptslist, 'List of scripts in all repositories.'],
                   'repos': [repositories, 'List of repositories.'],
                   'log': [log, 'Logs of liman.'],
                   'search': [search, 'Search recursively in all repositories'],
                   'update': [update, 'Update specific repository by name.'],
                   'add': [add, 'Add new repository to the liman.'],
                   'remove-repository': [remove_repository,
                                         'Remove installed repository from liman.'],
                   'remove': [remove, 'Remove installed scripts.'],
                   'install': [install, 'Install new script to the system.'],
                   'installed': [installed, 'List of installed scripts in the system.'],
                   'integrity': [integrity, 'Check and fix problems with liman itself.']}
    argc = len(sys.argv)
    if not argc > 1:
        helpmenu()
        sys.exit('Usage: liman <command> [command argument]')
    command = sys.argv[1]
    if command not in commandlist:
        helpmenu()
        sys.exit('Command not found!')
    if argc > 2:
        name = sys.argv[2].replace('/', '#')
        commandlist[sys.argv[1]][0](name)
    else:
        commandlist[sys.argv[1]][0]()


def helpmenu():
    '''
        Display the help ( commands ) of the liman.
    '''
    commandlist = {'list': [scriptslist, 'List of scripts in all repositories.'],
                   'repos': [repositories, 'List of repositories.'],
                   'log': [log, 'Logs of liman.'],
                   'search': [search, 'Search recursively in all repositories'],
                   'update': [update, 'Update specific repository by name.'],
                   'add': [add, 'Add new repository to the liman.'],
                   'remove-repository': [remove_repository,
                                         'Remove installed repository from liman.'],
                   'remove': [remove, 'Remove installed scripts.'],
                   'install': [install, 'Install new script to the system.'],
                   'installed': [installed, 'List of installed scripts in the system.'],
                   'integrity': [integrity, 'Check and fix problems with liman itself.']}
    for command in commandlist:
        print command + '\t\t' + commandlist[str(command)][1]


def log():
    """
        Displaying log file of the liman.
    """
    os.system('cat ' + DATA_FOLDER + 'log')


def root():
    """
        Check if program run as root.
    """
    if not os.geteuid() == 0:
        sys.exit('Root is required for this action.')


def permission():
    """
        Permission fix for liman data folder.
    """
    root()
    os.system('chmod -R 755 ' + DATA_FOLDER)


def integrity():
    """
        Checking liman's integrity of files. Existence, permission issues and so on.
    """
    root()
    # Let's check if there's a binary or user run this from somewhere else
    if not os.path.isfile(BINARY):
        print 'Copying liman under /usr/bin/'
        shutil.copy(sys.argv[0], '/usr/bin/liman')
    # Check if liman has run permission
    if not os.access(BINARY, os.X_OK):
        print 'Fixing liman\' run permission'
        os.chmod('/usr/bin/liman', 733)
    # Check if git installed or not.
    if not os.path.isfile('/usr/bin/git'):
        print 'Git not found, installing...'
        if platform.system() == 'Darwin':
            os.system('git')
        else:
            os.system('apt-get install git')
    # Lastly, check if liman data folder exist.
    if not os.path.isdir(DATA_FOLDER):
        os.mkdir(DATA_FOLDER)
    print 'Integrity check completed, everything should be ok now :)'


def details(name, index):
    """
        Parsing script file' lines for data
    """
    if not search(name):
        sys.exit()
    script = open(name, 'r')
    try:
        current = script.readlines()[index]
        if not current.startswith('#'):
            return 'Don\'t have any detail'
        return current.rsplit(': ', 1)[1]
    except IndexError:
        return 'Don\'t have any detail'


def add(name):
    """
        Add new repository
    """
    root()
    # Creating repository folder with right permissions
    if not os.path.isfile(DATA_FOLDER + 'repos/' + name):
        os.system('mkdir -p ' + DATA_FOLDER + 'repos/' + name)
        os.chdir(DATA_FOLDER + 'repos/' + name)

    # Initializing git and enabling sparse checkout
    print 'Adding repository...'
    os.system('git init >> ' + DATA_FOLDER + 'log && git remote add origin https://github.com/'
            + str(name.replace('#', '/')) + '.git >> ' + DATA_FOLDER +'log')
    os.system('echo \'scripts/*\' >> .git/info/sparse-checkout' +
              '&& git config core.sparsecheckout true ')

    # Finally update
    update(name)


def update(name):
    """
        Update specific repository.
    """
    root()
    # Check if there's any repository or not.
    if not os.path.isdir(DATA_FOLDER + 'repos'):
        sys.exit('There\'s no repository at all.')
    # First get list of repositories initialized
    repos = os.listdir(DATA_FOLDER + 'repos')
    print 'Updating repositories'
    for current in repos:
        print current
        if current == name or name == '':
            # Updating repository with sparsecheckout
            os.chdir(DATA_FOLDER + 'repos/' + str(current))

            os.system('git pull --depth=2 origin master')
            os.system('chmod -R o=rx ' + DATA_FOLDER + 'repos/' + str(current) + '/scripts/*')
            if not os.path.isdir(DATA_FOLDER + 'repos/' + str(current) + '/scripts'):
                print 'Invalid repository, deleting now.'
                remove_repository(name)
            else:
                print str(current) + ' updated!'
                permission()


def remove_repository(name):
    """
        Delete repository by simply deleting it's folder
    """
    root()
    if name == '':
        sys.exit('You must write repository name')
    name = name.replace('/', '#')
    shutil.rmtree(DATA_FOLDER + 'repos/' + str(name))
    print str(name) + ' removed!'


def remove(name):
    """Remove the script from installed folder."""
    root()
    if name == '':
        sys.exit('You must write script name')
    if name.startswith('l-'):
        name = name[2:]
    os.remove(DATA_FOLDER + 'installed/' + str(name) + '.sh')
    os.remove('/usr/bin/l-' + str(name))
    print str(name) + ' removed.'


def scriptslist():
    """
        Listing files in all directories (repositories) under liman.
    """
    if not os.path.isdir(DATA_FOLDER + 'repos/'):
        sys.exit('There\'s no repository at all.')
    os.chdir(DATA_FOLDER + 'repos')
    repos = os.listdir(DATA_FOLDER + 'repos')
    for repo in repos:
        scripts = os.listdir(DATA_FOLDER + 'repos/' + str(repo) + '/scripts/')
        for script in scripts:
            print str(script) + ' > ' + details(DATA_FOLDER +
                                                'repos/' + str(repo) + '/scripts/' + str(script), 3)


def installed():
    """
        Display the list of installed scripts under installed folder
    """
    if not os.path.isdir(DATA_FOLDER + 'installed'):
        sys.exit()
    # List the scripts under installed folder
    scripts = os.listdir(DATA_FOLDER + 'installed')
    for script in scripts:
        print 'l-' + script[:-3]


def install(name):
    """
        Find and install desired script, also link and
        give permission so that user can run directly like l-sample
    """
    root()
    # Let's create the installed folder
    try:
        os.mkdir(DATA_FOLDER + 'installed')
    except OSError:
        pass
    location = search(name)
    if not location:
        sys.exit()
    if not name.endswith('.sh'):
        name = name + '.sh'
    shutil.copyfile(location, DATA_FOLDER + 'installed/' + str(name))
    os.system('ln -sf ' + str(location) + ' /usr/bin/l-' + str(name[:-3]))
    os.system('chmod +x /usr/bin/l-' + str(name[:-3]))
    print 'l-' + str(name[:-3]) + ' is installed.'


def repositories():
    """
        Display the list of repositories
    """
    if not os.path.isdir(DATA_FOLDER + 'repos'):
        sys.exit('There\'s no repository at all.')

    repos = os.listdir(DATA_FOLDER + 'repos')
    for current in repos:
        print current


def search(name):
    """
        Search for scripts in all repositories, it will stop after first result.
    """
    # name = sys.argv[2]
    if not os.path.isdir(DATA_FOLDER + 'repos'):
        sys.exit()
    if not name.endswith('.sh'):
        name = name + '.sh'
    repos = os.listdir(DATA_FOLDER + 'repos')
    for current in repos:
        scripts = os.listdir(DATA_FOLDER + 'repos/' + str(current) + '/scripts/')
        for script in scripts:
            if script in name:
                result = DATA_FOLDER + 'repos/' + str(current) + '/scripts/' + str(script)
                if sys.argv[1] == 'search':
                    print result
                return result
    print str(name) + ' not found.'
    return False


main()
