#! /usr/local/bin/python

import argparse
import os

from Apps.JarvisSpeaker import JarvisSpeaker
from Resources.Libraries import Library
from Resources.osInteraction import Interaction

library_name = 'JarvisDetectUSERS'


class JarvisDetect:
    """ Detects Wireless card MacID's.

    Uses Aircrack-ng to scan the wireless spectrum for registered MacID's from './registry.lock'

    :detect: Scans the network and returns any MacIDs found within the wireless range, and the number of times it was found.
    """

    # TODO Depricate Registry.lock use, use Resources.Libraries
    # TODO Define a garbage collection protocol for JarvisDetect that enables proper closer of scan CSV files/logs.
    def __init__(self, lists_path=None):
        self.registry_location = './registry.lock'
        self.search_term = 'key:'
        self.osi = Interaction()
        self._keys = None

        self.speaker = JarvisSpeaker()

        parser = argparse.ArgumentParser()
        parser.add_argument('-d', '--documentation', help='Simply outputs the functionality of '
                                                          'this App to the stdout', action='store_true')
        parser.add_argument('-rf', '--readfromfile', help='Flag this option if you want to load new users and MacID\'s.'
                                                          'This option requires two paths: The first containing UserID\'s'
                                                          'and the second containing MacID\'s, separated by a space. '
                                                          'These files must contain their respective values in matching '
                                                          'sequential order.',
                            type=str)
        parser.add_argument('-i', '--interactive', help='Runs JarvisDetect in an interactive, shell based interface.',
                            action='store_true')
        parsed_args = parser.parse_args()
        if parsed_args.documentation:
            print('Uses airocrack-ng\'s \"AiroDump-NG\" to monitor the wireless spectrum for WLAN MAC_ID\'s.\n\n\n' \
                  '%s' % parser.print_help())
            quit()

        if parsed_args.readfromfile is not None or lists_path is not None:
            self._keys = self.__build_list_fromfile(parsed_args.readfromfile)
        else:
            self._keys = self.__populate_list()

        if parsed_args.interactive:
            self.interactive()

    @staticmethod
    def __build_list_fromfile(path_str):
        """ Reads MacID's line by line from specified file location and returns them in a mutable list.

        :param path_str: A path to a file containing MacID's.
        :return: A mutable list containing MacID's.
        """
        returnable = {}

        name_location, id_location = path_str.split(' ', 2)

        if os.access(name_location, os.F_OK):
            with open(name_location) as name_file, open(id_location) as id_file:
                for name_line, id_line in zip(name_file, id_file):
                    returnable[name_line] = id_line
        else: raise RuntimeError('JarvisDetect could not open %s or %s!' % (name_location, id_location))

        if len(list(returnable.keys())) is 0: raise RuntimeError('JarvisDetect could not read MacID\'s from %s!' % path_str)
        else: return returnable

    @staticmethod
    def __populate_list():
        """ Builds a list of open temporary files or creates a new Library.

        :return: Either a list of open temporary files or an empty mutable list.
        """
        exists = Library.check_library(library_name)
        if exists:
            return Library.unpack_libraries(library_name).pop()
        else:
            raise RuntimeError('JarvisDetect could not load any user keys. Please run JarvisDetect with option '
                               '\'--readfromfile\' or \'-rf\' or python flag lists_path to load new keys before running '
                               'a scan.')

    def detect(self):
        """ Starts a new process of scanner.sh and counts through lines for 10 seconds before killing the process and
        returning MacID's that were found and the number of times that they were found.

        :returns: A mutable list containing tuples with MacID's and the number of times of occurrence.
        """
        # TODO Update detect() to use airodump-ng's CSV functionality.
        num_times_found = 0

        # detect handler
        log, process = self.osi.run('./Apps/JarvisDetectResources/scanner.sh', timer=15)

        # get a mac id
        # registry_file = open(self.registry_location)
        returnable = {}

        # # search through registry file for tags
        # for line in registry_file:
        #     if line.count(self.search_term) > 0 and (
        #             line.index(self.search_term) == 0):
        #         keys.append(line[len(self.search_term):-1])

        with open(log) as log_file:
            for term in self._keys.keys():
                for line in log_file:
                    if line.count(term) > 0:
                        num_times_found += 1
                    if num_times_found > 0:
                        returnable[term] = num_times_found

        process.kill()
        while process.poll() is None:
            pass
        self.osi.cleanup()

        return returnable

    def check_for_user(self, user):
        """ Calls JarvisDetect.detect() and iterates through its results to check for specified user.

        :param user: A user key.
        :return: True for user found, False for user not found.
        """
        results = self.detect()
        if list(results.keys()).count(user) > 0:
            return True
        else:
            return False

    def interactive(self):
        lister = {}
        for i, xname in enumerate(self._keys.keys()):
            print ('    %s: %s' % (str(i + 1), xname))
            lister[str(i + 1)] = xname
        xinput = input('Who do you want to detect? [Enter menu number...]: ')
        if list(lister.keys()).count(xinput()) > 0:
            if self.check_for_user(lister[xinput]):
                self.speaker.say('%s is within range!' % str(lister[xinput]), execution=True); return True
            else: self.speaker.say('%s is not within range!' % str(lister[xinput]), execution=True); return False
        else:
            print('Please select a number!')
            self.interactive()


if __name__ == '__main__':
    x = JarvisDetect('~/Documents/Jarvis/JarvisDetectResources/initialnames.txt ~/Documents/Jarvis/JarvisDetectResources/intialids.txt')
    print (x.detect())
