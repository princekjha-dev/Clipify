"""
Helper script to get YouTube cookies for video downloads
"""

from pathlib import Path


def main():
    """Print instructions for getting YouTube cookies"""
    
    cookies_path = Path.cwd() / "cookies.txt"
    exists = "YES" if cookies_path.exists() else "NO"
    
    instructions = f"""
==============================================================================
                   GET YOUTUBE COOKIES - 5 MINUTES
                                                                            
  This will allow Clipify to download YouTube videos without errors        
==============================================================================

STEP 1: Install Browser Extension
---------------
Chrome/Edge: https://chrome.google.com/webstore/detail/cclelndahbckbenkjhflpdbgdldlbecc
Firefox: https://addons.mozilla.org/firefox/addon/cookies-txt/

STEP 2: Close ALL Browsers
---------------
Close every browser window (Chrome, Edge, Firefox, etc.)

STEP 3: Open YouTube in Your Browser
---------------
1. Open ONLY Edge or Chrome
2. Go to https://www.youtube.com
3. Make sure you're LOGGED IN to your YouTube account

STEP 4: Export Cookies
---------------
1. Click the extension icon in your browser toolbar
2. Select "Export" (or "Get cookies for this site")
3. Save the file as: cookies.txt

STEP 5: Place Cookies File
---------------
Move or save cookies.txt to this location:

    {cookies_path}

STEP 6: Test Download
---------------
Run your command again:

    python clipify.py --url https://www.youtube.com/watch?v=... --output clips

==============================================================================
                         IMPORTANT NOTES
                                                                            
 - Make sure you're LOGGED IN to YouTube
 - Don't use cookies from multiple websites mixed together
 - Export ONLY YouTube cookies
 - Close all other browser tabs before exporting
 - File should be saved as cookies.txt (not cookies.json)

 Current cookies location: {cookies_path}
 Cookies found: {exists}
==============================================================================
"""
    
    print(instructions)


if __name__ == "__main__":
    main()
