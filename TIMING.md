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
