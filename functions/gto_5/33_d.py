def function5(a = 1, b = 2):
    return a + b

def function6():
    return function5(a, b)

print(function6(2, 3))