def function5(a = 4, b = 5):
    print(a + b)

def function6(a=6, b=5):
    print(a + b)
    return function5()

print(function5())