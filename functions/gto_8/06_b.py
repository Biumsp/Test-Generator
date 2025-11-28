def function11(n):

    i = 2

    while i < n:

        i += 2
        print(f"i: {i}")

        if i > 5 and i <= 10:
            continue

print(function11(13))