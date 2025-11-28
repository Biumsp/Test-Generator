def function5(a, b):
    return a + b
    print("a + b")

def function6(a = 1, b = 2):
    return function5(a, b)

print(function5(1, 3))