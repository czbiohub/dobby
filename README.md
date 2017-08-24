# dobby
Dobby is the heroic house-elf that automates SampleSheet generation from Google Sheets

## Usage

To get help on how to use `dobby`, use the command `dobby -h`:

```
$ dobby -h 
Usage: dobby  <command>

  Hi! Dobby is the heroic house-elf that automates SampleSheet generation
  from Google Sheets. And, of course, Dobby is free.

Options:
  -h, --help  Show this message and exit.

Commands:
  cherrypick  Convert concentrations --> ECHO pick list
```

### Example: Cherrypick

Right now, the only command is to "cherrypick" a fluorescence plate reader output:

```
$ dobby cherrypick -h
Usage: dobby cherrypick [OPTIONS] FILENAME PLATE_NAME MOUSE_ID

  Transform plate of cDNA fluorescence to ECHO pick list

  Parameters ---------- filename : str     Name of the cDNA fluorescence 384
  well QC output plate_name mouse_id filetype standards_col blanks_col
  standards plot output_folder

  Returns -------

Options:
  --filetype TEXT
  --standards-col INTEGER
  --blanks_col INTEGER
  --standards TEXT
  --plot
  --output-folder TEXT
  -h, --help               Show this message and exit.
```

Here is an example usage of it:


```
$ dobby cherrypick testing/MAA000154.txt MAA000154 30_2_M --plot --output-folder test_output
MAA000154: Wrote regression plot to test_output/regression/MAA000154_regression_lines.pdf
MAA000154: Wrote fluorescence heatmap to test_output/fluorescence/MAA000154_fluorescence_heatmap.pdf
MAA000154: Wrote concentrations heatmap to test_output/concentrations/MAA000154_concentrations_heatmap.pdf
MAA000154 (30_2_M) has 249 cells passing Concentration QC
MAA000154: Wrote concentrations_cherrypicked_no_standards_or_blanks heatmap to test_output/concentrations_cherrypicked_no_standards_or_blanks/MAA000154_concentrations_cherrypicked_no_standards_or_blanks_heatmap.pdf
Wrote cherrypicked ECHO pick list to test_output/cherrypicked/MAA000154_echo.csv
Wrote non_cherrypicked ECHO pick list to test_output/non_cherrypicked/MAA000154_echo.csv
```