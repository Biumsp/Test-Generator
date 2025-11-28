def function5(a = "2", b = "4" ):
    print(a + b)
    return a + b

def function6(a = 6, b = 5):
    return function5()

print(function6())