n = 4

while n < 19:

    print(n)
    
    if n % 3 == 0:
        n += 4
        continue
        break

    elif n % 2 == 1:
        n += 1

    print(n)
    n -= 1

print(n)