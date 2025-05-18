import os
import re
import csv
import tkinter as tk
from tkinter import filedialog
from collections import defaultdict
from typing import Dict, List, Tuple, Counter

def CreateIndex(Dir: str, StopList: str) -> Tuple[Dict[int, str], Dict[str, Dict[int, int]]]:
    """
    Create an inverted index from files in a directory.
    
    Args:
        Dir (str): Directory containing the documents
        StopList (str): Name of stop word file in the directory (to be excluded)
    
    Returns:
        Tuple[Dict[int, str], Dict[str, Dict[int, int]]]: A tuple containing:
            - DocTable: Dictionary mapping document IDs to filenames
            - TermTable: Inverted index mapping terms to dictionaries of doc_id -> frequency
    """
    # Initialize data structures
    DocTable = {}  # Maps document IDs to filenames
    TermTable = defaultdict(lambda: defaultdict(int))  # Maps terms to {doc_id: frequency} dictionaries
    
    # Load stop words
    stop_words = set()
    stop_list_path = os.path.join(Dir, StopList)
    if os.path.exists(stop_list_path):
        with open(stop_list_path, 'r', encoding='utf-8', errors='ignore') as f:
            stop_words = {word.strip().lower() for word in f}
    
    # List of files to process (excluding the StopList file)
    files_to_process = [f for f in os.listdir(Dir) 
                         if os.path.isfile(os.path.join(Dir, f)) and f != StopList]
    print(f"Processing files: {files_to_process}")
    
    # Process each file
    for doc_id, filename in enumerate(files_to_process):
        file_path = os.path.join(Dir, filename)
        
        # Add file to DocTable
        DocTable[doc_id] = filename
        
        try:
            # Process file contents
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
                
                # Extract words (simple tokenization)
                words = re.findall(r'\b\w+\b', content)
                
                # Count words that start with 'c' (case insensitive) and not in stop words
                word_counts = Counter(word for word in words if word.startswith('c') and word not in stop_words)
                
                # Update TermTable with word frequencies
                for word, count in word_counts.items():
                    TermTable[word][doc_id] = count
        except Exception as e:
            print(f"Error processing file {filename}: {e}")
    
    # Convert nested defaultdicts to regular dicts for return
    return DocTable, {term: dict(doc_freqs) for term, doc_freqs in TermTable.items()}


def display_index(DocTable: Dict[int, str], TermTable: Dict[str, Dict[int, int]]) -> None:
    """Display the contents of the inverted index in a readable format."""
    print("Document Table:")
    print("---------------")
    for doc_id, filename in sorted(DocTable.items()):
        print(f"ID: {doc_id} -> {filename}")
    
    print("\nTerm Table:")
    print("-----------")
    for term, doc_freqs in sorted(TermTable.items()):
        doc_details = []
        for doc_id, freq in doc_freqs.items():
            doc_details.append(f"{DocTable[doc_id]} (freq: {freq})")
        print(f"'{term}' appears in: {list(doc_freqs.keys())} ({', '.join(doc_details)})")


def save_to_csv(DocTable: Dict[int, str], TermTable: Dict[str, Dict[int, int]]) -> None:
    """
    Save DocTable and TermTable to CSV files.
    
    Args:
        DocTable: Dictionary mapping document IDs to filenames
        TermTable: Inverted index mapping terms to dictionaries of doc_id -> frequency
    """
    # Save DocTable to CSV
    with open("doc_table.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Document ID", "Filename"])
        for doc_id, filename in sorted(DocTable.items()):
            writer.writerow([doc_id, filename])
    
    # Save TermTable to CSV
    with open("term_table.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Term", "Document IDs with Frequencies", "Document Names"])
        for term, doc_freqs in sorted(TermTable.items()):
            doc_details = []
            for doc_id, freq in doc_freqs.items():
                doc_details.append(f"{DocTable[doc_id]} (freq: {freq})")
            writer.writerow([term, str(dict(doc_freqs)), ", ".join(doc_details)])
    
    print("\nResults saved to doc_table.csv and term_table.csv")


