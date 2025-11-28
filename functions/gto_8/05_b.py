def function11(n):

    i = 0

    while i < n:

        i += 1
        print(f"i: {i}")

        if i > 5 and i <= 10:
            continue

print(function11(12))