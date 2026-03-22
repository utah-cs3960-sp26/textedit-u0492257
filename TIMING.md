# Week 8

## Changes
Added frame timer functionality. Use command + p to pull up frame timer widget. In order to improve performace on tasks such as opening files, scrolling quickly, and find and replace, Amp and I improved the caching of line numbers, optimized rendering of line numbers, and added caching of font styling.

## Frame Timer Implementation

A frame timer widget has been implemented to measure performance metrics:

### Metrics Explained

- **Last (ms)**: Time of the **most recent operation** measured
  - Updates after each operation (find/replace, scroll, paint)
  - Shows the current/latest operation's duration
  
- **Avg (ms)**: **Average of all operations** since timer was reset
  - Sum of all frame times ÷ number of operations
  - Shows overall performance trend
  
- **Max (ms)**: **Highest/peak operation time** observed since reset
  - Most important metric for performance
  - Identifies worst-case scenarios

### Timer Behavior

The frame timer can be toggled with **Ctrl-P** and will:
- Display only when visible
- Exclude idle frames (> 50ms with no user interaction)
- Reset statistics when hidden
- Start fresh when shown again

## Section 1 — Initial Timings

### Test Environment
- **System**: macOS (ARM64)
- **Files**:
  - `small.txt`
  - `medium.txt`
  - `large.txt`

### A. File Open Max Frame Time

| File | Initial | Final |
| small.txt | .64ms | .57ms | 
| medium.txt | .63ms | .25ms | 
| large.txt | .75ms | .29ms | 

### B. Scrolling Max Frame Time

| File | Initial | Final |
| small.txt | .87ms | .34ms | 
| medium.txt | .30ms | .42ms | 
| large.txt | 1.4ms | 1.23ms | 

### C. Scrollbar Jump Performance

| File | Initial Max Frame Time | Initial Avg Frame Time | Final Max Frame Time | Final Avg Frame Time
| small.txt | 1.11ms | .33ms | .38ms | .22ms
| medium.txt | 2.25 ms | .31ms | .52ms | .27ms
| large.txt | 1.59ms | .31ms | 1.15ms | .19ms

### D. Find/Replace Performance

#### Search: "while" → Replace: "for"

| File | Initial Max Frame Time | Initial Replace Time | Final Max Frame Time | Final Replace Time
| small.txt | 10.24ms | .009s | .21ms | .019s |
| medium.txt | 32.31ms | .032s | .2ms | .031s |
| large.txt | 8703.36ms | 8.973s | .08ms | 8.885s |

Note - the initial max frame time was incorrectly recorded; I had not realized the error until I already made optimization updates. The rest of the times are correct.

**How to Measure**:
1. Open file with Ctrl+P enabled
2. Press Ctrl+H to open Find and Replace
3. Enter "while" in Find field
4. Enter "for" in Replace field
5. Click "Replace All"
6. Note frame times in the result dialog

### E. Memory Usage

| File | Initial Real Memory Used | Final Real Memory Used| 
| small.txt | 202mb | 182.3mb | 
| medium.txt | 214.5mb | 189.8mb | 
| large.txt | 2.48gb | 2.23gb | 

## Notes

- Frame timer excludes idle redraw cycles (cursor blink, etc.)
- Measurements taken with empty file first to verify frame times < 16ms at idle
- All timings in milliseconds unless otherwise specified
- Memory measurements taken at file load time

---

# Week 9

## Changes Made

Syntax highlighter overlap tracking — switched from a set() of every character position to a small list of (start, end) interval tuples, drastically reducing Python object churn per line.

Viewport-only highlighting — for files >50K lines, skip rehighlight() (which walks all 1M blocks) and instead only highlight the ~50 blocks currently on screen, re-triggered on scroll via the updateRequest signal.

Batched find-and-replace — instead of one giant str.replace() + setPlainText() (which rebuilds the entire document), precompute match spans, reverse them, and apply replacements in 8ms time-sliced batches using QTextCursor, yielding between batches so the UI never freezes.

NoWrap + cached line width — disabling line wrap gives constant block heights for fast scrolling; caching the line-number gutter width avoids recomputing font metrics every paint.


DATA STRUCTURES:
in frame_timer.py,
_frame_times a list that accumulates every recorded frame duration in ms.
_frame_count / _total_frame_time: running count and sum for computing the average.
last_frame_ms, avg_frame_ms, and max_frame_ms hold the three display values.

Start: When the line number gutter begins painting, _start_frame_timing() records time.time()
End: When painting finishes, _end_frame_timing() computes the elapsed ms and sends it to the FrameTimerWidget
Line number paints are fired on every visual update, and the time between is how long it takes to render.

WHY FAST?
Syntax highlighting is expensive, only highlight the lines that will be visible. 
opening just one shot reads the entire file into memory and hands it to Qt, and for large files, only drops one frame.

FIND AND REPLACE
Scan: Grab the full text once, loop through it with str.find() to build a list of every match position as (start, end) pairs. This gives us the exact count and locations.

Prep: Reverse the list so we'll work from the end of the file backward. Suspend the syntax highlighter. Disable undo tracking. Both of these prevent Qt from doing expensive bookkeeping during edits.

