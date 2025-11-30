n = 5

while n < 19:

    print(n)
    
    if n % 3 == 0:
        n += 5
        continue
        break

    elif n % 2 == 1:
        n += 2

    print(n)
    n -= 1

print(n)