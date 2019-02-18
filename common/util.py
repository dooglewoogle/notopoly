Colour = {
    "BROWN": '\033[38;5;88m',
    "PURPLE": '\033[35m',
    "CYAN": '\033[36m',
    "DARKCYAN": '\033[36m',
    "BLUE": '\033[34m',
    "GREEN": '\033[32m',
    "ORANGE": '\033[38;5;166m',
    "YELLOW": '\033[33m',
    "RED": '\033[31m',
    "END": '\033[0m',
}

def display_turnstart_blurb(name, money, land, position):
    print "Player ", name
    print "Bal: $", money
    print "Currently at:", position


    if land.get("properties") is not None and len(land['properties']) > 0:
        print "\nProperties:"

        for p in land.get("properties"):
            print(format_indent(p))
            if land['properties'][p] is not None:
                print(format_indent("Houses: %s" % land['properties'][p], indent=4))

    if land.get("stations") is not None and len(land['stations']) > 0:
        print "\nStations:"
        for s in land.get("stations"):
            print s

    if land.get("utilities") is not None and len(land['utilities']) > 0:
        print "\nUtilities:"
        for x in land.get("utilities"):
            print x

def display_action(act, *args):
    extra = " ".join(str(a) for a in args)
    print("\t - "+act + extra)

def format_indent(msg, indent=2):
    return " "*indent + " - " + msg

def choice_header(head):
    print "\n-",head,"-"

def display_turnend():
    print "-"*40

def colourtest():
        print Colour.BROWN + "Brown" + Colour.END
        print Colour.PURPLE + "Purple" + Colour.END
        print Colour.ORANGE + "Orange" + Colour.END
        print Colour.BLUE + "Blue" + Colour.END
        print Colour.GREEN + "Green" + Colour.END
        print Colour.YELLOW + "Yellow" + Colour.END



if __name__ == "__main__":
    colourtest()