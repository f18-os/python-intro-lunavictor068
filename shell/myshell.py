import os
import sys
import re
# import os
#
# user_input = input()
# list_input = user_input.split()
# print(list_input)
# command = None
# arguments = None
# file = None
# # Not enough arguments
# if len(list_input) < 2:
#     print("More than 2 arguments needed")
#     exit()
# index = list_input.index(">")
# # input has at least a file
# if len(list_input) > 1:
#     file = list_input[index + 1]
# # input has a command
# if len(list_input) > 2:
#     command = list_input[0]
# # input has arguments
# if len(list_input) > 3:
#     arguments = list_input[:index]
#
# print("command: {}".format(command))
# print("arguments: {}".format(arguments))
# print("file: {}".format(file))
#
# for directory in re.split(":", os.environ['PATH']): # try each directory in the path
#     program = "%s/%s" % (directory, command)
#     os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
#     try:
#         os.execve(program, arguments, os.environ) # try to exec program
#     except FileNotFoundError:             # ...expected
#         pass                              # ...fail quietly
    # os.close(1)

# perform(argument)
# 	if( no more operations in argument)
# 		exit
# 	else
# 		get next operation
# 		index of last operation = perform operation
# 		perform(argument starting at index of last operation)
#
# Perform operation(argument)
# 	perform required operation
# 	return index of operation


def main():
    while True:
        # default prompt is $
        prompt = "$"
        if "ps1" in os.environ:
            prompt = os.environ["ps1"]
        # Get commands from user
        user_commands = input(prompt + " ").split(" ")
        # change directory
        if len(user_commands) > 1 and user_commands[0] is "cd":
            os.chdir(user_commands[1])
        # other commands
        else:
            # performs deletes parts of user_commands it has used.
            performs(user_commands)
            execute(user_commands)


def execute(user_commands):
    rc = os.fork()
    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:
        command_found = False
        for directory in re.split(":", os.environ['PATH']):  # try each directory in the path
            program = "%s/%s" % (directory, user_commands[0])
            os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
            try:
                os.execve(program, user_commands, os.environ)  # try to exec program
                command_found = True
            except FileNotFoundError:  # ...expected
                pass  # ...fail quietly
        if not command_found:
            os.write(2, ("Child:    Could not exec %s\n" % user_commands[0]).encode())
            sys.exit(1)  # terminate with error
    else:
        child_pid, exit_code = os.wait()
        os.write(1, ("Program terminated with exit code %d\n" %
                     exit_code).encode())


shell_commands = ['>', '<', '|', '&']


def performs(command_list):
    # Check if command_string contains a shell_command
    # from stackoverflow.com/questions/30020184/how-to-find-the-first-index-of-any-of-a-set-of-characters-in-a-string
    operation = next((argument for argument in command_list if argument in shell_commands), None)
    if operation is not None:
        last_operation_index = perform(operation, command_list)
        del command_list[:last_operation_index + 1]
        performs(command_list)


def perform(operation, command_list):
    print(str(operation) + " " + str(command_list))
    index = None
    if operation is "<":
        index = 1
        print("performing <")
    elif operation is ">":
        index = 1
        print("performing >")
    elif operation is "|":
        index = 1
        print("performing |")
    elif operation is "&":
        index = 1
        print("performing &")
    else:
        index = 1
    return command_list.index(operation)


def output_redirect():
    print("output redirect")


def input_redirect():
    print("output redirect")


def pipe():
    print("output redirect")


def background():
    print("output redirect")


if __name__ == "__main__":
    main()

# test_command = "fsadf < sadfdsfds > fsafsafsd | ssaffasfsda | safafafa | sadfasfds & fasfssd"
# performs(test_command.split(" "))

