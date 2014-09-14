butts

Somethings to keep in mind - if my programs delete, mutate, or otherwise make some change
that you're not happy with, sorry but that's something that happens sometimes when a
program isn't ready yet. Hell, it happens sometimes when the program is already finished!
The point is... don't get too attached to any particular version, plus don't try to do
something that will obviously cause you more problems (like trying to edit a file that
isn't a card with the card editor) and you SHOULD be fine, but there's still a small
chance something else might go wrong. I'll try to make sure that won't happen, mkay?

OK! With that out of the way, let's get down to the nitty-gritty.




==== INSTALLATION ====

Ok, so to help test this out in it's unfinished state, there's a few things that you'll
need to install... I'm sorry :(

- Python 2.7.8              https://www.python.org/ftp/python/2.7.8/python-2.7.8.msi
    (Do the full install)
- Pygame 1.9.2a0            http://www.lfd.uci.edu/~gohlke/pythonlibs/#pygame
    (Get the one that ends with win32-py2.7 and just keep clicking next)

Optional, BUT RECOMMENDED:
- GIT 2.1.0                 http://git-scm.com/downloads
    (Just keep clicking next)

Optional Stuff:
- PIL 1.1.7                 http://effbot.org/downloads/PIL-1.1.7.win32-py2.7.exe
    (This is only if you want to use the card editor)




==== USING GIT ====

Ok, so if you're reading this, it likely means you've already downloaded everything,
but still...

TO DOWNLOAD THIS PROJECT WITH GIT:
  first find a location you'd like to download to.
  Right-click that location and click 'GIT Bash'.
  Then type in "git clone https://github.com/raubana/TSSSFgame.git".
  and press enter. It'll automatically create a folder for you called "TSSSFgame"
  and download the entire project to it.

TO UPDATE THE PROJECT:
  Right-click the "TSSSFgame" folder and open 'GIT Bash'. Type in 'git pull' and press
  enter. It should update (or otherwise tell you everything is up to date).

TO UPDATE THE PROJECT WHEN GIT WON'T LET YOU BECAUSE IT'S A BUTT:
  Ok, something important to note here -

  THIS METHOD IS GOING TO REMOVE EVERYTHING YOU'VE CHANGED OR ADDED
  SO THINGS LIKE CUSTOM CARDS ARE GOING TO DISAPPEAR!!

  So yeah, make sure to move them out of the folder first if you REALLY care about them.
  OK anyways, just like the previous one, right-click the "TSSSFgame" folder and click
  'open GIT Bash'. First type in 'git fetch --all' and press enter. Then, type in
  'git reset --hard origin/master' and press enter. This will reset your folder and make
  everything exactly as it is on Github.




==== SOMETHING WENT WRONG ====

Ok, this is actually kind of a good thing, because I need to catch everything that
could go wrong before I make a final release. Oh, uh... sorry about it breaking for
you though.

Bear in mind that this is a mutuality thing - I CAN'T HELP YOU IF YOU DON'T HELP ME.

What I mean is, the only way your problem can be fixed is if I know about it first,
so I need you to message me with information on that issue or it might never get fixed!
Also, when messaging me, I need you to be as clear as possible (not wordy, just clear)
so that I can more easily assess the cause of the problem and get it fixed sooner.
...also, don't give me no attitude, mkay? Mkay.

1. Save The Error Message
  Anyway, when you run into a program-crashing error, a message should appear in the
  command prompt window. Try right-clicking the command prompt window (the part you grab
  onto to move it around) and click "Edit" then "Select All". Right-click it again and
  this time click "Edit" then "Copy". You should now have the contents of the command
  prompt window on your clipboard.

  You should put this into a '.txt' file and save it on your desktop or something before
  moving onto the next part, because you'll probably want to close the program and you
  might need the clipboard again.

2. Message Me!
  Ok, next, you'll want to message me somehow. Your best bet is to email me, so here's my
  email address:

    raubana@gmail.com

  I've got a thing that will let me know if I've received any emails with "tsssf" in it's
  subject, so you could say "My TSSSF game thing broke: I NEED HELP!!" or "The tsssfgame
  crashed when I tried to do this and that" or just "TSSSF" and I'll know pretty quickly!

  In the body of the email, give me a short description of what was happening right
  before the crash occurred - especially what you did the instant before the program
  crashed. Then, put in the body the error message stuff you'd saved from earlier OR you
  could just make it an attachment. Then, send it off!

  Your contribution is always appreciated :)