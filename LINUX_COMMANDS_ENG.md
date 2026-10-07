# Useful Linux Commands (Non-Exhaustive List)

> **Note:** Parameters and options may vary depending on distribution and shell environment (notably for `touch`, `mkdir`, and `grep`).

```bash
# Search for occurrences of "error" in .log files with line numbers and context
grep -Hn -A 3 -B 2 "error" *.log

# Navigate to user's Documents directory
cd ~/Documents/

# List files and directories in long format
ls -l

# Create multiple python files simultaneously using brace expansion
touch {file1,file2}.py

# Create a directory with custom permissions
mkdir -m 755 tests
```
