def pieces(string):
    """returns a list containing all pieces of string, see example below"""
    tag_pieces = []
    for word in string.split():
        cursor = 1
        while True:
            # this method produces pieces of 'TEXT' as 'T,TE,TEX,TEXT'
            tag_pieces.append(str(word[:cursor]))
            if cursor == len(word):
                break
            cursor += 1
    return tag_pieces
