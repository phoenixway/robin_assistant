import os
import logging
import shutil


log = logging.getLogger('pythonConfig')


def folder_exists(folder):
    return os.path.exists(folder) and os.path.isdir(folder)


def folder_empty(folder):
    return os.listdir(folder) == []


def assure_exists(folder, init_func):
    if folder_exists(folder):
        if folder_empty(folder):
            init_func(folder)
    else:
        try:
            os.makedirs(folder)
            log.debug(f"Created directory: {folder}")
        except Exception as e:
            log.error(f"Error creating directory: {folder}, exception: {e}")
        init_func(folder)


def copy_file(source_file, destination_directory):
    # Get the full paths of the source file and destination directory
    source_path = os.path.abspath(source_file)
    destination_path = os.path.abspath(destination_directory)

    # Check if the source file exists
    if not os.path.isfile(source_path):
        print(f"Source file '{source_file}' does not exist.")
        return

    # Check if the destination directory exists, create it if not
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    # Construct the full path for the destination file
    destination_file = os.path.join(destination_path, os.path.basename(source_file))

    try:
        # Copy the file from source to destination
        shutil.copy(source_path, destination_file)
        log.debug(f"File '{source_file}' copied to '{destination_file}' successfully.")
    except Exception as e:
        log.error(f"Failed to copy file '{source_file}' to '{destination_file}': {e}")


def copy_contents(source_directory, destination_directory):
    # Get the full paths of the source and destination directories
    source_path = os.path.abspath(source_directory)
    destination_path = os.path.abspath(destination_directory)

    # Check if the source directory exists
    if not os.path.exists(source_path):
        print(f"Source directory '{source_directory}' does not exist.")
        return

    # Check if the destination directory exists, create it if not
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    try:
        # Copy the contents of the source directory recursively to the destination
        for root, dirs, files in os.walk(source_path):
            relative_path = os.path.relpath(root, source_path)
            destination_dir = os.path.join(destination_path, relative_path)

            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)

            for file in files:
                source_file = os.path.join(root, file)
                destination_file = os.path.join(destination_dir, file)
                shutil.copy(source_file, destination_file)

        log.debug(f"Contents of '{source_directory}' copied to '{destination_directory}' successfully.")
    except Exception as e:
        log.error(f"Failed to copy contents of '{source_directory}' to '{destination_directory}': {e}")


def init_brains(brains_path):
    script_path = os.path.abspath(__file__)
    script_directory = os.path.dirname(script_path)
    default_brains_path = os.path.join(script_directory, 'default_brains')
    copy_contents(default_brains_path, brains_path)


def init_plugins(path):
    script_path = os.path.abspath(__file__)
    script_directory = os.path.dirname(script_path)
    default_path = os.path.join(script_directory, 'default_plugins')
    copy_contents(default_path, path)


def init_root(path):
    pass


def init_config():
    home_folder = os.path.expanduser("~")
    robin_config_path = os.path.join(home_folder, '.config/robin_assistant')
    assure_exists(robin_config_path, init_root)
    brains_path = os.path.join(robin_config_path, 'brains')
    assure_exists(brains_path, init_brains)
    plugins_path = os.path.join(robin_config_path, 'plugins')
    assure_exists(plugins_path, init_plugins)
    return {
        'config_path': robin_config_path,
        'brains_path': brains_path,
        'plugins_path': plugins_path,
    }
