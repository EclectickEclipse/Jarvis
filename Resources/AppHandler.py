#! /usr/local/bin/python

import os
import sys
import time

from Resources.osInteraction import Interaction


class AppFinder(object):
    """ Maintains a list of available applications and a short description on their functionality.

    :method: find_jarvis_apps is used to search through the ./Apps folder for useful applications.
    """

    def __init__(self, treedir=os.getcwd(), quiet=False, excluded_list=None):
        """ Gets initial applications.

        :param treedir: Included by default by Jarvis.
        """
        self.apps = {}
        self.excluded_files = ['__init__', '.pyc', '.DS_Store', 'registry.lock']
        self.executable_files = ['.py', '.sh']
        self.treedir = treedir

        if excluded_list is not None:
            if type(excluded_list) is str:
                self.excluded_files.append(excluded_list)
            elif type(excluded_list) is list:
                for user_exclusion in excluded_list:
                    self.excluded_files.append(user_exclusion)
            else:
                sys.stderr.write('Could not exclude user designated file: Requires a string or a python list. Received:'
                                 ' %s.\n' % str(type(excluded_list)))

    # @staticmethod
    def find_jarvis_apps(self, quiet=False):
        """ Builds a list of files, and checks for valid executable files.

        :returns: A dictionary containing the path of the apps and the description of each app.
        """

        if os.access(self.treedir, os.F_OK):
            for path, dirs, files in os.walk(self.treedir):
                for current_file in files:
                    self.apps[current_file] = [os.path.join(path, current_file)]

            apps_list = self.apps.copy().keys()
            # while 1:
            for app in apps_list:
                checks = []
                for excluded_name in self.excluded_files:
                    if app.count(excluded_name) is not 0:
                        checks.append(-1)
                    for executable_name in self.executable_files:
                        if app.count(executable_name) >= 1:
                            checks.append(1)

                for check in checks:
                    if check is 1 and not -1:
                        pass
                    elif check is -1:
                        try: del self.apps[app]
                        except KeyError: print(self.apps)

            from Resources.osInteraction import Interaction
            for app in self.apps.copy().keys():
                try:
                    log = Interaction.run(self.apps[app][0], kwargs='-d')
                    time.sleep(0.2)
                    with open(log[0]) as f:
                        self.apps[app].append(f.read())

                    os.remove(log[0])

                except OSError as e:
                    if not quiet:
                        sys.stderr.write('Could not execute %s! Excluding from list.\n%s, %s\n' % (self.apps[app][0],
                                                                                                   e.errno, e.strerror))
                    del(self.apps[app])

            return self.apps
        else:
            if not quiet: raise OSError('Could not access %s.' % './Apps/\n')


class AppLauncher(object):
    # TODO Further document AppLauncher
    def __init__(self, applist):
        self.applist = applist

    @staticmethod
    def exec_app(app):
        e = Interaction.run(app,wait_for_execution=True)
        os.remove(e[0])
        return e

    def interactive(self):
        while 1:
            print('Please select an option:')
            options = {}
            for i, app in enumerate(self.applist):
                options[i + 1] = self.applist[app][0]
                print('    %s: %s' % (i + 1, app))
            inp = input('::> ')
            try:
                if list(options.keys()).count(int(inp)) > 0:
                    return self.exec_app(options[int(inp)])
            except ValueError:
                pass

if __name__ == '__main__':
    x = AppFinder()
    retu = x.find_jarvis_apps()
    for val in retu:
        print(val)
        print(retu[val])
