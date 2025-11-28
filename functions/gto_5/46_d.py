def function5(a, b):
    return a + b

def function6(a = 6, b = 5):
    return function5(a, b)

print(function6(a = 3, b = "c"))