import os
import re
import shlex
import subprocess
import sys
import yaml
import time

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

def progressLine(current, total, bar_length=50):
    if total <= 0:
        return
    
    progress = current / total
    filled_length = int(progress * bar_length)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    
    sys.stdout.write(f"\r{' ' * 100}\r")
    sys.stdout.write(f"[{bar}] {current}/{total} ({progress * 100:.1f}%)")
    sys.stdout.flush()
    
    if current >= total:
        sys.stdout.write("\n")
        sys.stdout.flush()

def printResult(test, passed, proof):
    sys.stdout.write("\n")
    sys.stdout.flush()
    
    print("=" * 80)
    
    test_id = test.get("id", "UNKNOWN")
    title = test.get("title", "No title")
    category = test.get("category", "N/A")
    severity = test.get("severity", "N/A")
    test_type = test.get("type", "N/A")
    
    if passed:
        print(f"{GREEN}{BOLD}✓ PASS{RESET} - {test_id}")
        print(f"{GREEN}No vulnerabilities detected{RESET}")
    else:
        print(f"{RED}{BOLD}✗ FAIL - RISK DETECTED{RESET}")
        print(f"{RED}{BOLD}Test ID:{RESET} {test_id}")
    
    print(f"\n{BOLD}Title:{RESET} {title}")
    print(f"{BOLD}Category:{RESET} {category}")
    print(f"{BOLD}Severity:{RESET} {severity}")
    
    frameworks = []
    if test.get("CIS"):
        frameworks.append(f"CIS: {test.get('CIS')}")
    if test.get("ISO"):
        frameworks.append(f"ISO27001: {test.get('ISO')}")
    if test.get("NIST"):
        frameworks.append(f"NIST: {test.get('NIST')}")
    
    if frameworks:
        print(f"{BOLD}Frameworks:{RESET} {' | '.join(frameworks)}")
    
    print(f"\n{BOLD}Type:{RESET} {test_type}")
    
    if test.get("file"):
        print(f"{BOLD}File:{RESET} {test.get('file')}")
    
    if test.get("command"):
        print(f"{BOLD}Command:{RESET} {test.get('command')}")
    
    if test.get("expected") is not None:
        print(f"{BOLD}Expected:{RESET} {test.get('expected')}")
    
    print(f"\n{BOLD}Evidence:{RESET}")
    
    if isinstance(proof, list):
        if proof:
            for line in proof[:5]:
                print(f"  {YELLOW}→{RESET} {str(line).strip()}")
            if len(proof) > 5:
                print(f"  {YELLOW}→{RESET} ... and {len(proof) - 5} more matches")
        else:
            print(f"  {BLUE}(No matches found){RESET}")
    else:
        print(f"  {proof}")
    
    print("=" * 80)

def cmdCheck(command, check):
    try:
        if not command:
            return False, "No command specified"
        
        args = shlex.split(command)
        result = subprocess.run(args, capture_output=True, text=True, timeout=30, check=False)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        output = stdout
        
        if not output and stderr:
            output = stderr
        
        passed = check is not None and str(check) in stdout
        
        if result.returncode != 0:
            if stderr:
                return False, stderr
            return False, f"Command exited with code {result.returncode}"
        
        return passed, output
    
    except subprocess.TimeoutExpired:
        return False, "Command timed out after 30 seconds"
    except FileNotFoundError:
        return False, f"Command not found: {command.split()[0] if command else 'unknown'}"
    except Exception as exc:
        return False, str(exc)

def textCheck(file, check):
    matches = []
    
    try:
        if not file:
            return False, "No file specified"
        
        if not os.path.isfile(file):
            return False, f"File not found: {file}"
        
        if check is None:
            return False, "No expected value specified"
        
        with open(file, "r", encoding="utf-8", errors="replace") as opened_file:
            for line in opened_file:
                stripped = line.strip()
                if str(check) in line and not stripped.startswith("#"):
                    matches.append(line.rstrip())
        
        return bool(matches), matches
    
    except PermissionError:
        return False, f"Permission denied: {file}"
    except Exception as exc:
        return False, str(exc)

def regexCheck(file, pattern):
    matches = []
    
    try:
        if not file:
            return False, "No file specified"
        
        if not os.path.isfile(file):
            return False, f"File not found: {file}"
        
        if not pattern:
            return False, "No regex pattern specified"
        
        compiled_pattern = re.compile(pattern)
        
        with open(file, "r", encoding="utf-8", errors="replace") as opened_file:
            for line in opened_file:
                stripped = line.strip()
                if compiled_pattern.search(line) and not stripped.startswith("#"):
                    matches.append(line.rstrip())
        
        return bool(matches), matches
    
    except re.error as exc:
        return False, f"Invalid regular expression: {exc}"
    except PermissionError:
        return False, f"Permission denied: {file}"
    except Exception as exc:
        return False, str(exc)

