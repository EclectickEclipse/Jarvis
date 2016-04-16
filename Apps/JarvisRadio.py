#! /usr/local/bin/python


class JarvisRadio(object):
    """ Implements basic audio file playback through Unix command options.

    Dependent on Resources.osInteraction.run_cmd() for implementing its interaction with the Unix command line.

    Spawning one SoX.play process at a time, and waiting for its completion to start another, JarvisRadio selects a
    random file from ./Apps/JarvisRadio.r/Music and feeds it to the process.

    Has functions for stopping the current file and play loop, and skipping the current song.

    Spawns a thread for its own Play loop, and uses the Main thread to read input from the user.
    """

    def __init__(self):
        import threading
        self.threader = threading

        self.playable_files = []

        self._supported_extensions = ['mp3']

        self.has_been_played = []
        self.processes = []
        self.__processes_lock = threading.Lock()

        self.radio_killer = False

        self.radio_mode = True
        # self.radio()

    def radio(self):
        self.playable_files = self._build_files_list()
        while not self.radio_killer:
            file_played = self.play_randomly()

            with self.__processes_lock:
                self.processes.append(file_played)

            while file_played[1].poll() is None:
                pass
        else:
            with self.__processes_lock:
                self.stop(self.processes[1])

    @staticmethod
    def play(target, execution=True):
        """ Plays Audio file at location of 'file'.

        Currently does not define the length of the file, requires additional development.

        :param target: A string containing the position of the audio file to be played.
        :param execution: Defaults to True, flagging call to Interaction to wait for execution.
        :returns: The PID of the spawned SoX subprocess, and the length of the file.
        """
        from Resources.osInteraction import Interaction
        log = Interaction.run_cmd('play', args=[target], wait_for_execution=execution)
        import os; os.remove(log[0])
        return log

    def play_next(self):
        """ Stops an currently playing files, and plays the next possible song.

        :returns: A tuple returned from Resources.osInteraction.run_cmd().
        """
        with self.__processes_lock:
            if self.stop(self.processes[1]) is not None:
                from Resources.osInteraction import Interaction
                next_song = self.play_randomly()
                self.processes.append(next_song)

    @staticmethod
    def stop(targets):
        """ Kills the specified 'targets' Popen objects.

        :param targets: A mutable list containing open Popen objects.
        :returns: A mutable list containing Popen objects, or None if there was an exception.
        """

        stopped_processes = []
        while 1:
            try:
                stopped_processes.append(targets.pop().kill())
            except (ValueError, AttributeError):
                return stopped_processes

        return None

    def play_randomly(self):
        """ Plays a file at random from self.playable_files.

        :returns: A tuple returned from Resources.osInteraction.run_cmd().
        """
        import random
        r = random

        random_file = None

        try:
            random_file = self.playable_files.pop((r.randint(0, len(self.playable_files) - 1)))
        except (AttributeError, ValueError):
            # print self.playable_files
            raise ValueError('random_file is still None, could not populate random_file.')

        if random_file is not None:
            while self.has_been_played.count(random_file) > 0:
                random_file = self.playable_files.pop((r.randint(0, (len(self.playable_files) - 1)) - 1))
            else:
                print ('Playing %s' % random_file)
                log = self.play(random_file, False)
                self.has_been_played.append(random_file)

                return log
        else: raise ValueError('random_file is still None, could not populate random_file.')

    def _build_files_list(self):
        """ Builds a list of files that can be played, out of links in ./Jarvis/Resources/Scripts/JarvisRadio.r/Music/.

        Automatically follows any symlinks within the aforementioned folder, and returns a mutable list containing valid
        file positions.

        :returns: A mutable list of valid file positions.
        """

        import os
        usable_files = []

        # First, is ./Apps/ unavailable?
        if not os.access('./Apps/', os.F_OK):
            err_files = {'path': [], 'dirs': [], 'files': []}
            for path, dirs, files in os.walk('./Apps/'):
                err_files['path'].append(path)
                err_files['dirs'].append(dirs)
                err_files['files'].append(files)

            return './Apps/ is unavailable....', err_files

        # Second, is ./Apps/JarvisRadio.r unavailable?
        elif os.access('./Apps/', os.F_OK) and not os.access('./Apps/JarvisRadio.r', os.F_OK):
            path, dirs, files = os.walk('./Apps/').next()
            err_files = {'path': path, 'dirs': dirs, 'files': files}
            return './Apps/ is available, but ./Apps/JarvisRadio.r/ is not available....', err_files

        # Third, is ./Apps/JarvisRadio.r/Music unavailable?
        elif os.access('./Apps/JarvisRadio.r/', os.F_OK) and not os.access('./Apps/JarvisRadio.r/Music/', os.F_OK):
            path, dirs, files = os.walk('./Apps/JarvisRadio.r/').next()
            err_files = {'path': path, 'dirs': dirs, 'files': files}
            return ('./Apps/JarvisRadio.r/ is available, but ./Apps/JarvisRadio.r/Music/ is not available....',
                    err_files)

        # if all these things are true, then perform logic to find out what files are available for playing.
        else:
            for path, dirs, files in os.walk('./Apps/JarvisRadio.r/Music/', followlinks=True):
                for file_name in files:
                    for extension in self._supported_extensions:
                        if file_name.count(extension) > 0:
                            usable_files.append(os.path.join(path, file_name))
            return usable_files

    @staticmethod
    def _add_to_library(target, name):
        """ Creates a new Symlink to the 'target' folder with 'name' in the JarvisRadio Music folder..

        :param target: A valid file path.
        :param name: A unique name for the new link.
        :returns: The created Symlink's path.
        """
        import os
        if os.access(target, os.F_OK):
            if name[-1] is '/':
                destination = os.getcwd() + str(name)
                os.symlink(target, destination, target_is_directory=True)
                return destination
            else:
                destination = os.getcwd() + str(name) + '/'
                os.symlink(target, destination, target_is_directory=True)
                return destination


class Scratchpad(JarvisRadio):

    def run(self):
        print (self._build_files_list)

    @staticmethod
    def arg_parser():
        """ Parses arguments given to the program on execution. """
        import argparse
        parser = argparse.ArgumentParser(description='Plays audio with minimal system requirements.')
        parser.add_argument('--RPI', help='Include this flag in program execution to enable execution with Raspberry '
                                          'Pi GPIO Pin accessibility.', action='store_true')
        args = parser.parse_args()
        if args.RPI:
            pass  # run with GPIO support.

    @staticmethod
    def remove_from_library(destination):
        """ Removes a Symlink with 'name' from ./Jarvis/Resources/Scripts/JarvisRadio.r/Music/.

        :param destination: The name of the Symlink to be removed.
        :returns: A boolean indicating if the Symlink was removed.
        """
        # target = name

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--documentation', help='Simply outputs the functionality of '
                                                      'this App to the stdout', action='store_true')
    parsed_args = parser.parse_args()

    if parsed_args.documentation:
        print('Plays media files that are either contained or linked to ./JarvisRadio.r/Music/.')
        quit()

    def run():
        import threading
        x = JarvisRadio()
        t = threading.Thread(target=x.radio(), name='JarvisRadio_random')
        t.daemon = True
        t.start()
        return x
    x = run()
    input('Press enter to quit!')
    x.Killer = True
