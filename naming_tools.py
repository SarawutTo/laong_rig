from imp import reload

# from typing import Union


def deconstruct(obj_name):  #: Union[str, loc.Core]
    try:
        try:
            compo = obj_name.name.split("_")
        except:
            compo = obj_name.split("_")
    except:
        return TypeError("Cant Split Name Object is {}".format(type(obj_name)))

    if len(compo) == 2:
        return compo[0], None, None, compo[1]

    elif len(compo) == 3:
        if compo[1].isdigit():
            return compo[0], compo[1], None, compo[2]
        else:
            return compo[0], None, compo[1], compo[2]

    elif len(compo) == 4:
        return compo[0], compo[1], compo[2], compo[3]

    else:
        return False


def construct(name, index, side, _type):
    name_list = []
    print(name, index, side, _type)
    if index:
        index = "{:02d}".format(int(index))

    for compo in [name, index, side, _type]:
        if compo:
            name_list.append(str(compo))

    return "_".join(name_list)


def upfirst(name):
    letter_count = len(str(name))
    if letter_count == 1:
        return name.upper()
    else:
        return name[0].upper() + name[1:]


def lowfirst(name):
    letter_count = len(str(name))
    if letter_count == 1:
        return name.lower()
    else:
        return name[0].lower() + name[1:]
