def function5(a, b):
    return a + b

def function6(a=6, b=5):
    return function5(2, b)

print(function6(a = 3))