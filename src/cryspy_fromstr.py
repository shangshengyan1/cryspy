import cryspy_numbers as nb
import quicktions as fr
import uncertainties as uc
import cryspy_geo as geo


def removeletters(string):
    assert isinstance(string, str), \
        "Argument must be of type str."
    for character in ["a", "b", "c", "d", "e", "f", "g", \
                      "h", "i", "j", "k", "l", "m", "n", \
                      "o", "p", "q", "r", "s", "t", "u", \
                      "v", "w", "x", "y", "z", \
                      "A", "B", "C", "D", "E", "F", "G", \
                      "H", "I", "J", "K", "L", "M", "N", \
                      "O", "P", "Q", "R", "S", "T", "U", \
                      "V", "W", "X", "Y", "Z"]:
        string =  string.replace(character, " ")
    return string

def str2linearterm(string, liste_variables):
    assert isinstance(string, str), \
        "Argument must be of type str."
    assert isinstance(liste_variables, list), \
        "Argument must be of type list."
    for item in liste_variables:
        assert isinstance(item, str), \
            "Argument must be a list of objects of type str."
    string = string.replace('-', '+-')
    string = string.replace(' ', '')
    words = string.split('+')
    liste_numbers = [0 for i in range(len(liste_variables) + 1)]
    for word in words:
        has_variable = False
        index = -1
        for a in word:
            if a.isalpha():
                word = word.replace(a, '')
                index = liste_variables.index(a)
                has_variable = True
        if word == '' or word == '-':
            if has_variable:
                word += '1'
            else:
                word += '0'
        liste_numbers[index] += fromstr(word)
    return liste_numbers

def fromstr(string):
    """
        >>> print(fromstr("1/2"))
        1/2
        >>> print(fromstr("1.2+/-0.1"))
        1.20(10)
        >>> print(fromstr("1.2(1)"))
        1.20(10)
        >>> print(fromstr("4"))
        4
        >>> print(fromstr("/ 1 2 \ \\n \ 3 4 /"))
         /  1  2  \ 
         \  3  4  / 

    """
    assert isinstance(string, str), \
        "Function fromstr must have an argument of type string."
    typ = typefromstr(string)
    if typ == nb.Mixed:
        try:
            result = mixedfromstr(string)
            assert isinstance(result, nb.Mixed), \
                "The following string looks like a number, but I "\
                "cannot convert it: %s"%(string)
            return result
        except:
            pass
    elif typ == nb.Matrix:
        try:
            return matrixfromstr(string)
        except ValueError:
            raise(Exception("The following string looks like a Matrix, "\
                            "but I cannot convert it: %s"%(string)))
    elif typ == geo.Symmetry:
        try:
            return symmetryfromstr(string)
        except ValueError:
            raise(Exception("The following string looks like a Symmetry, "\
                            "but I cannot convert it: %s"%(string)))
    elif typ == geo.Transformation:
        try:
            return transformationfromstr(string)
        except ValueError:
            raise(Exception("The following string looks like a "\
                            "Transformation, but I cannot convert it: %s"\
                            %(string)))
    elif typ == geo.Coset:
        try:
            return cosetfromstr(string)
        except ValueError:
            raise(Exception("The following string looks like a Coset "\
                            "but I cannot convert it: %s"%(string)))
    elif typ == geo.Pos:
        try:
            return posfromstr(string)
        except ValueError:
            raise(Exception("The following string looks like a Pos "\
                            "but I cannot convert it: %s"%(string)))
    elif typ == geo.Dif:
        try:
            return diffromstr(string)
        except ValueError:
            raise(Exception("The following string looks like a Dif "\
                            "but I cannot convert it: %s"%(string)))

def typefromstr(string):
    words = string.split()

    if ('a' in string) or ('b' in string) or ('c' in string) \
        or ("then" in string) or ('O' in string) or ("->" in string):
        return geo.Transformation
    elif (words[0][0] == '/') and words[-1][-1] == '/':
        return nb.Matrix
    elif (words[0][0] == '<') and (words[-1][-1] == '>'):
        return nb.Matrix
    elif ('p' in string) or ('P' in string) or ('r' in string) or ('R' in string):
        return geo.Pos
    elif ('d' in string) or ('D' in string):
        return geo.Dif
    elif ('{' in string) and ('}' in string):
        return geo.Coset
    elif ('x' in string) or ('y' in string) or ('z' in string):
        return geo.Symmetry
    elif ('\n' in string) or ('\\' in string) or (' ' in string):
        return nb.Matrix
    else:
        return nb.Mixed

def mixedfromstr(string):
    try:
        return nb.Mixed(int(string))
    except:
        try:
            return nb.Mixed(float(string))
        except:
            try:
                return nb.Mixed(fr.Fraction(string))
            except ValueError:
                try:
                    return nb.Mixed(uc.ufloat_fromstr(string))
                except ValueError:
                    raise(Exception("The following string looks like a number, "\
                                    "but I can't convert it: %s"%(string)))
        

