#!/usr/bin/env python3

import argparse
import conf_tester

def main():
    print("Iniciando" , flush=True)
    parser = argparse.ArgumentParser(description="Autocompliance")
    parser.add_argument("-f", "--file", required=False, help="YAML file with tests")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show proofs")
    parser.add_argument("-b", "--basic", action="store_true", help="Use basic file: bconf.yaml")
    parser.add_argument("-c", "--complex", action="store_true", help="Use complex file:conf.yaml")
    arg = parser.parse_args()

    if arg.basic:
        yaml_file="bconf.yaml"
    elif arg.complex:
        yaml_file="cconf.yaml"
    elif arg.file:
        yaml_file=arg.file
    else:
        yaml_file="bconf.yaml"
    
    conf_tester.checkTests(conf_tester.fileLoad(yaml_file),arg.verbose)


if __name__ == "__main__":
    main()