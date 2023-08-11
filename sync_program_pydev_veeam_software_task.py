import subprocess
import time
import datetime
import sys

def createFolder():
    check_if_exists = "dir {}; exit 0".format(backup_folder)
    try:
        subprocess.run(check_if_exists, shell=True, check=True)  
        remove_command = f'rm -rf "{backup_folder}"'
        subprocess.run(remove_command, shell=True, check=True)
        create_command = f'mkdir "{backup_folder}"'
        subprocess.run(create_command, shell=True, check=True)
        print(f"Folder '{backup_folder}' was succesfully created.")
    except subprocess.CalledProcessError as e:
        print(f"Folder '{backup_folder}' doesn't exist.")

def folderCheck(folder):   
    result = subprocess.check_output("ls -l {0} | {1}; exit 0".format(folder, "awk '{print $9}'"), stderr=subprocess.STDOUT, shell=True)
    result = result.decode("utf-8")
    result = result[1:-1].split('\n')
    return result

def folderSizeCheck(folder):   
    result = subprocess.check_output("ls -l {0} | {1}; exit 0".format(folder, "awk '{print $9, $5}'"), stderr=subprocess.STDOUT, shell=True)
    result = result.decode("utf-8")
    return result

def filesCopy(source_files, backup_files):
    for i in source_files:
        if i not in backup_files:
            type_file = subprocess.check_output("file {}/{}; exit 0".format(source_folder, i), stderr=subprocess.STDOUT, shell=True)
            type_file = type_file.decode("utf-8")
            type_file = type_file.split('\n')
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if 'directory' not in type_file[0]:
                subprocess.call(["cp", "{}/{}".format(source_folder, i), "{}".format(backup_folder)])
                with open(logs_file, "a") as file:
                    file.write(f"{current_time} - File {i} was copied to backup folder.\n")
                print(f"{current_time} - File {i} was copied to backup folder.")
            else:
                subprocess.call(["cp", "-r", "{}/{}".format(source_folder, i), "{}".format(backup_folder)])
                with open(logs_file, "a") as file:
                    file.write(f"{current_time} - Folder {i} was copied to backup folder.\n")
                print(f"{current_time} - Folder {i} was copied to backup folder.")

def filesRemove(source_files, backup_files):
    for i in backup_files:
        if i not in source_files:
            type_file = subprocess.check_output("file {}/{}; exit 0".format(backup_folder, i), stderr=subprocess.STDOUT, shell=True)
            type_file = type_file.decode("utf-8")
            type_file = type_file.split('\n')
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if 'directory' not in type_file[0]:
                subprocess.call(["rm", '-rf', "{}/{}".format(backup_folder, i)])
                with open(logs_file, "a") as file:
                    file.write(f"{current_time} - File {i} was removed from backup folder.\n")
                print(f"{current_time} - File {i} was removed from backup folder.")
            else:
                subprocess.call(["rm", '-rf', "{}/{}".format(backup_folder, i)])
                with open(logs_file, "a") as file:
                    file.write(f"{current_time} - Folder {i} was removed from backup folder.\n")
                print(f"{current_time} - Folder {i} was removed from backup folder.")

def filesUpdate(source_files_size, backup_files_size):
    source_files_size = folderSizeCheck(source_folder)
    backup_files_size = folderSizeCheck(backup_folder)

    source_files_size = source_files_size.split('\n')
    backup_files_size = backup_files_size.split('\n')

    diff = set(backup_files_size) - set(source_files_size)
    if len(diff) > 0:
        for i in diff:
            i = i.split(" ")[0]
            subprocess.call(["cp", "-r", "{}/{}".format(source_folder, i), "{}".format(backup_folder)])
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(logs_file, "a") as file:
                file.write(f"{current_time} - File {i} was updated to backup folder.\n")
            print(f"{current_time} - File {i} was updated to backup folder.")

# Main program

if len(sys.argv) < 5:
    print("Use: python3 <file_name.py> <interval_time> <source_folder> <backup_folder> <logs_file>")
    sys.exit(1)

try:
    interval_time = int(sys.argv[1])
except ValueError:
    print("Interval time argument must be integer!")
    sys.exit(1)

source_folder = sys.argv[2]
if source_folder.endswith("/"):
    print("The source folder path is not correct! Try without '/' at the end.")
    sys.exit(1)

backup_folder = sys.argv[3]
if backup_folder.endswith("/"):
    print("The backup folder path is not correct! Try without '/' at the end.")
    sys.exit(1)

logs_file = sys.argv[4]
if logs_file.endswith("/"):
    print("The logs folder path is not correct! Try without '/' at the end.")
    sys.exit(1)

createFolder()

# check initial states
source_files = folderCheck(source_folder)
backup_files = folderCheck(backup_folder)

source_files_size = folderSizeCheck(source_folder)
backup_files_size = folderSizeCheck(backup_folder)

# make a copy of source_files to backup_files
filesCopy(source_files, backup_files)

while True:
    try:
        # periodical checks
        source_files = folderCheck(source_folder)
        backup_files = folderCheck(backup_folder)

        source_files_size = folderSizeCheck(source_folder)
        backup_files_size = folderSizeCheck(backup_folder)

        if source_files != backup_files:
            if len(source_files) >= len(backup_files) and source_files != ['']: 
                filesCopy(source_files, backup_files)
            elif len(backup_files) >= len(source_files) and backup_files != ['']:
                filesRemove(source_files, backup_files)
        else:
            if source_files_size != backup_files_size:
                filesUpdate(source_files_size, backup_files_size)
        time.sleep(interval_time)
    except Exception as e:
        print('Error: {}'.format(str(e)))
        break



    


