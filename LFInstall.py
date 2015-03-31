#!/usr/bin/env python

"""
LFInstall: CLI Tool to install Lightfields from Steve's DX10 Fixer

The Installer tries to determine what Airports are installed and copies the
matching light fields from Steve's DX10Fixer in the correct folders.

The general structure of this program is based on a template that can be found at
http://www.jamesstroud.com/jamess-miscellaneous-how-tos/python/cli-program-skeleton
"""

######################################################################
# import the next four no matter what
######################################################################
import os
import sys
import textwrap
from optparse import OptionParser
import FSX
import logging


######################################################################
# edit next two to your liking
######################################################################
__program__ = "LFInstall"
__version__ = "0.1"

######################################################################
# the defaults for the config, if needed
######################################################################
DEFAULTS = {"element" : "C",
            "max_measurement" : 1.0e9,
            "min_measurement" : 1.0,
            "max_sumsq" : 1.0e12,
            "convergence" : 1.0e-10,
            "maxiter" : 100,
            "guess" : 0.010,
            "vf_criterion" : 0.05,
            "debug" : False,
            "log_level" : 0}

LOGFORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format=LOGFORMAT)

######################################################################
# no need to touch banner() or usage()
######################################################################
def banner(width=70):
    hline = "=" * width
    sys.stderr.write(hline + "\n")
    p = ("%s v.%s " % (__program__, __version__)).center(width) + "\n"
    sys.stderr.write(p)
    sys.stderr.write(hline + "\n")

def usage(parser, msg=None, width=70, pad=4):
    lead_space = " " * (pad)
    w = width - pad
    err = ' ERROR '.center(w, '#').center(width)
    errbar = '#' * w
    errbar = errbar.center(width)
    hline = '=' * width
    if msg is not None:
        msg_list = str(msg).splitlines()
        msg = []
        for aline in msg_list:
            aline = lead_space + aline.rstrip()
            msg.append(aline)
        msg = "\n".join(msg)
        print ('\n'.join(('', err, msg, errbar, '')))
        print (hline)
    print
    print (parser.format_help())
    sys.exit(0)

######################################################################
# set up the options parser from the optparse module
#   - see http://docs.python.org/library/optparse.html
######################################################################
def doopts():

    ####################################################################
    # no need to edit the next line
    ####################################################################  
    program = os.path.basename(sys.argv[0])

    ####################################################################
    # edit usg to reflect the options, usage, and info for user
    #   - see http://en.wikipedia.org/wiki/Backus-Naur_Form 
    #       - expressions in brackets are optional
    #       - expressions separated by bars are alternates
    #   - don't mess with the "%s", this is a template string
    #   - here, CSVFILE and associated usage info is just an example
    ####################################################################
    usg = """\
        usage: %s

          The Program does not need additional arguments.
        """
    usg = textwrap.dedent(usg) % program
    parser = OptionParser(usage=usg)
    
    ####################################################################
    # - these are only some examples
    # - but -t and -c options are recommended if using a config file
    ####################################################################  
    parser.add_option("-t", "--template", dest="template",
                      default=False, action="store_true",
                      help="print template settings file",
                      metavar="TEMPLATE")
    parser.add_option("-c", "--config", dest="config",
                      metavar="CONFIG", default=None,
                      help="config file to further specify conversion")
    return parser

######################################################################
# creates an easy configuration template for the user
######################################################################
def template():
    ####################################################################
    # this is yaml: http://www.yaml.org/spec/1.2/spec.html
    #   - keep the first document type line ("%YAML 1.2") and
    #     the document seperator ("---")
    #   - edit the template to match DEFAULTS
    ####################################################################
    t = """
        %YAML 1.2
        ---
        element : C
        max_measurement : 1.6e+7
        min_measurement : 3.0e+2
        max_sumsq : 1.0e10
        convergence : 1.0e-5
        maxiter : 100
        guess : 0.012
        vf_criterion : 0.05
        debug : False
        log_level : 0
        """
    
    ####################################################################
    # no need to edit the next two lines
    ####################################################################
    print (textwrap.dedent(t))
    sys.exit(0)

######################################################################
# process the command line logic, parse the config, etc.
######################################################################
def main():
    ####################################################################
    # no need to touch the next two lines
    ####################################################################
    parser = doopts()
    (options, args) = parser.parse_args()
    
    ####################################################################
    # start processing the command line logic here
    #   - this logic is for
    #     "usage: %s -h | -t | [-c CONFIG] CSVFILE"
    #   - don't touch the next four if you have a config file
    ####################################################################
    if options.template:
        template()
    else:
        banner()
    
    ####################################################################
    # just as an example, we get the value of 'csvfile' from args
    ####################################################################
    #if len(args) != 1:
    #    usage(parser)
    #else:
    #    csvfile = args[0]
    
    ####################################################################
    # create the configuration that will be used within the program
    #   - first make a copy of DEFAULTS
    #   - then, update the copy with the user_config of
    #     the config file
    #   - this allows the user to specify only a subset of the config
    #   - try to catch problems with the config file and
    #     report them in usage()
    ####################################################################
    config = DEFAULTS.copy()
    if options.config:
        if os.path.exists(options.config):
            f = open(options.config)
            user_config = yaml.load(f.read())
            config.update(user_config)
        else:
            msg = "Config file '%s' does not exist." % options.config
            usage(parser, msg)
        
    # main stuff
    FSXPath = FSX.getFSXFolder()
    logging.info("Found FSX in %s" % FSXPath)
    
    DX10Path = FSX.getDX10SceneryFixerFolder()
    logging.info("Found DX10 SceneryFixer in %s" % DX10Path)
    
    foundAirports = FSX.getInstalledAirports()

    logging.info("Found %d installed addon airports. *=LF already installed" % len(foundAirports))
    for airport in sorted(foundAirports.keys()):
        msg = str("\t" + airport + " ")
        if FSX.airportHasLightField(foundAirports, airport):
            msg += "*"
        logging.info(msg)
    
    FSX.copyLightFields(foundAirports)

if __name__ == "__main__":
  main()

