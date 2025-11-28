def function5(a = "2", b = "4" ):
    return a + b

def function6(a = 6, b = 5):
    return function5(a, b)

print(function6(3, 4))