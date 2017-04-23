# Liman

  Liman is not a package manager.
  It is written in the Python language.
  Copying, duplication and reuse are very convenient.
  There is a directory structure where scripts are listed and some information is kept.

### Prerequisites

  Python Language,
  Git Structure

### Install

```
$ wget -q https://raw.githubusercontent.com/liman/liman/master/install.sh -O - | sudo bash
```

## Usage Manual

```
Usage: liman <command> [command argument]

Commands:
  list                # List of scripts in all repositories
  repos               # List of repositories
  log                 # Logs of liman
  search              # Search recursively in all repositories
  update              # Update specific repository by name
  add                 # Add new repository to the liman
  remove-repository   # Remove installed repository from liman
  remove              # Remove installed scripts
  install             # Install new script to the system
  installed           # List of installed scripts in the system
  integrity           # Check and fix problems with liman itself
```
### Example

```
$ sudo liman add liman/ldepo
```

## License