def matrixfromstr(string):
     string = string.replace('|', '\\')
     string = string.replace('/ ', ' ')
     string = string.replace('<', ' ')
     string = string.replace('>', ' ')
     string = string.replace(' /', ' ')
     string = string.replace('\n', '\\')
     for i in range(4):
        string = string.replace('\\ \\', '\\')
        string = string.replace('\\  \\', '\\')
        string = string.replace('\\   \\', '\\')
     rowwords = string.split('\\')
     rowliste = []
     for rowword in rowwords:
         words = rowword.split()
         liste = []
         for word in words:
             liste.append(mixedfromstr(word))
         rowliste.append(nb.Row(liste))
     return nb.Matrix(rowliste)


def symmetryfromstr(string):
    words = string.split(',')
    assert len(words) == 3, \
        "The following string looks like a Symmetry, but it has not "\
        "three comma-separated terms: %s"%(string)
    liste = []
    for word in words:
        row = nb.Row(str2linearterm(word, ['x', 'y', 'z']))
        liste.append(row)
    liste.append(nb.Row([fromstr("0"), fromstr("0"), fromstr("0"), \
        fromstr("1")]))
    return geo.Symmetry(nb.Matrix(liste))


def transformationfromstr(string):
    if len(string.split("then")) > 1:
        # The string respresents not an elementar transformation,
        # i.e. the string represents a transformation which is
        # a composition of elementar transformations.
        result = geo.Transformation(nb.Matrix.onematrix(4))
        for word in string.split("then"):
            result = transformationfromstr(word) * result
    else:
        # The string represents an elementar transformation,
        # i.e. either a pure translation of the origin or a
        # pure change of the axes.
        if ('O' in string) or ("->" in string):
            # The string represents a pure translation of the origin.
            words = string.split("->")
            word = words[1]
            word = word.replace('(', ' ').replace(')', ' ').replace(',', ' ')
            threenumbers = fromstr(word)
            print(threenumbers)
            matrix = nb.Matrix([[1, 0, 0, threenumbers.liste[0].liste[0]], \
                                 [0, 1, 0, threenumbers.liste[0].liste[1]], \
                                 [0, 0, 1, threenumbers.liste[0].liste[2]], \
                                 [0, 0, 0, 1                             ]])
        elif ('a' in string) or ('b' in string) or ('c' in string):
            # The string represents a pure change of the axes
            lines = string.split('\n')
            assert len(lines) == 3, \
                "The following string looks like a Transformation, but it has not "\
                "exactly three lines: %s"%(string)
            liste = []
            i = 0
            for line in lines:
                i += 1
                words = line.split(' ')
                assert  (    ((i == 1) and (words[0] == "a'")) \
                          or ((i == 2) and (words[0] == "b'")) \
                          or ((i == 3) and (words[0] == "c'"))  )\
                    and (words[1] == '='), \
                    "The Transformation must have the following form: \n" \
                    "a' = ... \n" \
                    "b' = ... \n" \
                    "c' = ... \n" \
                    "in this Order!"
    
                row = nb.Row(str2linearterm(words[2], ['a', 'b', 'c']))
                liste.append(row)
            liste.append(nb.Row([fromstr("0"), fromstr("0"), fromstr("0"), \
                fromstr("1")]))
            m = nb.Matrix(liste)
            matrix = nb.Matrix( \
                [nb.Row([m.liste[0].liste[0], m.liste[1].liste[0], m.liste[2].liste[0], m.liste[0].liste[3]]), \
                 nb.Row([m.liste[0].liste[1], m.liste[1].liste[1], m.liste[2].liste[1], m.liste[1].liste[3]]), \
                 nb.Row([m.liste[0].liste[2], m.liste[1].liste[2], m.liste[2].liste[2], m.liste[2].liste[3]]), \
                 nb.Row([m.liste[3].liste[0], m.liste[3].liste[1], m.liste[3].liste[2], m.liste[3].liste[3]])])
    
        return geo.Transformation(matrix.inv())


def cosetfromstr(string):
    string = string.replace('{', ' ')
    string = string.replace('}', ' ')
    return geo.Coset(fromstr(string), geo.canonical)


def posfromstr(string):
    string = string.replace('\n', ' ')
    string = string.replace('\\', ' ')
    string = string.replace('/ ', ' ')
    string = string.replace(' /', ' ')
    string = string.replace('|', ' ')
    string = removeletters(string)
    words = string.split()
    string = '\n'.join(words)
    string += "\n 1"
    return geo.Pos(matrixfromstr(string))

def diffromstr(string):
    string = string.replace('\n', ' ')
    string = string.replace('\\', ' ')
    string = string.replace('/ ', ' ')
    string = string.replace(' /', ' ')
    string = string.replace('|', ' ')
    string = removeletters(string)
    words = string.split()
    string = '\n'.join(words)
    string += "\n 0"
    return geo.Dif(matrixfromstr(string))