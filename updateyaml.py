
"""
This function takes YAML from each MD file and compiles it into the MD portion of the fileself.
This is useful because that compiled code can be customized if needed and easier to read/edit.
"""

import os
import yaml
# Takes open file and returns dict from YAML in file.
def parse_YAML(f): # Need to write my own parser because Hugo yaml use --- twice, and Python parsers throw errors at it
    yamlstr = f.readline()
    line = f.readline()
    while not line.startswith("---"):
        if line.startswith( "#"):

        yamlstr += line
        line = f.readline()
    return yaml.load( yamlstr )
  
def parse_YAML2(f):
    doc = f.readlines()
    comments = []
    lines = {}
    for lineNum, line in enumerate( doc[1:] ):
        if line.startswith("#"):
            comments.append( (lineNum, line) )
    while not line.startswith("---"):
        if line.startswith( "#"):

        yamlstr += line
        line = f.readline()
    return yaml.load( yamlstr )

wiki = "content/wiki/"
directory = os.fsencode( wiki )
def get_coins( dir ):
    for entry in os.scandir( dir ):
        filename = os.fsdecode(entry)
        if not filename.endswith("_index.md"):
            with open(filename,'r') as f:
                coin = parse_YAML( f )
            yield coin

def check_missing_keys():
    coins = list( get_coins( directory ) )
    foundKeys = set( coins[0].keys() )
    for index, coin in enumerate( coins ):
        curKeys = set( coin.keys() )
        curHasNew = curKeys - foundKeys
        curLacksKeys = foundKeys - curKeys

        if curHasNew:
            print( f'{[c["name"] for c in coins[:index]]} \n are lacking from {coin["name"]} \n {[key for key in curHasNew]}' )

        if curLacksKeys:
            print( f"{ coin['name'] } lacks keys: \n{ curLacksKeys }" )

        foundKeys = foundKeys.union( curLacksKeys )

    # All keys found:
    print( "#########################\n ############################### \nFollowing is a complete list of keys: \n\n")
    print( foundKeys )

url1 = ""
def updateSpecs():
    coins = list( get_coins( directory ) )
