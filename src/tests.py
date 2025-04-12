import sys, threading
from PyQt5.QtWidgets import QApplication
import gui as myGui
import rip as rip
import utils as utils

def main(): 
    

    app = QApplication(sys.argv)

    ripper = rip.Ripper(None)
    threading.Thread(target = ripper.processRipQueue, daemon=True).start()
    threading.Thread(target=ripper.processWorkQueue, daemon=True).start()

    window = myGui.MainWindow(ripper)

    ripper.window = window

    window.show()

    testURLS = [
    ("https://www.youtube.com/watch?v=yykFKAZuU_g", 0, ripper.getPath()), # Y Single Video (Boy Harsher - LA)
    ("https://music.youtube.com/watch?v=6GqJYOJLq2E&si=C4lsEPid4WROZmkM,", 0, ripper.getPath()), # YM Single Video (Boy Harsher - LA)

    ("https://www.youtube.com/watch?v=sK_D3wGANhY&list=PLgsEX5K5yzJI2Hr4CgCmOlT3ZbnQ8aSVJ", 2, ripper.getPath()), # Y Single Playlist (elijah who - i'm tired of feeling this way)
    ("https://music.youtube.com/watch?v=j-k0gJgc4FM&list=PLQMmC9DAcgQCskmnA04APtCJLOgT9p0X3", 2, ripper.getPath()), # YM Single Playlist (Avril Lavigne - I Love You (Hardtekk))

    ("https://www.youtube.com/playlist?list=PLQMmC9DAcgQCskmnA04APtCJLOgT9p0X3", 1, ripper.getPath()), # Y Playlist (FF DJ MIX?!)
    ("https://music.youtube.com/playlist?list=PLQMmC9DAcgQCskmnA04APtCJLOgT9p0X3", 1, ripper.getPath()) # YM Playlist (FF DJ MIX?!)
]
    print(f"Running Tests....")
    for url in testURLS:
        ripper.addToQueue(url)

    sys.exit(app.exec())

if __name__ == '__main__':
    main()