def permissionCheck(file, expected_perms):
    try:
        if not file:
            return False, "No file specified"
        
        if not os.path.exists(file):
            return False, f"File not found: {file}"
        
        if expected_perms is None:
            return False, "No expected permissions specified"
        
        stats = os.stat(file)
        perms = oct(stats.st_mode & 0o777)[2:].zfill(3)
        expected = str(expected_perms).strip()
        passed = perms == expected
        proof = f"Permissions: {perms}, Expected: {expected}"
        
        return passed, proof
    
    except PermissionError:
        return False, f"Permission denied: {file}"
    except Exception as exc:
        return False, str(exc)

def fileExistsCheck(file):
    try:
        if not file:
            return False, "No file specified"
        
        exists = os.path.exists(file)
        return exists, f"File exists: {exists}"
    
    except Exception as exc:
        return False, str(exc)

def fileLoad(file):
    try:
        if not file:
            print(f"{RED}Error:{RESET} No YAML file specified")
            return []
        
        if not file.lower().endswith((".yaml", ".yml")):
            file += ".yaml"
        
        if not os.path.isfile(file):
            print(f"{RED}Error:{RESET} YAML file not found: {file}")
            return []
        
        with open(file, "r", encoding="utf-8") as opened_file:
            data = yaml.safe_load(opened_file)
        
        if not isinstance(data, dict):
            print(f"{RED}Error:{RESET} Invalid YAML structure")
            return []
        
        raw_tests = data.get("tests", [])
        
        if not isinstance(raw_tests, list):
            print(f"{RED}Error:{RESET} 'tests' must be a list")
            return []
        
        tests = []
        
        for test in raw_tests:
            if not isinstance(test, dict):
                continue
            
            check = test.get("check") or {}
            frameworks = test.get("frameworks") or {}
            
            tests.append({
                "id": test.get("id"),
                "title": test.get("title"),
                "type": check.get("type"),
                "file": check.get("file"),
                "command": check.get("command"),
                "expected": check.get("expected"),
                "CIS": frameworks.get("CIS"),
                "ISO": frameworks.get("ISO27001"),
                "NIST": frameworks.get("NIST"),
                "category": test.get("category"),
                "severity": test.get("severity"),
            })
        
        return tests
    
    except yaml.YAMLError as exc:
        print(f"{RED}Error:{RESET} Invalid YAML: {exc}")
        return []
    except PermissionError:
        print(f"{RED}Error:{RESET} Permission denied: {file}")
        return []
    except OSError as exc:
        print(f"{RED}Error:{RESET} Could not read configuration: {exc}")
        return []
    except Exception as exc:
        print(f"{RED}Error while loading config:{RESET} {exc}")
        return []

def checkTests(tests, verbose=False):
    results = []
    total_tests = len(tests)
    passed_tests = 0
    
    print(f"\n{BOLD}Starting WomComp Compliance Scan...{RESET}")
    print(f"Total tests: {total_tests}")
    print("=" * 80)
    
    if total_tests == 0:
        print(f"{YELLOW}No tests to execute.{RESET}")
        return results
    
    test_results = []
    
    for index, test in enumerate(tests, 1):
        test_type = str(test.get("type") or "").lower()
        passed = False
        proof = "No check performed"
        
        if "file_contains" in test_type:
            passed, proof = textCheck(test.get("file"), test.get("expected"))
        elif "file_exists" in test_type:
            passed, proof = fileExistsCheck(test.get("file"))
        elif "permission" in test_type:
            passed, proof = permissionCheck(test.get("file"), test.get("expected"))
        elif "regex" in test_type:
            passed, proof = regexCheck(test.get("file"), test.get("expected"))
        elif "command" in test_type:
            passed, proof = cmdCheck(test.get("command"), test.get("expected"))
        else:
            passed, proof = cmdCheck(test.get("command"), test.get("expected"))
        
        if passed:
            passed_tests += 1
        
        test_results.append((test, passed, proof))
        results.append((test.get("id"), passed, proof))
        
        progressLine(index, total_tests, 50)
    
    sys.stdout.write("\n\n")
    sys.stdout.flush()
    
    if verbose:
        for test, passed, proof in test_results:
            printResult(test, passed, proof)
    
    failed_tests = total_tests - passed_tests
    compliance_score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print("\n" + "=" * 80)
    print(f"{BOLD}Scan Summary:{RESET}")
    print(f"  Total tests: {total_tests}")
    print(f"  {GREEN}Passed: {passed_tests}{RESET}")
    print(f"  {RED}Failed: {failed_tests}{RESET}")
    print(f"  {BOLD}Compliance Score: {compliance_score:.1f}%{RESET}")
    print("=" * 80)
    
    return results