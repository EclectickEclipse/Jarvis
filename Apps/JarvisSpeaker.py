#! /usr/local/bin/python


class JarvisSpeaker:
    """ Provides Speech functions for Jarvis.

    Maintains a persistent library of statements, and methods to interact with it.

    :say (term=str, wait_time=int, execution=bool): Uses Speech modules to say the given term.
    :respond (wait_time=int, execution=bool): Gets a random statement from self.responses and passes it to self.say().
    :add_statement (statements=list, key=str): Adds a new response to self.responses. Omit key and it automatically creates the key.
    :remove_statement (statements=list, key=str): Removes the given key from self.responses.
    :cleanup (library_name=str): Creates a library out of self.responses. Omit library_name to use 'JarvisSpeech'.
    """

    def __init__(self, keys_path=None, values_path=None):
        """ Loads the JarvisSpeech Library, and parses commandline options.

        :param keys_path: An optional file containing keys in topdown order, one per file. Passes to __init__.build_jarvis_speech()
        :param values_path: An optional file containing values in topdown order, one per file. Passes to __init__.build_jarvis_speech()
        :returns: A new JarvisSpeaker object.
        """

        import argparse
        import os

        # move to base jarvis folder
        # os.chdir('..')

        parser = argparse.ArgumentParser(description='Uses MacOSx\'s builtin speech engine to say statements.')
        parser.add_argument('--keysfile', help='The path of the file to populate keys with.', type=str)
        parser.add_argument('--valuesfile', help='The path of the file to populate the values with.')
        args = parser.parse_args()

        self.statements = None

        def load_library():
            """ Attempts to load the JarvisSpeech Library.

            :returns: A dictionary built from the loaded JarvisSpeech Library.
            """
            from Resources.Libraries import Library
            try:
                if Library.check_library('JarvisSpeech'):
                    return Library.unpack_libraries('JarvisSpeech').pop()
                else:
                    raise IOError
            except (OSError, IOError, EOFError):
                return {'acknowledge': ['Yes', 'Of Course', 'Of course boss', 'Whatever you say.']}

        def build_jarvis_speech(keys_pathx, values_pathx):
            """ Loads responses in order top down by line from files designated with keys_path and values_path

            :param keys_pathx: The path of the file containing keys to load.
            :param values_pathx: The path of the file containing values to load.
            :returns: Returns a dictionary built with keys and values from provided files.
            """
            response_dict = {}

            keys_file = open(keys_pathx)
            keys = []
            for line in keys_file:
                keys.append(line.strip('\n'))

            values_file = open(values_pathx)
            values = []
            for line in values_file:
                values.append(line.strip('\n'))

            for key, value in zip(keys, values):
                response_dict[key] = value
            return response_dict

        if (args.keysfile and args.valuesfile is not None) or (keys_path and values_path is not None):
            if os.access(args.keysfile, os.F_OK) and os.access(args.valuesfile, os.F_OK):
                self.statements = build_jarvis_speech(args.keysfile, args.valuesfile)
            else:
                self.statements = load_library()
        else:
            self.statements = load_library()

        self.__last_statement = ''

        self.cleanup()

    @staticmethod
    def say(term, wait_time=0, execution=False):
        """ Uses MacOSx's built in text to speech engine to say term.

        :param term: The statement to make via MacOSx speech module.
        :param wait_time: The amount of time to wait for the statement to complete. Defaults to 0
        :param execution: If True, waits for the Popen thread to complete execution before returning.

        :returns: A tuple returned by Resources.osInteraction.Interaction.run_cmd().
        """

        from Resources.osInteraction import Interaction

        argument = 'say'
        term = [term]

        log = Interaction.run_cmd(argument, args=term, timer=wait_time, wait_for_execution=execution)
        import os; os.remove(log[0])

        return log

    def respond(self, wait_time=0, execution=False):
        """ Uses a randomly generated statement from self.responses to automatically respond to the user.

        :param wait_time: The amount of time to wait for the statement to complete. Defaults to 0
        :param execution: If True, waits for the Popen thread to complete execution before returning.

        :returns: A tuple returned by Resources.osInteraction.Interaction.run_cmd(). Returns None if unable to run say.
        """
        import random
        r = random

        responses_list = self.statements['acknowledge']

        log = None

        while 1:
            statement = responses_list[r.randint(0, (len(responses_list) - 1))]

            if statement is self.__last_statement:
                pass
            else:
                self.__last_statement = statement
                log = self.say(statement, wait_time, execution)
                break

        return log

    def add_statement(self, statements, key='acknowledge'):
        """ Adds a new response to self.responses. Generates automatic key values.

        :param statements: A list of values to be added to self.responses.
        :param key: The key to be added to self.responses. Defaults to 'acknowledge'.
        :returns: self.responses.
        """
        if key is 'acknowledge':
            while 1:
                try:
                    self.statements[key].append(statements.pop())
                except (IndexError, ValueError):
                    break
        else:
            try:
                if type(self.statements[key]) is list:
                    while 1:
                        try:
                            self.statements[key].append(statements.pop())
                        except (IndexError, ValueError):
                            break
                else:
                    raise ValueError('Key position is used.')
            except KeyError:
                self.statements[key] = statements

        self.cleanup()

        return self.statements

    def remove_statement(self, statements, key='acknowledge'):
        """ Removes a field from self.responses by the key entry.

        :param statements: A list of responses to be removed.
        :param key: The key from which to remove statements. Defaults to 'acknowledge'
        :returns: The value of the field removed. Returns None if it could not remove the field.
        """
        try:
            removed_value = self.statements[key].pop(self.statements[key].index(statements))
        except (IndexError, ValueError):
            self.cleanup()
            return None

        self.cleanup()
        return removed_value

    def cleanup(self, library_name='JarvisSpeech'):
        """ Pickles self.responses to ensure data persistence of responses module.

        :param library_name: The name of the library to be pickled. Defaults to JarvisSpeech.
        :returns: The path of the Library that was pickled.
        """
        from Resources.Libraries import Library
        log = Library.pickle_libraries([self.statements], library_name)

        return log

    def get_statements(self):
        """ Simply returns the working statements dictionary.

        :return: self.statements
        """

        return self.statements

if __name__ == '__main__':
    # Handle documentation grabs.
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--documentation', help='Simply outputs the functionality of '
                                                      'this App to the stdout', action='store_true')
    parser.add_argument('-s', '--statement', help='An optional statement to say.', type=str)
    parsed_args = parser.parse_args()

    if parsed_args.documentation:
        import sys
        sys.stdout.writelines('Uses MacOSx\'s builtin Text to Speech to enable vocal feedback to users using machines ' +
                              'that do not have a screen to work with. This module is intended to be used for internal' +
                              ' use of Jarvis, but has use to third party developers.')
        quit()

    if parsed_args.statement is not None:
        log = JarvisSpeaker.say(parsed_args.s)
        quit()

    import time
    import sys

    log = JarvisSpeaker.say('Hello world from Jarvis Speaker!')

    sys.stdout.writelines('Loading JarvisSpeaker')
    while log[1].poll() is None:
        sys.stdout.writelines('.')
        time.sleep(0.5)
    else:
        log[0].close()
