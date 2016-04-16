#! /usr/local/bin/python

# See ./Docs/Abstract.md to see a small exposition on the abstract inner
#  workings of Jarvis' core functionality.

import argparse

from Resources.AppHandler import *
from Resources.Libraries import Library
import csv, time

# TODO Further define core functionality of Jarvis to include use of JarvisServer.
# TODO Design a mainloop for Jarvis to ensure persistence of the main thread.


class Jarvis(object):
    """ Network utility service.

    Base executable of Jarvis.
    """

    def __init__(self, parser):
        """ Initializes a Jarvis object. """
        # from Resources.JarvisServer import JarvisServer
        # self.js = JarvisServer()

        # TODO Build initial settings save / load

        self.runtime_vars = {}
        self.running_dir = sys.argv[0]
        self.jarvis_paths = {
            'Apps': self.running_dir + '/Apps/',
            'Docs': self.running_dir + '/Docs/',
            'Libs': self.running_dir + '/Libs/',
            'Links': self.running_dir + '/Links/',
            'Resources': self.running_dir + '/Resources',
        }

        # TODO Define loading jarvis runtime from shutdown.

        # TODO Define runtime flags

        self.parsed_args = parser.parse_args()

    def run(self):
        # TODO Document Jarvis.run()
        # TODO Further define user funcitonality.
        finder = AppFinder(self.jarvis_paths['Apps'])
        ex = AppLauncher(finder.find_jarvis_apps())
        print('Press CNTRL+C to exit!')
        while 1:
            try:
                print(ex.interactive())
            except KeyboardInterrupt:
                break

    @staticmethod
    def loader(pathtolibs):
        """
        :param pathtolibs: The path to the the directory that contains the save files.
        :return: Returns either a jarvis runtime, or None.
        """
        with open(pathtolibs, 'w') as f:
            creader = csv.reader(f)
            table = []
            for row in creader:
                table.append(row)

            if len(table) > 0:
                return Library.unpack_libraries(table[-1][0])
            else:
                return None

    def __del__(self, reason=None):
        """ Further definition of Jarvis Garbage collection protocols.

        :param reason: Include a string to log why Jarvis was shutdown without proper shutdown.
        """
        # TODO Determine a better location to host Jarvis Saves. They could potentially be very large files.
        # Is it more prudent to use pickle here? I don't believe that a save of the main jarvis runtime would be needed.
        Library.pickle_libraries([self], 'JarvisShutdown%s' % time.time(), self.jarvis_paths['Libs'])
        with open(self.jarvis_paths['Libs'] + 'Saves', 'w') as f:
            cwriter = csv.writer(f)
            cwriter.write('JarvisShutdown%s' % time.time(), reason)



class Scratchpad(Jarvis):
    """ An object used for testing and development of new central features of Jarvis. """

    def shutdown(self, js):
        print ('\n\n\n----------------\nCleaning up JarvisSpeaker.\n----------------')
        js.shutdown()

        while js.is_scanning:
            pass

        # time.sleep(2)
        print ('\n\n\n----------------\nGoodbye.\n----------------\n\n\n')

    @staticmethod
    def read_js_status(js):
        status = js.status()
        catter = ''
        for key in sorted(status.keys()):
            if key == 'Hosts':
                if key == 'Hosts' and len(list(status[key].keys())) == 0:
                    catter += '\n----------------\nFound %s, expanding js.status[\'%s\'].keys()  ...' % (key, key)
                    time.sleep(0.2)
                    catter += '\n  - js.status[\'%s\'].keys() had no internal hosts......' % key
                    time.sleep(0.2)
                else:
                    catter += '\n----------------\n Found %s, expanding js.status[\'%s\'].keys()  ...\n    %s' % (
                        key, key, sorted(status[key].keys()))
                    time.sleep(0.2)
                    catter += '\n----------------'
                    time.sleep(0.2)
                    for value in sorted(status[key].keys()):
                        catter += '\n    ------------'
                        time.sleep(0.2)
                        catter += '\n    Expanding js.status[\'%s\'][\'%s\']:\n    -   %s' % (key, value,
                                                                                              (status[key][value]))
                        time.sleep(0.2)
            else:
                catter += '\n----------------\nFirst level key is: \"%s\", Expanding js.status[\'%s\']: \n -  %s'\
                          % (key, key, status[key])
                time.sleep(0.1)
        return catter

if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('scratch', action='store_true')
    j = Jarvis(parse)
    # j.run()
