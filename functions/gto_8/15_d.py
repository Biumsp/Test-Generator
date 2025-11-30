n = 5

while n <= 20:

    print(n)
    n -= 2
    
    if n % 3 == 0:
        n += 5
        continue

    elif n % 2 == 0:
        n += 3

    else:
        continue

    if n == 11:
        break

    print(n)
    n -= 1

print(n)