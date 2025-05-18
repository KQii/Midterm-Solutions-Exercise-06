# Inverted Index Search Engine

An implementation of an inverted index system for text document search and retrieval.

## Problem Statement

This program creates and uses inverted indexes with the following functionalities:

- **CreateIndex(Dir, StopList)**: Takes a directory name and a file called StopList (in that directory) as input. It returns an inverted index as output. The DocTable includes all files in the directory Dir, except for the StopList file. The TermTable includes only all words occurring in the directory that start with the letter "c" (lower- or uppercase).

- **Find(Word, Weight, N)**: Finds the top N documents in the index associated with the specified word, considering the given weight.

- **FindFromFile(WordFile, N)**: Similar to the above, but instead of taking a single word as input, it takes a file called WordFile. This file has, on each line, a word (string) and a weight (float). It then attempts to find, using the inverted index, the top N matches for this query.

## Implementation Details

### Data Structures

The program uses two main data structures:

1. **DocTable**: A dictionary mapping document IDs (integers) to document names (filenames)

   ```
   DocTable = {
       0: "document1.txt",
       1: "document2.txt",
       # ...
   }
   ```

2. **TermTable**: An inverted index mapping terms to dictionaries that map document IDs to term frequencies
   ```
   TermTable = {
       "computer": {0: 5, 2: 3},  # "computer" appears 5 times in doc 0, 3 times in doc 2
       "cloud": {1: 7, 4: 2},     # "cloud" appears 7 times in doc 1, 2 times in doc 4
       # ...
   }
   ```

### Key Functions

#### CreateIndex(Dir, StopList)

This function:

- Takes a directory path and a stop words file name as input
- Loads stop words from the specified file
- Processes each file in the directory (excluding the stop list file)
- Extracts words from each document
- Filters to include only words starting with 'c' (case insensitive)
- Removes stop words
- Counts word frequencies
- Builds the DocTable and TermTable
- Returns both tables

#### Find(Word, Weight, N)

This function:

- Searches for a specific word in the TermTable
- Calculates document scores based on term frequency \* weight
- Returns the top N documents sorted by score

#### FindFromFile(WordFile, N)

This function:

- Reads words and their weights from a file
- Accumulates scores for documents across all query terms
- Returns the top N documents sorted by total score

### Helper Functions

- **display_index()**: Displays the contents of DocTable and TermTable
- **save_to_csv()**: Saves DocTable and TermTable to CSV files
- **main()**: The main program loop that handles user interaction

## Installation Guide

### Prerequisites

- Python 3.6 or higher

### Installation Steps

1. Ensure Python is installed on your system:

   ```
   python --version
   ```

2. Download the inverted_index.py file to your preferred location

## Setup Instructions

1. Clone the repository:

   ```
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Run the program:
   ```
   python inverted_index.py
   ```

## Usage Instructions

### Running the Program

1. Open a terminal or command prompt
2. Navigate to the directory containing the inverted_index.py file
3. Run the program:
   ```
   python inverted_index.py
   ```

### Using the Program

After running the program, follow these steps:

1. **Specify Document Directory**:

   - When prompted, enter the full path to the directory containing your text documents

2. **Specify StopList File**:

   - Enter the name of the file containing stop words (words to be excluded from indexing)

3. **View the Created Index**:

   - The program will display the created DocTable and TermTable
   - The results will also be saved to CSV files (doc_table.csv and term_table.csv)

4. **Search Options**:
   - Option 1: Search by a single word
     - Enter the word, its weight, and the number of results to retrieve
   - Option 2: Search using a word file
     - Enter the path to a file containing words and weights
     - Enter the number of results to retrieve
   - Option 3: Exit the program

### Word File Format

The word file should have the following format:

```
word1 weight1
word2 weight2
...
```

Example:

```
computer 1.5
coding 2.0
cloud 0.8
```

## Examples

### Example 1: Creating an Index

Input:

- Directory: /documents
- StopList: stopwords.txt

Contents of Directory:

- article1.txt: "Computer science is a fascinating field. Computing power has increased."
- article2.txt: "Cloud computing is revolutionizing IT. Companies are moving to the cloud."
- stopwords.txt: "is a the to are"

Output:

```
Document Table:
---------------
ID: 0 -> article1.txt
ID: 1 -> article2.txt

Term Table:
-----------
'computer' appears in: [0] (article1.txt (freq: 1))
'computing' appears in: [0, 1] (article1.txt (freq: 1), article2.txt (freq: 1))
'cloud' appears in: [1] (article2.txt (freq: 2))
'companies' appears in: [1] (article2.txt (freq: 1))
```

### Example 2: Single Word Search

Input:

- Word: "computing"
- Weight: 1.5
- N: 2

Output:

```
Top 2 documents for 'computing' (weight: 1.5):
-------------------------------------
Document: article1.txt, Score: 1.5
Document: article2.txt, Score: 1.5
```

### Example 3: Word File Search

Input:

- WordFile: query.txt containing:
  ```
  computing 1.5
  cloud 2.0
  ```
- N: 2

Output:

```
Top 2 documents for query in 'query.txt':
-------------------------------------
Document: article2.txt, Score: 5.5
Document: article1.txt, Score: 1.5
```

## Notes and Limitations

- The index only includes words starting with the letter 'c'
- The program uses a simple tokenization approach
- Stop words are excluded from the index
