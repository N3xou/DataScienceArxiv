import arxiv
import matplotlib.pyplot as plt
import requests
import PyPDF2
import os
import re
from scipy.stats import linregress
import numpy as np
client = arxiv.Client()

def create_box_plot(data, data2,data3):
    min_len = min(len(data), len(data2), len(data3))
    plt.figure(figsize=(8, 6))
    plt.boxplot([data, data2, data3],
                patch_artist=True,  # Fill box with color
                boxprops=dict(facecolor='lightblue', color='blue'),  # Color of the box
                whiskerprops=dict(color='black'),  # Color of whiskers
                capprops=dict(color='black'),  # Color of caps
                medianprops=dict(color='red', linewidth=2),  # Color and width of median line
                flierprops=dict(marker='o', markerfacecolor='green', markersize=8, linestyle='none'),
                showmeans=True

                # Style of outliers
                )

    plt.title('Number of references per year \ntagged with Image Classification(Arxiv)', fontsize=16, fontweight='bold')
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Number of references', fontsize=14)
    plt.xticks([1, 2, 3], ['2013', '2017', '2023'], fontsize=12)
    y_ticks = np.arange(0, 150, 10)
    plt.yticks(y_ticks, y_ticks)
    plt.grid(True, linestyle='--', alpha=0.7)


    plt.tight_layout()
    plt.legend()
    plt.show()

def download_pdf_for_year(year,folder_path):
    query = f"submittedDate:[{year}01010000 TO {year}12312359] AND Image Classification"
    search = arxiv.Search(query=query, max_results=1000)
    papers = client.results(search)

    for paper in papers:
        paper.download_pdf(dirpath=folder_path)


def convert_pdf_to_txt(folder_path):
    # List all files in the folder
    files = os.listdir(folder_path)

    # Iterate over each file in the folder
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name.lower().endswith('.pdf'):  # Check if it's a PDF file
            txt_file_path = os.path.splitext(file_path)[0] + '.txt'  # Create corresponding txt file path
            with open(file_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                text = ''
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text()
                try:
                    with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
                        txt_file.write(text)
                except (UnicodeEncodeError, Exception) as e:
                    print(f"Error: {e.__class__.__name__} occurred while processing {file_name}. Skipping...")
                    continue
            print(f"Converted {file_name} to {os.path.basename(txt_file_path)}")





def extract_highest_reference_number(file_path):
    highest_refnum = None
    current_refnum = 0
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        ref_pos = text.lower().rfind("references")  # Find the position of the word "references"
        if ref_pos != -1:  # If "references" is found
            text_after_references = text[ref_pos + len("references"):]  # Extract text after "references"
            matches = re.findall(r'\[(\d+)\]', text_after_references)  # Search for [number] in text after "references"
            for match in matches:
                if  current_refnum < int(match) < current_refnum+2:
                    current_refnum = int(match)
        if current_refnum > 0:
            highest_refnum = current_refnum
        else:
            if ref_pos != -1:  # If "references" is found
                matches = re.findall(r'(\d{1,2})\.', text_after_references)  # Search for [number] in text after "references"
                for match in matches:
                    if current_refnum < int(match) < current_refnum+2:
                        current_refnum = int(match)
        if current_refnum > 0:
            highest_refnum = current_refnum
    if highest_refnum is not None:
        return highest_refnum


def calculate_avg_refnum(folder_path):
    year = int(folder_path[-4:])
    highest_refnums = []
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith('.txt'):
            file_path = os.path.join(folder_path, file_name)
            highest_refnum = extract_highest_reference_number(file_path)
            if highest_refnum is not None and 4 < highest_refnum < 150:
                highest_refnums.append(highest_refnum)
    if highest_refnums:  # Check if there are any valid highest reference numbers
        avg_highest_refnum = sum(highest_refnums) / len(highest_refnums)
        print(f'Number of data values for year {year}: {len(highest_refnums)}')
        print(f'Highest references number for year {year}: {max(highest_refnums)}' )
        print(f'Mean references number for year {year}: {round(np.mean(highest_refnums))}')
        print(f'Average references number for year {year}: {round(avg_highest_refnum)}\n')
        return avg_highest_refnum,highest_refnums
    else:
        return None




# Running the functionsx

#download_pdf_for_year(2017,'./pdfs2017')

#convert_pdf_to_txt('./pdfs2017')


def showResults():

    avg_highest_refnum2013,highest_refnums2013 = calculate_avg_refnum('./texts2013')
    avg_highest_refnum2017,highest_refnums2017 = calculate_avg_refnum('./texts2017')
    avg_highest_refnum2023,highest_refnums2023 = calculate_avg_refnum('./texts2023')
    if avg_highest_refnum2013 is not None and avg_highest_refnum2023 is not None:
        create_box_plot(highest_refnums2013,highest_refnums2017,highest_refnums2023)
    else:
        print("No valid reference numbers found.")

showResults()
