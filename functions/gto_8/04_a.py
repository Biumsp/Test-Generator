# Il metodo .endswith delle stringhe, restituisce True 
# se la stringa a cui è applicato finisce con (ends with) 
# la sotto-stringa specificata in input

# Esempio:
# "esempio".endswith("io") >>> True
# "esempio".endswith("tu") >>> False

days = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]

for d in days:
    if d.endswith("io") or d.endswith("le"):
        print(d)
        continue

    elif d.endswith("o"):
        print("quasi")
    
    else:
        print("non ci siamo")
        break

    print("ok")