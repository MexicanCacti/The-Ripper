import re

def loadCSS(filename, styleBlock):
    contents = None
    with open(filename, "r") as css:
        contents = css.read()
    
    match = re.search(rf"{styleBlock}\s*\{{(.*?)\}}", contents, re.DOTALL)
    if match:
        return f"{styleBlock} {{{match.group(1)}}}"
    else:
        return ""

# Use Regex to Match this better!    
def checkValidUrl(url):
    if not "youtube" in url.lower():
        return -1
    if "playlist" in url.lower():
        return 1
    return 0

def trimFile(filePath):
    return re.sub(r'\.[^.]+$', '', filePath)
