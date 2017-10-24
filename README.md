# dobby
Dobby is the heroic house-elf that automates SampleSheet generation from Google Sheets

# install
Install Anaconda https://www.anaconda.com/download/. Maker sure to add it to your path

```
conda create --yes -n dobby pandas jupyter six matplotlib seaborn scipy python=3.6
source activate dobby
pip install -e .
make test-cli
```

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
  aggregate    Collect cherrypicked files into 384-well ECHO pick list ready
               files
  cherrypick   Use 384-well plate reader fluorescence to choose only cells
               with high enough signals
  samplesheet  Create an Illumina sample sheet using a template
```

# Running tests
Make sure you're in a dobby environment

```
cd test
python -m unittest test_cherrypick
```

to run just one test

```
python -m unittest test_cherrypick.TestCherrypick.test_2_flagged
```

### Outputs

Dobby outputs to the following folders:

```
cherrypicked/             # Tidy tables of samples with enough concentration
concentration/            # Heatmap of concentration data
flagged/
    1stpass_regression/   # If regression R < 0.98
    2ndpass_blanks/       # If mean blanks < 0
    3rdpass_samples/      # If number of samples passing QC < 50
    repeat_flags/         # Samples that got flagged with more than one criteria
fluorescence/             # Heatmap of fluorescence data
non-cherrypicked/         # Tidy tables of all samples
regression/               # Regression plots of standards
```

### Example: Cherrypick

You can "cherrypick" the best samples out of a 384-well plate whose
fluorescence is high enough using `dobby cherrypick`:

```
$ dobby cherrypick -h
Usage: dobby cherrypick [OPTIONS] FILENAME PLATE_NAME MOUSE_ID

  Transform plate of cDNA fluorescence to ECHO pick list

  Parameters
  ----------
  filename : str
       Name of the cDNA fluorescence 384 well QC output plate_name mouse_id filetype standards_col blanks_col
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

### Example: Aggregate



```
dobby  aggregate  --desired-concentration 0.3 ~/Google\ Drive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3\ Month/cherrypicked/*.csv --output-folder ~/Google\ Drive/MACA/cDNA\ Pick\ Lists/3_month/
```

Advanced usage: sort files by date, then aggregate:

```
$ ls -Str ~/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/*.csv | xargs dobby aggregate  --desired-concentration 0.3  --output-folder ~/googledrive/MACA/cDNA\ Pick\ Lists/3_month/
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000937_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/D041912_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00000.csv
Wrote 1 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/D041914_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00001.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/D042193_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/D042479_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00002.csv
Wrote 1 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000400_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00003.csv
Wrote 3 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000424_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000452_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000510_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00004.csv
Wrote 3 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000531_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000538_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000550_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00005.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000554_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000559_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00006.csv
Wrote 1 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000578_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00007.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000586_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000587_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00008.csv
Wrote 3 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000593_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000599_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000611_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00009.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000612_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000776_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00010.csv
Wrote 1 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000871_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00011.csv
Wrote 1 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000909_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00012.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000923_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000928_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00013.csv
Wrote 3 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000932_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000935_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000940_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00014.csv
Wrote 1 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/D041911_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00015.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/D042044_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/D042180_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00016.csv
Wrote 1 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/D042253_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00017.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/D042467_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/D042474_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00018.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/D042475_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000377_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00019.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000385_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000398_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00020.csv
Wrote 3 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000409_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000439_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000441_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00021.csv
Wrote 1 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000487_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00022.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000560_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000564_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00023.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000571_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000572_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00024.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000573_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000577_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00025.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000583_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000592_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00026.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000595_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000596_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00027.csv
Wrote 1 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000603_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00028.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000604_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000605_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00029.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000609_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000617_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00030.csv
Wrote 1 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000652_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00031.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000752_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000844_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00032.csv
Wrote 1 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000848_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00033.csv
Wrote 3 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000870_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000873_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000891_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00034.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000899_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000901_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00035.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000908_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000914_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00036.csv
Wrote 4 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000918_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000919_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000922_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000925_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00037.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000927_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000930_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00038.csv
Wrote 2 files (/home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000938_echo.csv, /home/dobby/googledrive/MACA/384W_QC/plate_reader/raw_plate_reader_output/3_Month/cherrypicked/MAA000944_echo.csv) to /home/dobby/googledrive/MACA/cDNA Pick Lists/3_month/echo_picklist_00039.csv
(0) files () didn't make it into a pick list :(
```

### Example: Samplesheet

```
$ dobby samplesheet --output-folder test_samplesheet test_aggregate/echo_picklist_00015.csv XT-C-04
Wrote test_samplesheet/echo_picklist_00015_samplesheet.csv
```