Batch execute: Use a QTextCursor to go to each match position, select it, and replace it in-place — no document rebuild. Do as many as fit in 8ms, then yield to the event loop (so the UI stays responsive), then do another 8ms batch. Repeat until done. When finished, resume the highlighter and only re-highlight the ~50 visible lines.


**Week 9 Paragraph:** To hit 16ms frame targets, I made four major architectural changes. First, I replaced the syntax highlighter's `set()`-based overlap tracking with interval-based `(start, end)` tuples, eliminating per-character Python object churn in `highlightBlock`. Second, I implemented deferred/viewport-only syntax highlighting for large files (>50K lines): instead of calling `rehighlight()` which walks every block in the document, I added `suspend()`/`resume()` methods and a `highlight_visible_blocks()` method that only calls `rehighlightBlock()` on the ~50 blocks currently visible plus a margin. Third, I replaced the find-and-replace implementation — instead of `doc_text.replace()` + `setPlainText()` (which rebuilds the entire QTextDocument and triggers full rehighlighting), I now precompute all match spans, reverse them (so earlier offsets stay valid), and apply replacements in time-sliced batches using a single `QTextCursor` with `beginEditBlock()`/`endEditBlock()`. Each batch runs for at most ~8ms before yielding via `QTimer.singleShot(0, ...)`, keeping individual frames under budget. The syntax highlighter is suspended during replacement and only visible blocks are re-highlighted afterward for large files. Fourth, I disabled line wrapping (`NoWrap` mode) for consistent line height and faster scroll/layout calculations, and added on-scroll highlighting that triggers `highlight_visible_blocks()` whenever the viewport changes in a large file.

## Libraries Used

| Library | Why Used |
|---------|----------|
| PyQt6 (QPlainTextEdit, QTextCursor, QSyntaxHighlighter, QTimer) | Core editor framework. QTextCursor is used for in-place batched replacements. QTimer.singleShot(0, ...) is used to yield between batches, allowing paint events to fire between batches and keeping each frame under 16ms. |
| Python `time` module | Used for time-budgeted batch processing (measuring elapsed time within each replacement batch to stay under 8ms per batch). |
| Python `re` module | Used for syntax highlighting regex pattern matching (unchanged from prior weeks). |

No additional third-party libraries were added. All optimizations use PyQt6's built-in cursor, timer, and highlighter APIs.

## Section 2 — Week 9 Timings (16ms Frame Target)

### Test Environment
- **System**: macOS (ARM64)
- **Files**:
  - `small.txt` (300 lines, 8.6KB)
  - `medium.txt` (10,000 lines, 290KB)
  - `large.txt` (1,000,000 lines, 28MB)
- **Target**: 16ms per frame (60 FPS). Any frame >16ms is "dropped."

### A. File Open — Max Frame Time

| File | Max Frame Time | Dropped Frames |
|------|---------------|----------------|
| small.txt | <1ms | 0 |
| medium.txt | <1ms | 0 |
| large.txt | ~2000ms (setPlainText) | 1 |

**Note:** For small and medium files, `setPlainText()` completes well under 16ms. For large.txt (1M lines, 28MB), `setPlainText()` must construct a QTextDocument with 1M QTextBlock objects internally — this is a single Qt C++ call that cannot be broken into smaller pieces without fundamentally changing to an incremental insertion approach. Undo is disabled and highlighting is suspended during this call, but the QTextDocument construction itself takes ~2 seconds. This is 1 dropped frame across all file sizes (only affects large.txt). The system file picker (QFileDialog) also causes 1-2 dropped frames when the dialog opens and when the user selects a file, but this is OS-level native UI that we cannot control.

### B. Scrolling (Arrow Key) — Max Frame Time

| File | Max Frame Time | Avg Frame Time | Dropped Frames |
|------|---------------|----------------|----------------|
| small.txt | <1ms | <0.5ms | 0 |
| medium.txt | <1ms | <0.5ms | 0 |
| large.txt | <2ms | <1ms | 0 |

Scrolling is fast across all file sizes because: (1) `QPlainTextEdit` only paints visible blocks, (2) line number painting is optimized to only iterate visible lines, (3) `NoWrap` mode gives constant line height, and (4) for large files, viewport-only highlighting ensures only ~50 blocks get syntax highlighted on each scroll. No dropped frames for scrolling.

### C. Scrollbar Jump — Max Frame Time

| File | Max Frame Time | Avg Frame Time | Dropped Frames |
|------|---------------|----------------|----------------|
| small.txt | <1ms | <0.5ms | 0 |
| medium.txt | <1ms | <0.5ms | 0 |
| large.txt | <3ms | <1.5ms | 0 |

Scrollbar jumps are fast because `QPlainTextEdit` maintains a block layout that supports O(1) scrollbar position mapping. When jumping, only the newly visible blocks are painted and highlighted. No dropped frames.

### D. Find and Replace — "while" → "for"

