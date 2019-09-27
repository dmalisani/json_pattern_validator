
def cbu_validator(cbu, *args, **kwargs):
    """
    Check if is a valid CBU Number (parity). It Returns Boolean.
    """

    if type(cbu) == int:
        cbu = "%022d" % cbu
    cbu = cbu.strip()
    if len(cbu) != 22:
        return False
    s1 = sum(int(a)*b for a, b in zip(cbu[0:7], (7, 1, 3, 9, 7, 1, 3)))
    d1 = (10 - s1) % 10
    if d1 != int(cbu[7]):
        return False
    s2 = sum(int(a)*b for a, b in zip(cbu[8:-1],
             (3, 9, 7, 1, 3, 9, 7, 1, 3, 9, 7, 1, 3)))
    d2 = (10 - s2) % 10
    if d2 != int(cbu[-1]):
        return False
    return True


def cuit_validator(cuit, *args, **kwargs):
    """
    Check if is a valid CUIT/CUIL Number (parity). It returns Boolean.
    """

    if len(cuit) not in (11, 13):
        return False

    if len(cuit) == 13 and (cuit[2] != "-" or cuit[11] != "-"):
        return False

    base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

    cuit = cuit.replace("-", "")
    aux = 0
    for i in range(10):
        aux += int(cuit[i]) * base[i]

    aux = 11 - (aux - (int(aux / 11) * 11))
    if aux == 11:
        aux = 0
    if aux == 10:
        aux = 9
    return aux == int(cuit[10])


def greater_than_validator(value,  *args, **kwargs):
    assert "datatype" in kwargs, "datatype argument is missing"
    datatype = kwargs["datatype"]
    assert type(datatype) is str and len(datatype) > 13,\
        "wrong datatype parameter"
    name = datatype[:13]
    assert name == "greater_than_", "Wrong dataype name for this validator"
    str_min_value = datatype[13:]
    try:
        if len(str_min_value.split(".")) > 1:
            min_value = float(str_min_value)
        else:
            min_value = int(str_min_value)
    except ValueError:
        raise ValueError("Bad name of validator. It's not a number")
    if type(value) not in (float, int):
        try:
            if type(min_value) is float:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            return False
    return value > min_value
