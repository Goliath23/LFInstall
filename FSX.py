#!/usr/bin/env python

import _winreg
import os
import fnmatch
import re
import logging
import os.path
import shutil

def copyLightFields(foundAirports):
    for airport in sorted(foundAirports.keys()):
        if airportHasLightField(foundAirports, airport):
            continue
        
        lfPath = getMatchingLightField(airport)
        
        if lfPath == "":
            logging.error("no Lightfield found for airport " + airport)
            continue
        
        shutil.copy(lfPath, foundAirports[airport])
        logging.info("Lightfield for %s installed." % airport)
        
    pass 
    
def getMatchingLightField(airport):
    lfbasepath = lfsrcpath = getDX10SceneryFixerFolder() + "\\bgl\\airport fields\\bgl\\"
    if os.path.exists(lfsrcpath) == False:
        logging.error("Searching for LightFields in %s. That path does not exist. Have you extracted thhe lightfields to this location?")
        raise (Exception)
    
    lfsrcpath = getDX10SceneryFixerFolder() + "\\bgl\\airport fields\\bgl\\" + airport + "_LightField.BGL"
    logging.debug("Searching LF for %s with path %s" % (airport, lfsrcpath))
    
    if os.path.exists(lfsrcpath) == False:
        return ""
        
    return lfsrcpath

def airportHasLightField(foundAirports, airport):
    if airport in foundAirports == False:
        return False
    
    lffilename = str(airport) + "_LightField.BGL"
    lfpath = str(foundAirports[airport]) + "\\" + lffilename
    
    logging.debug("lfpath: %s" % lfpath)
    
    if os.path.exists(lfpath) == False:
        return False
        
    return True

def getInstalledAirports():
    FSXFolder = getFSXFolder()
    numMatches = 0
    foundAirports = {}
    
    dirtree = os.walk (FSXFolder)
    
    for entry in dirtree:
        #ignore LandClass folders
        if re.search(r"_LC", entry[0]) != None:
                logging.debug("ignoring LandClass Folder: %s" % entry[0])
                continue
            
        #ignore Global Scenery Folders
        if re.search(r"Scenery\\Global", entry[0]) != None:
                logging.debug("ignoring: %s" % entry[0])
                continue
            
        #ignore standard scenery folders
        if re.search(r"Scenery\\[0-9]*\\", entry[0]) != None:
                logging.debug("ignoring: %s" % entry[0])
                continue
        
        #ignore aerosoft afd folder
        if re.search(r"\\afd\\", entry[0], re.IGNORECASE) != None:
                logging.debug("ignoring: %s" % entry[0])
                continue
            
        #ignore aerosoft Cities folder
        if re.search(r"\\Cities\\", entry[0], re.IGNORECASE) != None:
                logging.debug("ignoring: %s" % entry[0])
                continue
        
        for file in fnmatch.filter(entry[2], "[a-zA-z][a-zA-z][a-zA-z][a-zA-z]_*.bgl"):
            airport = str(file).split('_')[0]
            airport = str(airport).upper()
            
            if airport == "XLIB":
                logging.debug("ignoring: %s" % airport)
                continue
            
            if airport == "STAT":
                logging.debug("ignoring: %s" % airport)
                continue
            
            if airport in foundAirports:
                if foundAirports[airport] != entry[0]:
                    logging.warning("ambigous match for %s in %s, Overwriting: %s" % (airport, entry[0], foundAirports[airport]))
                
            foundAirports[airport] = entry[0]
            numMatches += 1
    
    return foundAirports


            
def getPath(valuename, name = "", name64bit = ""):
    key = None
    
    reghandle = _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE)
    
    try:
        key = _winreg.OpenKey(reghandle, name)
    except WindowsError:
        pass
    
    if key == None:
        try:
            key = _winreg.OpenKey(reghandle, name64bit)
        except WindowsError:
            pass
    
    if key == None:
        return ""
    
    [Pathname, regtype] = _winreg.QueryValueEx(key, valuename)
    
    if (Pathname == ""):
        raise WindowsError
    
    return Pathname
    

def getFSXFolder():
    return getPath("SetupPath",
                   r'SOFTWARE\Microsoft\Microsoft Games\Flight Simulator\10.0',
                   r'SOFTWARE\Wow6432Node\Microsoft\Microsoft Games\Flight Simulator\10.0')


def getDX10SceneryFixerFolder():
    return getPath("Path",
                   "SOFTWARE\SteveFSX\DX10 Scenery Fixer",
                   "SOFTWARE\Wow6432Node\SteveFSX\DX10 Scenery Fixer")
   
