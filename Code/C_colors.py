# -*- coding: utf-8 -*-

    
Warning         = "\x1b[36m\x1b[40m"
Caption         = "\x1b[30m\x1b[47m"
Emphasize       = "\x1b[4m"
Black           = "\x1b[30m"
Red             = "\x1b[31m" 
Green           = "\x1b[32m"
Yellow          = "\x1b[33m"
Blue            = "\x1b[34m"
Magenta         = "\x1b[35m"
Cyan            = "\x1b[36m"
White           = "\x1b[37m"
BackBlue        = "\x1b[44m"
BackBlue        = "\x1b[44m"
BackGreen       = "\x1b[42m"
Script          = "\x1b[44m"
Default         = "\x1b[39m"
Grey            = "\x1b[90m"
LightGreen        = "\x1b[92m"

#End all color commands
END             = "\x1b[0m"
End             = "\x1b[0m"
end             = "\x1b[0m"

#with double space between letters, only for one string!
def printT(args):
    s=' '
    print(Caption+s.join(args)+End)
    return

def printb(*args):
    s=' '
    print(Cyan+s.join(args)+End)
    return

def printg(*args):
    s=''
    print(Green+s.join(args)+End)
    return