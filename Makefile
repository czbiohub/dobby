test-cli:
	dobby make_echo_pick_lists test/data/MAA000154.txt MAA000154 30_2_M --plot --output-folder test_output

test-io:
	dobby parse_fluorescence test/data/MAA000154.txt --filetype txt > test/data/MAA000154.csv

test-io-heatmap:
	dobby parse_fluorescence test/data/MAA000154.txt --filetype txt --figure-folder test_output > test/data/MAA000154.csv