# ir-vsm
Vector-Space Model (VSM) for Information Retrieval (IR) implemented for Assignment 1 in COL764.

## Requirements
**Python** *(recommended 3.6+)* is the language used by this project. Huge amount of data is processed during indexing and it is recommended to have good amount of RAM.

The project uses some inbuilt python libraries like `json`, `gzip`, `re`, `argparse` and takes help from some easily available libraries like `lxml` and `nltk` for pre-processing which can be installed using the command (`requirements.txt` has the complete list and part of it gets downloaded with the two main packages mentioned above)
```
pip3 install -r requirements.txt
```

`nltk` additionally requires `punkt` module for stemming. To download `punkt`, you can use the following code:
```python 
import nltk
nltk.download("punkt")
```
*(You can also use `nltk.download()`, which gives a GUI to download modules)*

To ease the installation, you can make use of the `makefile` provided. You can use the following command:
```
make
```


## File Structure
The main source files are 
- [`invidx.py`](#invidxpy) used for making the inverted indexes using a VSM
- [`vecsearch.py`](#vecsearchpy) to perform query search from the VSM
- [`printdict.py`](#printdictpy) is a helper tool for printing the dictionary,
- [`constants.py`](#constantspy) contains some constant values like `STOP_WORDS` that is used by the above programs
- [`utils.py`](#utilspy) contains some helper functions to calculate `tf` and `idf` in the above programs

### `invidx.py`
As mentioned earlier, this program builds the inverted indexes of the collection which can be run using: 
```
python3 invidx.py coll-path indexfile
```
where
* `coll-path` is the **directory** where the files of the collection is stored
* `indexfile` is the name of the generated index files

When the program is run, two files would have appeared, namely:
* `indexfile.dict` which contains the dictionary of words, document mapping and other informations
* `indexfile.idx` which contains the index postings

**Note: The directory of collections should not have any other files other than the document data. The format of each file follow the format given below.** Note that additional tags (along with more than one `<TEXT>` tag) can be present but each tag should be closed appropriately (XML standards) and content in all other tags except `<DOCNO>` and `<TEXT>` are ignored. The project is made primarily for English language.
```
<DOC>
	<DOCNO> A1234 </DOCNO>
	<TEXT> 
		Some text of the document
	</TEXT>
	<TEXT>
		There can be more text here...
	</TEXT>
	...
</DOC>
```

These files should have already been processed with named entities tagging (before being fed to `invidx.py`). Currently, it supports tags for *Location*, *Organization* and *Person* given in the following format (note that there should be a space after the opening and before the closing of the tag and each entity should be tagged **seperately**):

```
<DOC>
	<DOCNO> A1234 </DOCNO>
	<TEXT> 
		This is <PERSON> Ben </PERSON>. He is from <LOCATION> New </LOCATION> <LOCATION> York </LOCATION>. He works in <ORGANIZATION> Google </ORGANIZATION>. Observe how <LOCATION> New </LOCATION> <LOCATION> York </LOCATION> has been tagged.
	</TEXT>
	...
</DOC>
```

### `vecsearch.py`
This program is used for searching and ranking the documents related to the queries.

```python3 
python3 vecsearch.py --query queryfile --output resultfile --index indexfile --dict dictfile [--cutoff k=10]
```
The flags give the path for each file and k in cutoff is for "top k relevant documents" (default 10) will be there in the output file. The output file is based on the format used by `trec_eval` (more info can be obtained from [here](https://github.com/usnistgov/trec_eval))

You might use `-h` flag for a detailed information of each flag.

**Note: The files with query should follow the following format (given below).** Note that additional tags can be present but the `<title>` and `<num>` should NOT be closed. No other additional content should be present after the tags and each tag/query should be in seperate line.
```
<top>
	<num> Number:  001 
	<title> Topic:  Apple
	...
</top>
```

The current implementation supports prefix searching (match terms starting with a particular word) and restricted named entities searching (which restricts the term to be serached to a named entity) or a combination of both. Use `*` (e.g. `app*`) to match words like `app`,`apple`, etc. and for named entity restriction, you can use `L:` for location, `O:` for organization, `P:` for person and `N:` for any named entity. For example, query with `O:apple` would restrict retrieval to documents containing the organization 'Apple' and not, for instance, the fruit apple. `N:Apple` is equivalent to `L:Apple`, `O:Apple` and `P:Apple`. You can use `O:App*` for a combination of both the options.


### `printdict.py`

This program prints the dictionary produced from `invidx.py` in a human-readable form to the screen. The command for running this file is:

```
python3 printdict.py indexfile.dict
```

where `indexfile.dict` is the path to dictionary produced in `invidx.py`. It prints out each line in the following format:
```
<indexterm>:<df>:<index-of-postings-list-in-idx-file>
```



### `constants.py`
Contains the list of stop words and dictionaries to convert one-digit numbers and months to their short form, which are used by other programs.


### `utils.py`
Contains the tf and idf functions used by the model.


## Footnotes
- This program uses stopwords list taken from NLTK library. The list was taken from [here](https://gist.github.com/sebleier/554280) and few other words were added depending on the requirements.


---
Note: The programs were built for the Associated Press (AP) dataset and might not suit other datasets without pre-processing.

*More info can be obtained from [design.pdf](design.pdf)*


***Project by [Subhalingam D](https://subhalingamd.github.io)***
