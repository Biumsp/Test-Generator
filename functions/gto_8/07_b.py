def function11(n):

    i = 0

    while i <= n:

        i += 2
        print(f"i: {i}")

        if i > 5 and i <= 10:
            continue

        if i == 12:
            break

    return n

print(function11(13))