## How to Run

use "python3 -m pytest" to run the tests.

use "python3 -m pytest --cov=src --cov-report=term-missing" to run code coverage report.

## Percent of Code Covered by Tests: 99.8%

## Exceptions

1. Lines 232-233 in text_editor.py. These lines are checking that the cursor position never reaches the character count. However, Qt already has checks for this in place, so line 233 is theoretically unreachable, but still good to have as a backup test in case Qt introduces bugs related to this scenario with a future version.

[`src/editor/text_editor.py#L232-L233`](src/editor/text_editor.py#L232-L233)

2. Line 19 in main.py. Doesn't contain any real logic, does not need to be tested.

[`src/main.py#L18-L19`](src/main.py#L18-L19)

