all: prereq pip ext
	
.SILENT: prereq pip ext


.PHONY: all


prereq: 
	echo "\n+ Checking if required files present..."
	test -f requirements.txt || (echo "\t- requirements.txt not found." && exit "1")
	test -f invidx.py || (echo "\t- invidx.py not found." && exit "1")
	test -f printdict.py || (echo "\t- [Warn] printdict.py not found.")
	test -f vecsearch.py || (echo "\t- vecsearch.py not found." && exit "1")
	test -f utils.py || (echo "\t- utils.py not found." && exit "1")
	test -f constants.py || (echo "\t- constants.py not found." && exit "1")
	test -f README* || (echo "\t- [Warn] README not found.")
	test -f design.pdf || (echo "\t- [Warn] design.pdf not found.")
	echo "All required files for running the project found.\n\n"

pip: 
	echo "+ Getting external libraries..."
	pip3 install -U -r requirements.txt && echo "Success.\n\n" || exit "2"
	
ext:
	echo "+ Downloading punkt for NLTK"
	echo "import nltk\nif nltk.download('punkt'):\n\tprint('Success.')\nelse:\n\tprint('Failed :/')" | python3