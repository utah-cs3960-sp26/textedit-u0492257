"""Tests for package initialization."""

import sys


def test_src_package_init():
    """Test that src package can be imported."""
    # Add src directory to path if not already there
    src_path = '/Users/austintopham/Desktop/cs3960/textedit-u0492257/src'
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Import the package
    import src
    
    # Check that __version__ is defined
    assert hasattr(src, '__version__')
    assert src.__version__ == "0.1.0"
