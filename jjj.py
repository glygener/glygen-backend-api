import re


def is_glycan_composition(term):
    term = term.strip().replace(" ", "")
    res_str = re.sub(r"[(,)]", " ", term)
    tmp_list_one, tmp_list_two = [], []
    w_list = res_str.strip().split(" ")
    if len(w_list)%2 != 0:
        return False, []
    for i in range(0, len(w_list) -1):
        if i%2 == 0:
            s = w_list[i]
            ss = w_list[i+1]
            f = s.isalpha() and ss.isdigit()
            tmp_list_one.append(f)
            cmp = "%s(%s)" % (s, ss)
            o = {"$text": { "$search": cmp}}
            tmp_list_two.append(o)

    return list(set(tmp_list_one)) == [True], {"$and":tmp_list_two}


term = "Hex(5)HexNAc(4)dHex(1)"
#term = "Hex(5)HexNAc(4)dHex"
f, q = is_glycan_composition(term)

print (f)
print (q)



