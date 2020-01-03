#!/usr/bin/env python3
import argparse
import configparser

class PVBaseModul():
    def __init__(self):
        pass

    def InitArguments(self, parser):
        print("PVBaseModul.InitArguments() called")

    def SetConfig(self, config, args):
        print("PVBaseModul.SetConfig() called")

    def CheckArgsOrConfig(self, config, constantvar, argconfig, configsection, configtopic, type='str'):
        try:
            if(argconfig is not None):  # Argument has priority
                print("Var '{}.{}' from commandline set to {}".format(configsection, configtopic, argconfig))
                return argconfig
            else:
                # check for config
                if(config.has_option(configsection, configtopic)):
                    if(type == 'str'):
                        v = config.get(configsection, configtopic)
                        print("Var '{}.{}' from config set to {} (str)".format(configsection, configtopic, v))
                    elif(type == 'int'):
                        v = config.getint(configsection, configtopic)
                        print("Var '{}.{}' from config set to {} (int)".format(configsection, configtopic, v))
                    else:
                        print("Error CheckArgsOrConfig: unknown type")

                    return v
        except Exception as e:
            print("CheckArgsOrConfig Error: " + str(e), file=sys.stderr)

        print("Var '{}.{}' from program default set to {} ".format(configsection, configtopic, constantvar))
        return constantvar
