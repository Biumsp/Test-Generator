def function5(a = 4, b = 5):
    return a + b

def function6(a=6, b=5):
    return function5(a = a, b = b)

print(function6())