def Find(Word: str, Weight: float, N: int, DocTable: Dict[int, str], TermTable: Dict[str, Dict[int, int]]) -> List[Tuple[str, float]]:
    """
    Find the top N documents associated with the specified word based on term frequency and weight.
    
    Args:
        Word (str): The word to search for
        Weight (float): The weight/importance of this search term
        N (int): Number of top documents to return
        DocTable (Dict[int, str]): Dictionary mapping document IDs to filenames
        TermTable (Dict[str, Dict[int, int]]): Inverted index mapping terms to dictionaries of doc_id -> frequency
    
    Returns:
        List[Tuple[str, float]]: List of tuples containing (document name, score) sorted by score in descending order
    """
    word = Word.lower()
    results = []
    
    # Check if word exists in the index
    if word not in TermTable:
        print(f"Word '{word}' not found in the index.")
        return []
    
    # Get document IDs and their frequencies for the word
    doc_freqs = TermTable[word]
    
    # Calculate scores based on term frequency and term weight
    for doc_id, freq in doc_freqs.items():
        doc_name = DocTable[doc_id]
        # Score is the product of term frequency and the term weight
        score = freq * Weight
        results.append((doc_name, score))
    
    # Sort by score in descending order
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N results
    return results[:N]


def FindFromFile(WordFile: str, N: int, DocTable: Dict[int, str], TermTable: Dict[str, Dict[int, int]]) -> List[Tuple[str, float]]:
    """
    Find the top N documents associated with words and weights specified in a file.
    
    Args:
        WordFile (str): Path to file containing word and weight pairs (one per line)
        N (int): Number of top documents to return
        DocTable (Dict[int, str]): Dictionary mapping document IDs to filenames
        TermTable (Dict[str, Dict[int, int]]): Inverted index mapping terms to dictionaries of doc_id -> frequency
    
    Returns:
        List[Tuple[str, float]]: List of tuples containing (document name, score) sorted by score in descending order
    """
    # Initialize a dictionary to accumulate scores for each document
    document_scores = defaultdict(float)
    
    try:
        # Read words and weights from the file
        with open(WordFile, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Parse word and weight from the line
                parts = line.split()
                if len(parts) >= 2:
                    word = parts[0].lower()
                    try:
                        weight = float(parts[1])
                    except ValueError:
                        print(f"Invalid weight for word '{word}', using default weight 1.0")
                        weight = 1.0
                    
                    # Check if word exists in the index
                    if word not in TermTable:
                        print(f"Word '{word}' not found in the index, skipping.")
                        continue
                    
                    # Get document IDs and their frequencies for the word
                    doc_freqs = TermTable[word]
                    
                    # Calculate and accumulate scores
                    for doc_id, freq in doc_freqs.items():
                        doc_name = DocTable[doc_id]
                        # Score is product of term frequency and query term weight
                        score = freq * weight
                        document_scores[doc_name] += score
                        
                else:
                    print(f"Ignoring invalid line: {line}")
        
        # Convert scores to list of tuples
        results = [(doc_name, score) for doc_name, score in document_scores.items()]
        
        # Sort by score in descending order
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N results
        return results[:N]
                
    except Exception as e:
        print(f"Error processing word file '{WordFile}': {e}")
        return []


def open_file_dialog(title="Select File", initialdir=None):
    """
    Open a file dialog and return the selected file path.
    This creates a fresh tkinter instance each time to avoid issues.
    """
    # Create a temporary Tkinter root window
    temp_root = tk.Tk()
    temp_root.withdraw()  # Hide the main window
    temp_root.attributes("-topmost", True)  # Ensure dialog appears on top
    
    # Open the file dialog
    file_path = filedialog.askopenfilename(
        parent=temp_root,
        title=title,
        initialdir=initialdir,
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    
    # Clean up
    temp_root.destroy()
    
    return file_path if file_path else None


def open_directory_dialog(title="Select Directory"):
    """
    Open a directory dialog and return the selected directory path.
    This creates a fresh tkinter instance each time to avoid issues.
    """
    # Create a temporary Tkinter root window
    temp_root = tk.Tk()
    temp_root.withdraw()  # Hide the main window
    temp_root.attributes("-topmost", True)  # Ensure dialog appears on top
    
    # Open the directory dialog
    directory = filedialog.askdirectory(
        parent=temp_root,
        title=title
    )
    
    # Clean up
    temp_root.destroy()
    
    return directory if directory else None


def main():
    # Set up the program
    print("Inverted Index Search Program")
    print("============================")
    
    # Select directory using dialog
    print("\nPlease select the directory containing your documents.")
    directory = open_directory_dialog("Select Directory Containing Documents")
    if not directory:
        print("No directory selected. Exiting program.")
        return
    
    # Select StopList file using dialog
    print("\nPlease select the StopList file.")
    stoplist_path = open_file_dialog("Select StopList File", directory)
    if not stoplist_path:
        print("No StopList file selected. Exiting program.")
        return
    
    # Extract just the filename from the path
    stoplist = os.path.basename(stoplist_path)
    
    print(f"\nProcessing directory: {directory}")
    print(f"Using stoplist: {stoplist}")
    
    # Create the index
    DocTable, TermTable = CreateIndex(directory, stoplist)
    
    print(f"\nCreated index with {len(DocTable)} documents and {len(TermTable)} terms")
    display_index(DocTable, TermTable)
    
    # Save results to CSV
    save_to_csv(DocTable, TermTable)
    
    while True:
        print("\nSearch options:")
        print("1. Search by single word")
        print("2. Search by word file")
        print("3. Exit")
        
        try:
            option = int(input("Enter your choice (1-3): "))
            
            if option == 1:
                # Single word search
                search_word = input("Enter a word to search: ")
                
                try:
                    word_weight = float(input("Enter the weight for this word (default is 1.0): ") or "1.0")
                except ValueError:
                    print("Invalid weight value. Using default weight 1.0.")
                    word_weight = 1.0
                
                top_n = int(input("Enter number of top documents to retrieve: "))
                
                # Find top N documents for the word
                results = Find(search_word, word_weight, top_n, DocTable, TermTable)
                
                if results:
                    print(f"\nTop {len(results)} documents for '{search_word}' (weight: {word_weight}):")
                    print("------------------------------------")
                    for doc_name, score in results:
                        print(f"Document: {doc_name}, Score: {score}")
                else:
                    print(f"No documents found containing '{search_word}'.")
                    
            elif option == 2:
                # Word file search
                print("\nPlease select the word file containing search terms and weights.")
                
                # Use a fresh dialog for file selection
                word_file = open_file_dialog("Select Word File")
                
                if not word_file:
                    print("No word file selected. Returning to menu.")
                    continue
                
                try:
                    top_n = int(input("Enter number of top documents to retrieve: "))
                    
                    # Find top N documents for the words in the file
                    results = FindFromFile(word_file, top_n, DocTable, TermTable)
                    
                    if results:
                        print(f"\nTop {len(results)} documents for query in '{os.path.basename(word_file)}':")
                        print("--------------------------------------------")
                        for doc_name, score in results:
                            print(f"Document: {doc_name}, Score: {score}")
                    else:
                        print(f"No documents found for query in '{os.path.basename(word_file)}'.")
                except ValueError:
                    print("Please enter a valid number for top N documents.")
                    
            elif option == 3:
                # Exit
                print("Exiting program.")
                break
                
            else:
                print("Invalid option, please try again.")
                
        except ValueError:
            print("Please enter a valid number.")


if __name__ == "__main__":
    main()
