#! /usr/local/bin

import os
import subprocess
import tempfile

from Resources.Libraries import Library

library_name = 'JarvisTMPFILES'

# TODO Restructure Interaction() to be better outfitted for co routines.


class Interaction:
    # TODO Define a method to pass control of a process back to the main process.
    # TODO Define a thread independent (coroutine structured) runtime to increase runtime stability.
    """ Securely handles scripts executable by the current user executing Jarvis.

    Due to the possibility of the user changing what file is executed and the current open restrictions on which files
    can be executed entirely, it poses a possible security threat. To help ensure privacy and security, Interaction
    uses a NamedTemporaryFile, and returns to the calling method said file. The calling method can then read the file to
    actively read the STDOUT/ERR of the executed script. Once this file is closed, it is automatically destroyed.
    """

    def __init__(self):
        self.tempfile_list = self.populate_list()

    @staticmethod
    def populate_list():
        """ Builds a list of open temporary files or creates a new Library.

        :return: Either a list of open temporary files or an empty mutable list.
        """
        exists = Library.check_library(library_name)
        if exists:
            return Library.unpack_libraries(library_name).pop()
        else:
            sys.stderr.write('osInteraction could load its library! Creating new library!')
            Library.pickle_libraries([[]],library_name)
            return []

    def cleanup(self):
        """ Goes through internal list of open temporary files, and deletes them.

        :return: None
        """
        for tempfile in self.tempfile_list:
            os.remove(tempfile)

        self.tempfile_list = []
        Library.pickle_libraries([[]], library_name)

    def update_list(self):
        self.tempfile_list = self.populate_list()

    @staticmethod
    def run(script, args=None, kwargs=None, timer=0, log=None, verbose=False,
            wait_for_execution=False):
        """ Runs a script with STDOUT/ERR redirection.

        :param kwargs: Optional flag arguments.
        :param script: Location of the script to run.
        :param args: Optional list of [arguments]. Defaults to None.
        :param timer: Optional amount of time to wait. Defaults to 0.
        :param log: STDOUT/STDERR redirection output location. Defaults to a Named Temporary File.
        :param verbose: A flag for verbose output.
        :param wait_for_execution: If True, waits for the Popen thread to complete execution before returning.

        :returns: The file postion of a TempFile object. To ensure security, this file must be closed.
        """

        # TODO Define parameters of sleeper in DocString.
        def sleeper(xtimer, process, wait):
            """Runs a thread to sleep and then kill whatever Popen object is passed to it.

            :param xtimer: The amount of time in seconds to wait before killing the process.
            :param process: The process to be killed.
            :param wait: Flags a wait for the process to execute.

            :returns: True if the process has been killed.
            """
            import time
            time.sleep(xtimer)
            process.kill()
            if wait:
                while process.poll is None:
                    pass
            if process.poll() is not None:
                return True
            else:
                return False

        log_file = None

        import os
        if log is None:
            x = tempfile.NamedTemporaryFile(mode='w+', delete=False)
            log_file = open(x.name, 'w+')
        elif type(log) is str and os.access(log, os.F_OK):
            log_file = open(log, 'w+')
        elif type(log) is str and not os.access(log, os.F_OK):
            log_file = open(log, 'w+')
        else:
            raise ValueError("log parameter must be str")

        argument = [str(script)]

        if kwargs is not None and type(kwargs) is list:
            for term in kwargs:
                argument.append(str(term))
        elif kwargs is not None and type(kwargs) is str:
            argument.append(kwargs)
        if args is not None and type(args) is list:
            for term in kwargs:
                argument.append(str(term))
        elif args is not None and type(args) is str:
            argument.append(args)

        if verbose:
            print('run_cmd:')
            print({'current directory': os.getcwd(), 'argument': argument, 'file': log})

        if log_file is None:
            raise ValueError
        else:
            p = subprocess.Popen(argument, stdout=log_file, stderr=log_file)
            if timer > 0 and not wait_for_execution:
                import threading
                t = threading.Thread(target=sleeper, args=(timer, p, wait_for_execution))
                t.daemon = True
                t.start()
            elif timer is 0 and wait_for_execution:
                while p.poll() is None:
                    pass

            import time

            if verbose:
                time.sleep(0.5)
                print ('Reading %s ' % str(log_file))
                with open(log_file.name) or log_file as f_log:
                    read = f_log.read()
                    print(read)
                    if read.count('\n') is 1 and len(read) is 0:
                        raise ValueError('Could not read output from PIPE. Got \\n from %s.' % f_log)
                    elif len(read) is 0:
                        raise ValueError('Could not read output from PIPE. Got a blank file stream from %s.' % f_log)

            return log_file.name, p

    @staticmethod
    def run_cmd(cmd, args=None, kwargs=None, timer=0, log=None, verbose=False,
                wait_for_execution=False):
        """ Runs a Unix command with STDOUT/ERR redirerction and optional support for additional arguments.

        :param kwargs: Additional optional flag arguments. Defaults to None.
        :param cmd: Unix command to run.
        :param args: Additional optional arguments. Defaults to None.
        :param timer: Optional amount of time to wait. Defaults to 0.
        :param log: STDOUT/STDERR redirection output location. Defaults to a Named Temporary File.
        :param verbose: A flag for verbose output.
        :param wait_for_execution: If True, waits for the Popen thread to complete execution before returning.

        :returns: The file postion of a TempFile object, PIPE object. To ensure security, this file must be closed.
        """

        # TODO Define parameters of sleeper in DocString.
        def sleeper(xtimer, process, wait):
            """Runs a thread to sleep and then kill whatever Popen object is passed to it.

            :param xtimer: The amount of time in seconds to wait before killing the process.
            :param process: The process to be killed.
            :param wait: Flags a wait for the process to execute.

            :returns: True if the process has been killed.
            """
            import time
            time.sleep(xtimer)
            process.kill()
            if wait:
                while process.poll is None:
                    pass
            if process.poll() is not None:
                return True
            else:
                return False

        log_file = None

        if log is None:
            x = tempfile.NamedTemporaryFile(mode='w+', delete=False)
            log_file = open(x.name, 'w+')
        elif type(log) is str and os.access(log, os.F_OK):
            log_file = open(log, 'w+')
        elif type(log) is str and not os.access(log, os.F_OK):
            log_file = open(log, 'w+')
        else:
            raise ValueError("log parameter must be str")

        argument = [str(cmd)]

        if kwargs is not None and type(kwargs) is list:
            for term in kwargs:
                argument.append(str(term))
        elif kwargs is not None and type(kwargs) is str:
            argument.append(kwargs)
        if args is not None and type(args) is list:
            for term in args:
                argument.append(str(term))
        elif args is not None and type(args) is str:
            argument.append(args)

        import subprocess

        if verbose:
            print('run_cmd:')
            print({'current dir': os.getcwd(), 'argument': argument, 'log file': log_file})

        p = subprocess.Popen(argument, stdout=log_file, stderr=log_file)
        if timer > 0 and not wait_for_execution:
            import threading
            t = threading.Thread(target=sleeper, args=(timer, p, wait_for_execution))
            t.daemon = True
            t.start()
        elif timer is 0 and wait_for_execution:
            while p.poll() is None:
                pass

        import time

        if verbose:
            while 1:
                try:
                    time.sleep(0.2)
                    break
                except UnboundLocalError:
                    import time
            print ('Reading %s ' % str(log_file))
            with open(log_file.name) as f_log:
                read = f_log.read()
                print(read)
                if read.count('\n') is 1 and len(read) is 0:
                    raise ValueError('Could not read output from PIPE. Got \\n from %s.' % f_log)
                elif len(read) is 0:
                    raise ValueError('Could not read output from PIPE. Got a blank file stream from %s.' % f_log)

        return log_file.name, p

        # return None

    def run_clean(self, *args):
        """ Tracks any open temporary files and passes through the return of osInteraction.run()

        Using this method enables closure of any generated temporary files with osInteraction.cleanup()

        :param args: Passthrough arguments for osInteraction.run()
        :return: The return recieved by osInteraction.run()
        """
        retu = self.run(*args)
        self.tempfile_list.append(retu[0])
        return retu

    def run_cmd_clean(self, *args):
        """ Tracks any open temporary files and passes through the return of osInteraction.run()

        Using this method enables closure of any generated temporary files with osInteraction.cleanup()

        :param args: Passthrough arguments for osInteraction.run_cmd()
        :return: The return received by osInteraction.run_cmd()
        """
        retu = self.run(*args)
        self.tempfile_list.append(retu[0])
        return retu

if __name__ == '__main__':
    import sys
    import time

    sys.stdout.writelines('Loading osInteraction')

    log = Interaction.run_cmd('echo', args=['Hello World from Jarvis.Resources.osInteraction!'])

    while log[1].poll() is None:
        sys.stdout.writelines('.')
        time.sleep(0.05)
    else:
        with open(log[0]) as f:
            for line in f:
                print ('\n\n' + line.split('\n')[0])

            f.close()
        with open(log[0]):
            pass
