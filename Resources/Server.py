#! /usr/local/bin/python

import os
import sys
import time

from Resources.Libraries import Library

# TODO Sanitize imports.


class JarvisServer(object):
    """ Initiates a new socket for Jarvis to use, and maintains a list of available Jarvis hosts on the network.

    Uses NMAP to scan for active TCP connections on port 5000, and maintains a list of possible hosts. Further defines
    a list of trusted connections after establishing a handshake(1) with the remote host. Provides framework
    interactions for the P2P network.

    JarvisServer maintains a list of child Threads within JarvisServer.Threads.

    :(1): Handshake is currently under conceptual design.
    :JarvisServer.sock: A raw socket.socket object.
    :JarvisServer.Threads: A list object containing raw threading.Thread objects for ease of access.
    :JarvisServer.hostname: The name of the host machine of the local Jarvis.
    :JarvisServer.Hosts: A dictionary containing possible host information of remote Jarvis's.
    :JarvisServer.has_scan: A boolean to notify the user if Jarvis has any scan information.
    :JarvisServer.is_scanning: A boolean to notify the user if Jarvis is scanning for new Jarvis's in the background.
    :JarvisServer.initialized: A boolean to signify when initialization is complete.
    """
    # TODO Futher document JarvisServer.
    # TODO Further define a socket and listening thread for JarvisServer to use.

    # TODO Restructure start().
    def start(self):
        can_continue = True

        for xthread in self.Threads:
            if xthread.name is 'xJarvisFinder':
                can_continue = False

        if can_continue:
            pass
        else:
            sys.stderr.write('Already found a JarvisFinder Thread.')
            return False

        self.jarvis_finder()
        try:
            while not self.is_scanning:
                pass
            else:
                return True
        except (IndexError, ValueError) as e:
            sys.stderr.write('Could not start JarvisServer.jarvis_finder(), got exception: {2}'
                             .format(e.message))
            return False

    def jarvis_finder(self):
        """ Use NMAP to search for other open Jarvis ports. """

        import nmap
        nm = nmap.PortScanner()

        def finder():
            """ Starts an nmap scan and iterates through its results to find any possible hosts. """
            while not self.ThreadKiller:
                self.is_scanning = True
                scan = nm.scan(self.__hostRange, str(self.JarvisPort))
                for host in list(scan['scan'].keys()):
                    if scan['scan'][host]['status']['state'] == 'up' and (
                                scan['scan'][host]['tcp'][int(self.JarvisPort)]['state'] == 'open'):
                        self._add_hosts(host, self.JarvisPort)
                        # self.scan_finished = True
                        # self._Hosts[(scan['scan'][host]['hostnames'][0]['name'])] = (host, self._JarvPort)
                    elif scan['scan'][host]['status']['state'] != 'up' and (
                                list(self.Hosts.keys()).count((scan['scan'][host]['hostnames'][0]['name'])) > 1):
                        self._del_hosts(host)
                        # self.scan_finished = True
                        # del self._Hosts[(scan['scan'][host]['hostnames'][0]['name'])]
                self.num_of_scans += 1
                self.has_scan = True
            else:
                self.is_scanning = False

        # bootstrap finder
        t = self._threader.Thread(target=finder, name='JarvisServer.jarvis_finder()')
        t.daemon = True
        t.start()
        self.Threads.append(t)
        return t

    # TODO Deprecate status().
    def status(self):
        """ Compiles information pertaining to the status. :returns: A dict containing status information. """

        def hosts_getter():
            """ Ensures self.Hosts is accessible. """
            try:
                if self.__hosts_lock.acquire():
                    value = self.Hosts
                    self.__hosts_lock.release()
                    return value
                else:
                    return {'Error': '_JarvisFinder is currently working with this variable.'}
            except AttributeError:
                return {'Error': 'Jarvis likely hasn\'t started scanning yet.....'}

        hosts = hosts_getter()

        x = {'sock': self.sock,
             'Threads': self.Threads,
             'JarvisPort': self.JarvisPort,
             'hostname': self.hostname,
             'Hosts': hosts,
             'is_scanning': self.is_scanning,
             'has_scan': self.has_scan}

        return x

    # TODO Restructure shutdown().
    def shutdown(self):
        """ Ensures that all persistent background threads are closed. """

        if len(self.Threads) is 1:
            sys.stderr.write('No threads are present to be shutdown by JarvisServer.shutdown().')
            return False
        self.ThreadKiller = True
        with self.__print_lock:
            print ('\n\n\n----------------\nJarvisServer is shutting down.')
            print ('\nCurrent active threads: ' + str(self._threader.activeCount()))
        for thread in self.Threads:
            with self.__print_lock:
                print ('  - Shutting down ' + str(thread.name))
            sys.stdout.writelines('      - ')
            while thread.is_alive():
                time.sleep(0.25)
                sys.stdout.writelines('.')
            else:
                with self.__print_lock:
                    print ('\n      - ' + str(thread.name) + ' has stopped running.')
        with self.__print_lock:
            print('\nCurrent active threads:' + str(self._threader.activeCount()) + '\n----------------')

        return True

    def reset_scan_counter(self):
        self.num_of_scans = 0

    def dump_hosts(self):
        """ Offloads a .jarv Library containing Hosts.

        :return: A boolean signifying success of method.
        """
        if os.access('./Libs/', os.F_OK):
            Library.pickle_libraries([self.Hosts], 'JarvisServer.Hosts')
            return True
        else:
            sys.stderr.write('Could not dump JarvisServer.Hosts...')
            return False

    # TODO Deprecate load_hosts_fromfile.
    def load_hosts_fromfile(self):
        """ Loads JarvisServer.Hosts from Library.

        :return: A boolean signifying success of method.
        """
        if os.access('./libs/', os.F_OK):
            if Library.check_library('JarvisServer.Hosts'):
                try:
                    self.Hosts = Library.unpack_libraries('JarvisServer.Hosts').pop()
                    return True
                except IndexError as e:
                    sys.stderr.write('Could not load JarvisServer.Hosts.... {1}' .format(str(e)))
                    return False
            else:
                return False


    @staticmethod
    def __range_finder():
        """ Gets the range of IP's to scan on the default network interface.

        :returns: Returns a range of IP's to be scanned.
        """
        import socket

        x = socket.gethostbyname(socket.gethostname())

        catter = []

        for letter in x: catter.append(letter)

        appender = ''

        while 1:
            if catter.pop() is not '.':
                pass
            else:
                catter.append('.')
                for val in catter:
                    appender += str(val)

                appender += '0-255'

                break

        return appender

    def _add_hosts(self, ip, port):
        """ Adds a new IP range and its associated known good port that can be used for JarvisServer connections. """

        if self.__hosts_lock.acquire():
            self.Hosts[ip] = port
            self.__hosts_lock.release()

    def _del_hosts(self, ip):
        """ Removes an IP that was known good that is no longer good."""

        if self.__hosts_lock.acquire():
            del self.Hosts[ip]
            self.__hosts_lock.release()

    # TODO Deprecate __socket_builder(). Having the code it performs outside of __init__ is unnecessary.
    def __socket_builder(self):
        """ Initiates all instance socket information. """

        import socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.hostname = socket.gethostname()

        # init networking variables
        self.connections = []
        self.has_scan, self.is_scanning = False, False

    # TODO Deprecate __thread_builder. Having the code it performs outside of __init__ is unnecessary.
    def __thread_builder(self):
        """ Initiates all instance thread information."""

        import threading
        self._threader = threading

        # Initiate threading.Lock objects.
        self.__hosts_lock = threading.Lock()
        self.__connections_lock = threading.Lock()
        self.__print_lock = threading.Lock()

        # Initiate thread resources.
        self.Threads = []

    def __init__(self):
        # TODO Restructure __init__ function.
        """ Initiates JarvisServer. """
        self.initialized = False
        # Initialize socket resources
        self.__socket_builder()

        # Initialize thread resources
        self.__thread_builder()

        self.ThreadKiller = False

        # run initialisation methods
        self.__hostRange = self.__range_finder()
        self.Hosts = {}

        self.initialized = True
        # self.jarvis_finder()
        self.JarvisPort = 5000

        self.num_of_scans = 0

    # Define non-instance variables.
