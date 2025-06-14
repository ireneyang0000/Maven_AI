import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
import time

def simplify_cvpr_scrape(url="https://openaccess.thecvf.com/CVPR2024?day=all"):
    """
    Scrapes paper titles, authors, PDF links, and supplementary material links 
    from the CVPR 2024 website based on the actual HTML structure.
    """
    print(f"Fetching data from: {url}")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    papers_data = []
    
    # Get all text content and split into lines
    all_text = soup.get_text()
    lines = all_text.split('\n')
    
    print(f"Processing {len(lines)} lines of text...")
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and navigation elements
        if not line or line in ['Back', 'Papers', 'CVPR 2024 CVF', 'CVPR 2024 open access']:
            i += 1
            continue
            
        # Look for paper titles (they are typically longer lines without special characters at the start)
        if (len(line) > 20 and 
            not line.startswith('@') and 
            not line.startswith('[') and 
            not line.startswith('Powered by:') and
            not line.startswith('Sponsored by:') and
            not line.startswith('These CVPR') and
            not line.startswith('Except for') and
            not line.startswith('This material') and
            not line.startswith('Copyright') and
            not line.startswith('All persons') and
            not line.startswith('Microsoft') and
            not line.startswith('Amazon') and
            not line.startswith('Facebook') and
            not line.startswith('Google')):
            
            paper_info = {'Title': line}
            
            # Look for authors in the next few lines
            authors = []
            j = i + 1
            while j < len(lines) and j < i + 10:  # Look up to 10 lines ahead
                next_line = lines[j].strip()
                
                # If we hit another potential title or special content, stop
                if (len(next_line) > 20 and 
                    not next_line.startswith('@') and 
                    not next_line.startswith('[') and
                    not next_line.startswith('Powered by:') and
                    not next_line.startswith('Sponsored by:')):
                    break
                    
                # If we hit a line with commas, it's likely authors
                if ',' in next_line and len(next_line) > 5:
                    authors.append(next_line)
                elif next_line and not next_line.startswith('[') and not next_line.startswith('@'):
                    # Single author or continuation
                    authors.append(next_line)
                    
                j += 1
            
            if authors:
                paper_info['Authors'] = '; '.join(authors)
            
            # Look for links in the surrounding area
            # Find the bibtex entry for this paper
            bibtex_start = None
            for k in range(i, min(i + 50, len(lines))):
                if lines[k].strip().startswith('@InProceedings'):
                    bibtex_start = k
                    break
            
            if bibtex_start:
                # Extract links from the area around the bibtex
                for k in range(max(0, bibtex_start - 10), min(len(lines), bibtex_start + 10)):
                    line_k = lines[k].strip()
                    
                    # Look for [pdf], [supp], [arXiv] links
                    if '[pdf]' in line_k.lower():
                        # Find the actual PDF link in the HTML
                        pdf_link = soup.find('a', href=re.compile(r'\.pdf$', re.IGNORECASE))
                        if pdf_link:
                            paper_info['PDF Link'] = requests.compat.urljoin(url, pdf_link['href'])
                    
                    if '[supp]' in line_k.lower():
                        # Find supplementary material link
                        supp_links = soup.find_all('a', href=re.compile(r'\.(zip|gz|tgz|rar|mp4|mov|avi|gif)$', re.IGNORECASE))
                        if supp_links:
                            paper_info['Supplementary Material Link'] = requests.compat.urljoin(url, supp_links[0]['href'])
                    
                    if '[arxiv]' in line_k.lower():
                        # Find arXiv link
                        arxiv_link = soup.find('a', href=re.compile(r'arxiv\.org', re.IGNORECASE))
                        if arxiv_link:
                            paper_info['arXiv Link'] = arxiv_link['href']
            
            papers_data.append(paper_info)
            print(f"Found paper: {line[:50]}...")
            
            # Move to after the authors section
            i = j
        else:
            i += 1
    
    print(f"Found {len(papers_data)} paper entries.")
    return papers_data

if __name__ == "__main__":
    cvpr_2024_url = "https://openaccess.thecvf.com/CVPR2024?day=all"
    extracted_data = simplify_cvpr_scrape(cvpr_2024_url)

    if extracted_data:
        # Convert to a pandas DataFrame for easy export
        df = pd.DataFrame(extracted_data)

        # --- Export to CSV ---
        csv_filename = 'cvpr_2024_papers_simplified.csv'
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"\nData successfully saved to {csv_filename}")

        # --- Export to JSON ---
        json_filename = 'cvpr_2024_papers_simplified.json'
        df.to_json(json_filename, orient='records', indent=4, force_ascii=False)
        print(f"Data successfully saved to {json_filename}")

        print("\nHere's a preview of the first 5 entries:")
        print(df.head().to_string())
    else:
        print("\nNo data was extracted. Please check the URL and the website's current HTML structure.")
