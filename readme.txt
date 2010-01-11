This is just an offline viewer and randomizer (and downloader) for Dinosaur Comics:
http://www.qwantz.com

and inspired by Dadasaurus:
http://www.crummy.com/features/dada/

Just adding a little control to the random fun of Dadasaurus with some Python.

This is completely unauthorized, and if Mr. North disapproves then I will promptly take it down.

It's a WX app, and depends on numpy and PIL.

Building apps with Py2App is completely ridiculous.  The app in DinosaurComics.zip works on the 10.5.7 and 10.6.2 machines I have now, as long as you have wxPython installed for your system Python2.5.  
DinosaurComicsSL.zip contains an app that should work if you have Snow Leopard an wxPython installed for System Python2.6.

Py2App didn't come anywhere close to building portable apps.

Of course, since it's just Python and WX, the program will run on anything as long as you have Python, wxPython, PIL, and numpy installed. just run 'dinoapp.py' and it should* work.

*should being the operative word.  I haven't tested it on Windows, and don't really care to, but it certainly works fine on Mac/*ix systems, and I don't see any reason why it would fail anywhere.

-MinRK