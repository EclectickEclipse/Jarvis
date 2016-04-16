#! /usr/local/bin/python

import threading

from Resources.osInteraction import Interaction


class JarvisSweep:

    def __init__(self,address='172.16.1.'):
        self.results_lock = threading.Lock()
        self.threads = []

        self.ip_address = address
        self.hosts = list(range(255))

        self.results = {
            'success': [0, []],
            'failure': [0, []]
        }
        self.hosts_numeric_total = 25500

        self.total = 0

    def sweep(self):
        """ Pings a list of hosts and determines if they are up. Spawns threads to ensure efficiency.

        :return: A dictionary containing the results.
        """
        # Main body below
        def ping_sweep(host_list):

            for target in host_list:
                log = Interaction.run_cmd('ping', [self.ip_address + str(target)], ['-c 1', '-t 1'])
                while log[1].poll() is None:
                    pass
                else:
                    if log[1].poll() is 0:
                        with self.results_lock:
                            self.results['success'][0] += 1
                            self.results['success'][1].append(self.ip_address + str(target))
                    elif log[1].poll() is 2:
                        with self.results_lock:
                            self.results['failure'][0] += 1
                            self.results['failure'][1].append(self.ip_address + str(target))

        list_of_hosts = []

        # Create lists of unique hosts and populate a list of threads waiting to start.
        for value in self.hosts:
            # populate a list
            if len(list_of_hosts) is not 15:
                list_of_hosts.append(value)
            # if list is 15 hosts long, populate thread.
            elif len(list_of_hosts) is 15:
                t = threading.Thread(target=ping_sweep, args=(list_of_hosts,))  # Add thread object to self.threads list.
                t.daemon = True
                self.threads.append(t)
                list_of_hosts = [value]
            elif value is self.hosts[:-1]:  # if at the end of the list
                list_of_hosts.append(value)
                t = threading.Thread(target=ping_sweep, args=(list_of_hosts,))
                t.daemon = True
                self.threads.append(t)

        # Start threads.
        for thread in self.threads:
            thread.start()

        # Wait for threads to finish execution.
        for thread in self.threads:
            while thread.is_alive():
                pass

        # Calculate percentage up and down.
        self.results['success'].append((1.0 * self.results['success'][0] / self.hosts_numeric_total) * 100)
        self.results['failure'].append((1.0 * self.results['failure'][0] / self.hosts_numeric_total) * 100)
        # Uncomment if you want the module to automatically output percentage up/down.
        # print '%s percent up, %s percent down.' % (str(round(self.results['success'][2], 2))
        #                                            , str(round(self.results['failure'][2], 2)))
        return self.results

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--documentation', help='Simply outputs the functionality of '
                                                      'this App to the stdout', action='store_true')
    parsed_args = parser.parse_args()

    if parsed_args.documentation:
        print('Spawns a series of threads that each ping a remote host once, and prints a short bit of information',
              'about what hosts are up or down and the percentage hit.')
        quit()

    try:
        js = JarvisSweep('169.254.200.')
        print (js.sweep()['success'])
        jsx = JarvisSweep()
        print (jsx.sweep()['success'])
    except:
        from Apps.JarvisSpeaker import JarvisSpeaker
        JarvisSpeaker.say('failure')

    from Apps.JarvisSpeaker import JarvisSpeaker
    JarvisSpeaker.say('done')
