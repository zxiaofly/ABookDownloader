import os
def safe_mkdir(dir):
    try:
        os.mkdir(str(dir))
    except FileExistsError:
        pass


def safe_remove(dir):
    try:
        os.remove(str(dir))
    except FileNotFoundError:
        pass