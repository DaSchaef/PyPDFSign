import argparse, os, re
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--infile", help="Input file: To be signed PDF.", required=True, type=argparse.FileType("rb"))
args = parser.parse_args()

infile = args.infile


def findPDFSection(file, sectionstr):
    file.seek(0, os.SEEK_END)
    lastpos = file.tell()
    readbytes = ""
    num_bytes = 0
    while lastpos > 0 and sectionstr not in readbytes:
        file.seek(lastpos, 0)
        readbytes = file.read(1).decode("utf-8")  + readbytes
        lastpos -= 1
    return lastpos       

def findRootObjNum(file, position=0):
    name = "/Root"
    file.seek(position, 0)
    for line in file:
        line = line.decode("utf-8")
        if name in line:
            matches = re.search(rf"{name} ([0-9]+) [0-9]+", line)
            return int(matches[1])

def getObjPosFromXREF(file, xrefpos, objnum):
    file.seek(xrefpos, 0)
    line = "-1 -1"
    for line in file:
        break
    for line in file:
        line = line.decode("utf-8")
        break
    objstart = int(line.split(" ")[0])
    file.seek(20*(objnum-objstart), 1)
    for line in file:
        line = line.decode("utf-8")
        break
    objstart = int(line.split(" ")[0])
    return objstart

def getXrefPos(file, startxrefpos):
    line = "-1"
    file.seek(startxrefpos, 0)
    for line in file:
        break
    for line in file:
        break
    for line in file:
        line = line.decode("utf-8")
        break
    return int(line)
    
def parseObjentry(line, retval):
    print("Regre", line, "\n----------------------------")
    while len(line) > 0:
        cnt = 1
        if line.startswith("/"):
            matches_dict = re.search(r"^/([a-zA-Z0-9]*)<<(.*?)>>", line)
            if matches_dict:
                retval[matches_dict[1]] = {}
                print("dict", line)
                print(matches_dict[1], matches_dict[2])
                print()
                retval[matches_dict[1]] = parseObjentry(matches_dict[2], retval[matches_dict[1]])
                cnt = len(matches_dict[1]) + len(matches_dict[2]) + 5
            else:
                matches_brackets = re.search(r"^/([a-zA-Z0-9]*)(\[|\(.*?\]|\))(/|$)", line)
                if matches_brackets:
                    print("brackets", line)
                    print(matches_brackets[1], matches_brackets[2])
                    print()
                    
                    retval[matches_brackets[1]] = matches_brackets[2]
                    #print("muh", line, matches[1], matches[2])
                    cnt = len(matches_brackets[1]) + len(matches_brackets[2]) + 4
                else:
                    matches = re.search(r"^/([a-zA-Z0-9]*)(.*?)(/|$)", line)
                    print("other", line)
                    print(matches[1], matches[2])
                    print()
                    retval[matches[1]] = matches[2]
                    #print("muh", line, matches[1], matches[2])
                    cnt = len(matches[1]) + len(matches[2]) + 2
        line = line[cnt:]
    print("Leave", line, "\n----------------------------")
    return retval
    
def obj2dict(file, startpos):
    retval = {}
    currentpointer = retval
    curentkey = None
    file.seek(startpos, 0)
    for line in file:
        line = line.decode("utf-8")
        if line.startswith("endobj"):
            break
        if line.startswith("<<"): # ignore first dict as this is what we parse
            line = line[2:-2]
        retval = parseObjentry(line, retval)  
        
    return retval
    
trailer_start = findPDFSection(infile, "\ntrailer")
startxref_start = findPDFSection(infile, "\nstartxref")
rootobjnum = findRootObjNum(infile, trailer_start)
xrefpos = getXrefPos(infile, startxref_start)

rootobjpos = getObjPosFromXREF(infile, xrefpos, rootobjnum)
print(rootobjpos)

infile.seek(rootobjpos, 0)

rootobj = obj2dict(infile, rootobjpos)
print(rootobj)
for line in infile:
    line = line.decode("utf-8")
    print(line)
    break
infile.close()
