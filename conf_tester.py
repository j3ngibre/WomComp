import subprocess
import shlex #To prevent inyections
import yaml



#PRINT RESULTS COOL WAY ;)
def printResult(test, passed, proof):
   
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    
    print("\n" + "="*80)
    
    if passed:
        
        print(f"{GREEN}{BOLD}✓ PASS{RESET} - {test.get('id')}")
        print(f"{GREEN}No vulnerabilities detected{RESET}")
    else:
       
        print(f"{RED}{BOLD}✗ FAIL - RISK DETECTED{RESET}")
        print(f"{RED}{BOLD}Test ID:{RESET} {test.get('id')}")
    
    
    print(f"\n{BOLD}Title:{RESET} {test.get('title')}")
    print(f"{BOLD}Category:{RESET} {test.get('category')}")
    print(f"{BOLD}Severity:{RESET} {test.get('severity')}")
    
    
    frameworks = []
    if test.get('CIS'):
        frameworks.append(f"CIS: {test.get('CIS')}")
    if test.get('ISO'):
        frameworks.append(f"ISO27001: {test.get('ISO')}")
    if test.get('NIST'):
        frameworks.append(f"NIST: {test.get('NIST')}")
    
    if frameworks:
        print(f"{BOLD}Frameworks:{RESET} {' | '.join(frameworks)}")
    
    
    print(f"\n{BOLD}Type:{RESET} {test.get('type')}")
    if test.get('file'):
        print(f"{BOLD}File:{RESET} {test.get('file')}")
    if test.get('command'):
        print(f"{BOLD}Command:{RESET} {test.get('command')}")
    print(f"{BOLD}Expected:{RESET} {test.get('expected')}")
    
    
    print(f"\n{BOLD}Evidence:{RESET}")
    if isinstance(proof, list):
        if proof:
            for line in proof:
                print(f"  {YELLOW}→{RESET} {line.strip()}")
        else:
            print(f"  {BLUE}(No matches found){RESET}")
    else:
        print(f"  {proof}")
    
    print("="*80)





#FOR COMMANDS
def cmdCheck(command , check):
    try:
        args=shlex.split(command)
        output= subprocess.run(args, capture_output=True , text=True).stdout.strip()
        return check in output , output
    except Exception as e:
        return False ,str(e)

#SIMPLY FIND COINCIDENCE IN TEXT ; NEED TO ADD WHEN WE SEARCH FOR SOMETHING AND IS COMMENTED RETURN FALSE
def textCheck( file,check):
    match=[]
    try:
        with open(file , "r") as  of:
            for l in of:
                if check in l:
                    match.append(l)
        return bool(match) , match
    except Exception as e:
        return False , str(e)

#LOADING THE FILES INTO STRUCTURES
def fileLoad(file):
    try:
        if not file.endswith(".yaml"):
            file=file+".yaml";
        with open(file ,"r") as of:
            data = yaml.safe_load(of)
            tests =[]

        for t in data.get("tests", []):
            check = t.get("check" ,{})
            fworks = t.get("frameworks",{})
            tests.append({
                "id":t.get("id"),
                "title":t.get("title"),
                "type":check.get("type"),
                "file":check.get("file"),
                "command":check.get("command"),
                "expected":check.get("expected"),
                "CIS":fworks.get("CIS"),
                "ISO":fworks.get("ISO27001"),
                "NIST":fworks.get("NIST"),
                "category":t.get("category"),
                "severity":t.get("severity")
        })
        return tests

    except Exception as e:
        print("Error while loading conf" ,e)
        return []


#RUNNING TESTS
def checkTests(tests ,verbose):
    result = []
    for i in tests:
        type = i.get("type", "")
        if "file_contains" in type:
            passed, proof = textCheck(i.get("file"), i.get("expected"))
        else:
            passed, proof = cmdCheck(i.get("command"), i.get("expected"))

        if verbose == True :
            printResult(i, passed, proof)

        result.append((i.get("id"), passed, proof))

    return result
