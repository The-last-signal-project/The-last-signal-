from .menu import App,SAVES_DIR
import os
import sys

def main():
    for sub in ("solo", "multi"):
        
        os.makedirs(os.path.join(SAVES_DIR, sub), exist_ok=True)

    App().run()


if __name__ == "__main__":
    main()
    
        

        



