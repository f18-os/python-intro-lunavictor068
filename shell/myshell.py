#!/usr/bin/env python3

import os
import sys
import re
import fileinput
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
    if len(user_commands) > 0:
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
        index = input_redirect(command_list)
    elif operation is ">":
        index = output_redirect(command_list)
    elif operation is "|":
        index = pipe(command_list)
    elif operation is "&":
        index = command_list.index(operation)
        print("performing &")
    else:
        index = command_list.index(operation)
    return index


def output_redirect(command_list):
    index = command_list.index(">")
    list_input = command_list[:index + 2]
    index = list_input.index(">")
    file = list_input[index + 1]
    command = list_input[:index]
    # with help from
    # https://stackoverflow.com/questions/47719965/how-to-redirect-stdout-to-a-file-and-then-restore-stdout-back
    # open
    f = open(file, "w+")
    saved = os.dup(1)
    os.close(1)
    os.dup(f.fileno())
    os.dup2(f.fileno(), sys.stdout.fileno())
    os.close(f.fileno())
    # execute command
    if len(command) > 0:
        execute(command)
    # restore
    sys.stdout.flush()
    os.dup2(saved, 1)
    os.close(saved)
    return index + 1


def input_redirect(command_list):
    index = command_list.index("<")
    list_input = command_list[:index + 2]
    index = list_input.index("<")
    file = list_input[index + 1]
    command = list_input[:index]
    # with help from
    # https://stackoverflow.com/questions/21568810/how-do-i-redirect-input-and-output-with-pycharm-like-i-would-on-the-command-line
    # open
    f = open(file, "r")
    saved = os.dup(0)
    os.close(0)
    os.dup(f.fileno())
    os.dup2(f.fileno(), sys.stdin.fileno())
    os.close(f.fileno())
    # execute command
    if len(command) > 0:
        execute(command)
    # restore
    sys.stdin.flush()
    os.dup2(saved, 0)
    os.close(saved)
    return index + 1


def pipe(command_list):
    index = command_list.index("|")
    command_left = command_list[:index]
    command_right = command_list[index + 1:]
    print("command_left: " + str(command_left))
    print("command_right: " + str(command_right))
    pid = os.getpid()  # get and remember pid

    pr, pw = os.pipe()
    for f in (pr, pw):
        os.set_inheritable(f, True)
    print("pipe fds: pr=%d, pw=%d" % (pr, pw))
    print("About to fork (pid=%d)" % pid)

    rc = os.fork()

    if rc < 0:
        print("fork failed, returning %d\n" % rc, file=sys.stderr)
        sys.exit(1)

    elif rc == 0:  # child - will write to pipe
        # print("Child: My pid==%d.  Parent's pid=%d" % (os.getpid(), pid), file=sys.stderr)
        # args = ["cat", "hello"]
        #
        # os.close(1)  # redirect child's stdout
        # os.dup(pw)
        # os.close(pw)
        # # for fd in (pr, pw):
        # #     os.close(fd)
        # execute(command_left)
        saved = os.dup(1)
        os.close(1)
        # os.dup(pw)
        os.dup2(pw, sys.stdout.fileno())
        os.close(pw)
        os.close(pr)
        # execute command
        if len(command_left) > 0:
            execute(command_left)
        # restore
        os.dup2(saved, 1)
        os.close(saved)
    else:  # parent (forked ok)
        # print("Parent: My pid==%d.  Child's pid=%d" % (os.getpid(), rc), file=sys.stderr)
        # os.close(0)
        # os.dup(pr)
        # os.close(pr)
        # # for fd in (pw, pr):
        # #     os.close(fd)
        # execute(command_right)

        saved = os.dup(0)
        os.close(0)
        # os.dup(pr)
        os.dup2(pr, sys.stdin.fileno())
        os.close(pr)
        os.close(pw)
        # execute command
        if len(command_right) > 0:
            execute(command_right)

        # restore
        sys.stdout.flush()
        sys.stdin.flush()
        os.dup2(saved, 0)
        os.close(saved)

        child_pid, exit_code = os.wait()
    return len(command_list)






def background():
    print("output redirect")


if __name__ == "__main__":
    main()

# test_command = "fsadf < sadfdsfds > fsafsafsd | ssaffasfsda | safafafa | sadfasfds & fasfssd"
# performs(test_command.split(" "))

