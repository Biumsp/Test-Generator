n = 0

while n < 20:

    n += 2
    print(n)
    
    if n % 3 == 0:
        continue

    elif n % 5 == 0:
        n += 3
        continue

    n += 1

print(n)