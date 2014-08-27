import sys, os

def error_and_quit(message):
    raw_input(message)
    sys.exit()

print "For this to run properly, make sure that each page in the 'imgs/pages' folder are of type '.png' and have been exported at a resolution of 300 ppi."
print ""
s = raw_input("Type in 'Y' to run: ")
print ""

if s == "Y":
    print "Importing pygame..."
    try:
        import pygame
    except:
        error_and_quit("Whoops! This can't run without pygame. Press return to quit.")

    print "Pygame imported! Let's get those pages..."

    folder = os.listdir("imgs/pages")
    pages = []

    for f in folder:
        if f.endswith(".png"):
            print("... '"+f+"'")
            try:
                pages.append((str(f),pygame.image.load("imgs/pages/"+f)))
            except:
                error_and_quit("Whoops! I couldn't load this image for some reason. Press return to quit.")
    print ""
    print "Pages loaded. Splitting the pages..."

    page_size = (2254,3110)
    cards_per_page = (3,3)
    topleft = (148,95)
    clip = 2
    gap = 3

    for i in xrange(len(pages)):
        name,page = pages[i]
        name = name.replace(".png","")
        print "... splitting '"+name+"'"
        for x in xrange(cards_per_page[0]):
            for y in xrange(cards_per_page[0]):
                #try:
                pos = (-int(topleft[0] + (page_size[0]/float(cards_per_page[0])+gap)*x + clip),
                       -int(topleft[1] + (page_size[1]/float(cards_per_page[1])+gap)*y + clip))
                card = pygame.Surface((int((page_size[0]/cards_per_page[0])-(clip*2)-gap),
                                       int((page_size[1]/cards_per_page[1])-(clip*2)-gap)))
                card.blit(page,pos)
                pygame.image.save(card,"imgs/split pages/"+name+"_"+str(x+1)+"_"+str(y+1)+".png")
                #except:
                #    error_and_quit("Whoops! Failed at "+str(x+1)+", "+str(y+1)+". Press return to quit.")

    print ""
    print "All pages have been split! Go see the cards in 'imgs/split pages'."
    raw_input("Press return to quit.")