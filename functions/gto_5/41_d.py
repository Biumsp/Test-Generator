def function5(a = 4, b = 5):
    return a + b

def function6(a=6, b=5):
    print("a + b")
    return function5(2, 3)

print(function6())