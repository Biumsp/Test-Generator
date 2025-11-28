def function5(a, b):
    print("a + b")
    return a + b

def function6(a = 1, b = 2):
    print("a + b")
    return function5(a, b)

print(function6())