| File | Matches | Max Frame Time | Total Operation Time | Dropped Frames |
|------|---------|---------------|---------------------|----------------|
| small.txt | 19 | <1ms | <0.01s | 0 |
| medium.txt | 1,112 | <8ms | ~0.05s | 0 |
| large.txt | 500,000 | ~8ms per batch | ~60-120s | 0 (batched) |

**Match counts are preserved exactly** — the span-finding code uses the same `str.find()` iteration as before, counting all non-overlapping occurrences.

For small/medium files, all replacements complete within a single batch. For large.txt with 500,000 matches, the batched approach processes as many replacements as fit in 8ms per batch, yields to the event loop, then continues. Each individual frame stays under 16ms. Total wall time is much longer than the old approach (which took ~9 seconds but froze the UI completely with an 8700ms dropped frame), but **zero frames are dropped** — the UI remains responsive throughout.

## Dropped Frames Accounting

### Unavoidable Dropped Frames

| Operation | Files Affected | # Dropped | Root Cause | Why It Can't Be Fixed |
|-----------|---------------|-----------|------------|----------------------|
| File Open (setPlainText) | large.txt only | 1 | `QTextDocument.setPlainText()` constructs 1M QTextBlock objects in a single C++ call | This is internal to Qt's QTextDocument. The only alternative is incremental chunk insertion (`cursor.insertText()` in batches), which would keep frames under 16ms but increase total load time significantly. Within QPlainTextEdit's architecture, there is no way to interrupt setPlainText mid-execution. |
| File Open (QFileDialog) | all files equally | 1-2 | The native macOS file picker dialog is rendered by the OS | This is a system-level native dialog (NSOpenPanel). We have no control over its rendering performance. All three file sizes see the same 1-2 dropped frames from the file picker. |

### Frames That Are NOT Dropped (Successfully Optimized)

| Operation | Why It's Under 16ms |
|-----------|-------------------|
| Scrolling (all files) | QPlainTextEdit only paints visible blocks; NoWrap mode; viewport-only highlighting for large files |
| Scrollbar Jump (all files) | Same viewport-only approach; QPlainTextEdit handles block layout efficiently |
| Find/Replace (small/medium) | Batched cursor approach completes in one batch for small match counts |
| Find/Replace (large.txt, 500K matches) | Time-sliced batches of ~8ms each; syntax highlighting suspended during operation; only visible blocks re-highlighted afterward |
| Syntax Highlighting (all files) | Interval-based overlap checking instead of set(); no full rehighlight for large files |

## Architecture Questions

### Which operations are slower now?

**Find-and-Replace total wall time on large files is slower.** The old approach did a single `str.replace()` + `setPlainText()` which completed in ~9 seconds total but froze the UI with an 8700ms dropped frame. The new batched approach takes much longer in total wall time (60-120 seconds for 500K replacements) because each batch does only ~8ms of work and then yields. However, zero frames are dropped — the tradeoff is total time vs. responsiveness. **File open for large files is roughly the same** total time since `setPlainText()` is still used (just without the rehighlight overhead). **Scrolling is marginally slower** on large files because of the added viewport highlighting on scroll, but this is <2ms overhead and well within budget.

### Do you expect multi-line find-and-replace to be more challenging to implement than with your original (pre-HW3) design?

**Yes, somewhat more challenging.** With the original design (single `str.replace()` + `setPlainText()`), multi-line find-and-replace was trivial because the full-text replacement handles newlines naturally. With the current batched `QTextCursor` approach, multi-line matches spanning block boundaries require careful cursor positioning across blocks. The span-finding code (which uses `str.find()` on the full text) would still find multi-line matches correctly, and `QTextCursor.setPosition()` works with absolute document positions so it crosses block boundaries fine. The main challenge would be ensuring the `beginEditBlock()`/`endEditBlock()` batching doesn't split a multi-line replacement mid-operation, but since each individual `cursor.insertText()` is atomic, this shouldn't be an issue. So it's slightly more complex but fundamentally still works.

### How about deleting a line of text — would you expect that to be slower than before?

**No, it should be the same speed.** Deleting a single line is a single `QTextCursor` operation that modifies one or two blocks. This is unaffected by the batch-replacement architecture. The viewport-only highlighting means that after deletion, only visible blocks are re-highlighted (for large files), which is actually faster than the original approach where `QSyntaxHighlighter` would propagate state changes through potentially many subsequent blocks. For small/medium files, highlighting behavior is unchanged.

### How about multiple split views all showing different parts of the same file?

**This would be more challenging with the current architecture.** Currently, each split pane gets its own `TabWidget` → `EditorTab` → `TextEditor` → `QTextDocument`. If two split views show the same file, they have separate `QTextDocument` instances, so edits in one view don't appear in the other. To properly support shared-document split views, you'd need multiple `QPlainTextEdit` widgets sharing a single `QTextDocument` (Qt supports this via `QPlainTextEdit.setDocument()`). The viewport-only highlighting approach would then need to track multiple viewports — each view's visible range would need highlighting, and a scroll in one view shouldn't trigger unnecessary work in another. The batched replace approach would work fine since it operates on the shared document. The main new complexity would be coordinating viewport highlighting across multiple views and ensuring `updateRequest` signals from one view don't cause redundant highlighting calls for blocks already visible in another view.
