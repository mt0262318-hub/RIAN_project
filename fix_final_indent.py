with open("main.py", "r") as f:
    content = f.read()

# Sabhi tabs ko 4 spaces me convert karna taaki indentation mix-up khatam ho jaye
content = content.replace("\t", "    ")

with open("main.py", "w") as f:
    f.write(content)

print("SUCCESS: All tabs converted to uniform 4 spaces across main.py!")
