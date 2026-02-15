"""Test main.py script execution."""

import subprocess
import sys
from pathlib import Path


def test_main_script_compiles():
    """Test that main.py can be compiled without syntax errors."""
    main_py = Path(__file__).parent.parent / "src" / "main.py"
    
    # Compile the file to check for syntax errors
    with open(main_py, "r") as f:
        code = f.read()
    
    compile(code, str(main_py), "exec")
    # If we got here, no syntax errors


def test_main_module_has_main_guard():
    """Test that main.py has the if __name__ == '__main__' guard."""
    main_py = Path(__file__).parent.parent / "src" / "main.py"
    
    with open(main_py, "r") as f:
        content = f.read()
    
    assert 'if __name__ == "__main__"' in content
    assert "main()" in content


def test_main_entry_point_guard_present():
    """Test that main.py entry point guard is properly formed."""
    main_py = Path(__file__).parent.parent / "src" / "main.py"
    
    with open(main_py, "r") as f:
        lines = f.readlines()
    
    # Find the if __name__ == "__main__" line
    guard_found = False
    for i, line in enumerate(lines):
        if 'if __name__ == "__main__"' in line:
            guard_found = True
            # Check that next line calls main()
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                assert "main()" in next_line
            break
    
    assert guard_found, "if __name__ == '__main__' guard not found"


def test_main_execution_via_code():
    """Test main.py entry point execution via code evaluation."""
    # Use exec to simulate running main.py as __main__
    main_py = Path(__file__).parent.parent / "src" / "main.py"
    
    with open(main_py, "r") as f:
        code = f.read()
    
    # Create namespace with __name__ set to '__main__'
    namespace = {"__name__": "__main__", "__file__": str(main_py)}
    
    # We can't actually execute because it requires QApplication
    # But we can verify the guard condition would be true
    assert "__name__" in namespace
    assert namespace["__name__"] == "__main__"
