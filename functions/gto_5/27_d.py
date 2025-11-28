def function5(a, b):
    return a + b

def function6(a = 1, b = 2):
    return function5(a, b)

print(function6(b = 3))