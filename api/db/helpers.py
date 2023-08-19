import os

def find_project_root():
    current_path = os.getcwd()
    while not os.path.isfile(os.path.join(current_path, 'LICENSE')):
        current_path = os.path.dirname(current_path)
    return current_path

root = find_project_root()

if __name__ == '__main__':
    print(find_project_root())
