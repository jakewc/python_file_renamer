Usage: `python renamer_run.py <absolute_directory_to_work_on>`
This script accepts one, and only one, absolute directory path.
It will rename all files which exactly match the filename pattern:
'[one or more characters].[any positive integer].[an image file extension]'
There must not be other files in the given directory which match the pattern:
'[filename which matches first pattern].temp'
The user must have write permissions for all working files.
To run tests, run `python -m unittest renamer_tests -b`.

# Assumptions
- Only tested on Linux, as this is what I use and also what Lex suggested
  the Pipeline team uses
- No non-builtin lib usage
- Path arg will always be absolute.
- Non-image files should not be ordered by the script, so need to
  pre-define image extensions. Therefore importing an extensible list of
  filetypes taken from github:
  https://github.com/arthurvr/image-extensions/blob/master/image-extensions.json
- When matching filename patterns:
  - There has to be at least one char before the first '.'
  - Image extensions are case-insensitive but
    prefixes (the part before the first '.') are case-sensitive
- All output filenums should have one leading zero.
- No two filenames can be EXACTLY identical, can only be as close
  as e.g x.1.jpg, x.01.jpg (*should be* enforced by file system).
- If two files originally had the same filenum (e.g. 'x.01.jpg' and 'x.1.jpg'),
  the one with more leading zeroes will always come first.
- The working dir cannot have e.g. both '1.1.jpg.temp' AND '1.1.jpg' in it
  when the util is run, see below.

# The Two-Pass Rename
As I see it, there are two ways to avoid rename collisions:
- The 'in-place' solution; 'shuffle' the filenames around to avoid conflicts,
  Tower-of-Hanoi-style.
  This would do an unpredictable number of renames which could be
  linear but could also be exponential, depending on how kind the original
  filenames are with their ordering. This would never conflict with
  anything else in the directory, but has runtime concerns at scale.
- The two-pass solution, which always does 2 * n renames by just
  renaming everything to the new name with .temp suffixed, then again to
  remove the suffix.
I have gone for the second option, but this does mean that the major limitation
of this util is that it can't operate on a directory which already contains
e.g. both '1.1.jpg.temp' AND '1.1.jpg'. It checks for this during validation
and exits if it finds this collision would occur.
