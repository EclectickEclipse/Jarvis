#! /usr/local/bin/python


class Library:
    """ Provides data persistence standardization to Jarvis.

    Provides methods to create, modify, load, and check for availability of Libraries.

    Libraries in this file is used to describe any data used to populate a '.jarv' file with pickle.

    :build_library: Populates a Library object with keys by values. ** DEPRECATED !!!**
    :pickle_libraries: Takes a list of objects and pickles a new Library with each object in the list.
    :unpack_libraries: Takes a name of a library and returns its contents in a list.
    :check_library: Takes a name of a library and returns True if it exists.
    """

    def __init__(self):
        pass

    # Deprecated
    @staticmethod
    def build_library(library, keys, values):
        for x, y in zip(keys, values):
            library[str(x)] = y

    @staticmethod
    def pickle_libraries(libraries, library_name, path='./Libs/'):
        """ Unpacks a list of libraries and saves them as the specified 'library_name'.

        :rtype: str
        :param libraries: A mutable list of data values to be stored into a '.jarv' file.
        :param library_name: The name used for the '.jarv' file. Algorithm cats '.jarv' to the end of 'library_name'
        :param path: The path where pickle_libraries saves the '.jarv' file. Defaults to './Libs/'

        :returns: The path of the '.jarv' file.
        """
        import pickle
        x, completed = str(path) + str(library_name) + '.jarv', False

        # Ensure proper directory

        # Dump 'libraries' into path at x.
        outfile = open(x, 'wb')
        while not completed:
            try:
                pickle.dump(libraries.pop(), outfile)
            except IndexError:
                completed = True
                break
        outfile.close()

        return x

    @staticmethod
    def unpack_libraries(library_name, path='./Libs/'):
        """ Loads pickled libraries and returns them in a list.

        :param library_name: The name of the '.jarv' file to be loaded. Automatically concatenates the file extension.
        :param path: The path of the folder where the '.jarv' file is located. Defaults to './Libs/'

        :returns: A mutable list containing all pickled information in the '.jarv' file.
        """
        import pickle

        infile, completed, x = open((path + library_name + '.jarv'), 'rb'), False, []
        while not completed:
            try:
                x.append(pickle.load(infile))
            except EOFError:
                completed = True
        infile.close()

        return x

    @staticmethod
    def check_library(library_name, path='./Libs/'):
        """ Checks to see if 'library_name' exists.

        :param library_name: The name of the library to check for.
        :param path: The path containing the library. Defaults to ./Libs/
        :return: A boolean signifying whether or not the library exists.
        """
        import os

        file_path = os.path.join(path, (library_name + '.jarv'))

        if os.access(file_path, os.F_OK):
            return True
        else:
            return False
