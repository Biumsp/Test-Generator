n = 0

while n < 20:

    n += 3
    print(n)
    
    if n % 3 == 0:
        n -= 1
        continue

    elif n % 5 == 0:
        n -= 2

    n += 1

    if n % 11 == 0:
        break


print(n)