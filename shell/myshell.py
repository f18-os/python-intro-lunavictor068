user_input = input()
list_input = user_input.split()
print(list_input)
command = None
arguments = None
file = None
# Not enough arguments
if len(list_input) < 2:
    print("More than 2 arguments needed")
    exit()
index = list_input.index(">")
# input has at least a file
if len(list_input) > 1:
    file = list_input[index + 1]
# input has a command
if len(list_input) > 2:
    command = list_input[0]
# input has arguments
if len(list_input) > 3:
    arguments = list_input[1:index]

print("command: {}".format(command))
print("arguments: {}".format(arguments))
print("file: {}".format(file))
