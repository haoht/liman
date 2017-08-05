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
VERSION = 'Alpha 0.4'
OS_TYPE = ''
ARCH = ''

def main():
    '''
        Main of liman.
    '''
    # platform.platform()
    # List style > name : [function name, description, required paramater count]
    parameter_list = {'list': [scriptslist, 'List of scripts in all repositories.', 0],
                      'repos': [repositories, 'List of repositories.', 0],
                      'log': [log, 'Logs of liman.', 0],
                      'search': [search, 'Search recursively in all repositories', 1],
                      'update': [update, 'Update specific repository by name.', 1],
                      'add': [add, 'Add new repository to the liman.', 1],
                      'remove-repository': [remove_repository,
                                            'Remove installed repository from liman.', 1],
                      'remove': [remove, 'Remove installed scripts.', 1],
                      'install': [install, 'Install new script to the system.', 1],
                      'installed': [installed, 'List of installed scripts in the system.', 0],
                      'integrity': [integrity, 'Check and fix problems with liman itself.', 0],
                      'version' : [version,'Display the version of liman',0],
                      'run' : [run,'Run script directly',1]}
    # First, check if there's any parameter or not.
    if len(sys.argv) == 1:
        sys.exit('Usage: liman <action> [parameter]')
    # Secondly, check if first parameter is in list or not.
    param = sys.argv[1]
    if not param in parameter_list:
        print('Usage: liman <action> [parameter]')
        sys.exit(sys.argv[1] + ' is not available in liman.')
    # Let's check if action needs more parameter and quit if there's not enough input.
    required_paramaters = parameter_list[param][2]
    if required_paramaters != len(sys.argv) -2:
        sys.exit(param + ' requires ' + str(required_paramaters) + ' parameter to work.')
    # Finally, execute the task.

    parameter_list[param][0]()

def log():
    """
        Displaying log file of the liman.
    """
    # Display version and log file under data folder.
    print('Liman ' + VERSION + ' logs\n*****************')
    os.system('cat ' + DATA_FOLDER + 'log')
    sys.exit()

def root():
    """
        Check if program run as root.
    """
    # We can simply check if script run as root by UID
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
        print('Copying liman under /usr/bin/')
        shutil.copy(sys.argv[0], '/usr/bin/liman')
    # Check if liman has run permission
    if not os.access(BINARY, os.X_OK):
        print('Fixing liman\' run permission')
        os.chmod('/usr/bin/liman', 533)
    # Check if git installed or not.
    if not os.path.isfile('/usr/bin/git'):
        print('Git not found, installing...')
        if platform.system() == 'Darwin':
            os.system('git')
        else:
            os.system('apt-get install git')
            os.system('yum install git')
            os.system('pacman -S git')
    # Lastly, check if liman data folder exist.
    if not os.path.isdir(DATA_FOLDER):
        os.mkdir(DATA_FOLDER)
    print('Integrity check completed, everything should be ok now :)')


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


def add():
    """
        Add new repository
    """
    name = sys.argv[1]
    root()
    # Creating repository folder with right permissions
    if not os.path.isfile(DATA_FOLDER + 'repos/' + name):
        os.system('mkdir -p ' + DATA_FOLDER + 'repos/' + name)
        os.chdir(DATA_FOLDER + 'repos/' + name)
    # Initializing git and enabling sparse checkout
    print('Adding repository...')
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
    print('Updating repositories')
    for current in repos:
        print(current)
        if current == name or name == '':
            # Updating repository with sparsecheckout
            os.chdir(DATA_FOLDER + 'repos/' + str(current))

            os.system('git pull --depth=2 origin master')
            os.system('chmod -R o=rx ' + DATA_FOLDER + 'repos/' + str(current) + '/scripts/*')
            if not os.path.isdir(DATA_FOLDER + 'repos/' + str(current) + '/scripts'):
                print('Invalid repository, deleting now.')
                remove_repository()
            else:
                print(str(current) + ' updated!')
                permission()


def remove_repository():
    """
        Delete repository by simply deleting it's folder
    """
    root()
    name = sys.argv[2]
    name = name.replace('/', '#')
    shutil.rmtree(DATA_FOLDER + 'repos/' + str(name))
    print(str(name) + ' removed!')


def remove(name):
    """Remove the script from installed folder."""
    root()
    if name == '':
        sys.exit('You must write script name')
    if name.startswith('l-'):
        name = name[2:]
    os.remove(DATA_FOLDER + 'installed/' + str(name) + '.sh')
    os.remove('/usr/bin/l-' + str(name))
    print(str(name) + ' removed.')


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
            print(str(script) + ' > ' + details(DATA_FOLDER +
                                                'repos/' + str(repo) + '/scripts/' + str(script), 3))


def installed():
    """
        Display the list of installed scripts under installed folder
    """
    if not os.path.isdir(DATA_FOLDER + 'installed'):
        sys.exit()
    # List the scripts under installed folder
    scripts = os.listdir(DATA_FOLDER + 'installed')
    for script in scripts:
        print('l-' + script[:-3])


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
    print('l-' + str(name[:-3]) + ' is installed.')


def repositories():
    """
        Display the list of repositories
    """
    if not os.path.isdir(DATA_FOLDER + 'repos'):
        sys.exit('There\'s no repository at all.')

    repos = os.listdir(DATA_FOLDER + 'repos')
    for current in repos:
        print(current)


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
                return result
    print(str(name) + ' not found.')
    return ''

def version():
    """
        Display the version of Liman
    """
    # Display the version and exit.
    sys.exit('Current liman version : ' + VERSION)

def run():
    """
        Run the script without installing it.
    """
    # Assuming system has bash installed TODO implement zsh and others.
    location = search(sys.argv[2])
    if location != '':
        os.system('bash ' + location)

main()
