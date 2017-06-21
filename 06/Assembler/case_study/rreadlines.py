fo = open("sample.txt", "r")
print("Name of the file: ", fo.name, fo.mode)

first_read = fo.read()
second_read = fo.read()
print(first_read)
print(second_read)
