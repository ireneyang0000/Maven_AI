import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
import time

def simplify_cvpr_scrape(url="https://openaccess.thecvf.com/CVPR2024?day=all"):
    """
    Scrapes paper titles, authors, abstract snippets, PDF links, and supplementary
    material links directly from the main CVPR 2024 page.
    """
    print(f"Fetching data from: {url}")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status() # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    papers_data = []

    # The CVF Open Access typically lists papers within <dl class="paper-details"> blocks.
    # Each <dl> contains <dt> (title) and <dd> (authors, abstract-snippet, links).
    paper_dl_entries = soup.find_all('dl', class_='paper-details')

    if not paper_dl_entries:
        print("Could not find any <dl class='paper-details'> entries. The website structure might have changed.")
        return []

    print(f"Found {len(paper_dl_entries)} paper entries.")

    for i, dl_entry in enumerate(paper_dl_entries):
        paper_info = {}

        # 1. Title and URL to Paper Page
        title_dt = dl_entry.find('dt', class_='paper-title')
        if title_dt:
            title_link = title_dt.find('a', href=True)
            paper_info['Title'] = title_link.get_text(strip=True) if title_link else title_dt.get_text(strip=True)
            paper_info['Paper Page URL'] = requests.compat.urljoin(url, title_link['href']) if title_link else None
        else:
            paper_info['Title'] = None
            paper_info['Paper Page URL'] = None

        # 2. Authors (usually in the dd immediately following the dt, or first dd)
        authors_dd = dl_entry.find('dd', class_='authors')
        if authors_dd:
            paper_info['Authors'] = authors_dd.get_text(strip=True)
        else:
            # Fallback: sometimes authors are in a general <dd> tag
            potential_authors_dd = dl_entry.find('dd')
            if potential_authors_dd and ';' in potential_authors_dd.get_text(): # Simple heuristic
                paper_info['Authors'] = potential_authors_dd.get_text(strip=True)
            else:
                paper_info['Authors'] = None

        # 3. Abstract Snippet (usually in a dd with class 'abstract-snippet' or similar)
        abstract_dd = dl_entry.find('dd', class_=re.compile(r'abstract|abstract-snippet'))
        if abstract_dd:
            paper_info['Abstract'] = abstract_dd.get_text(strip=True)
        else:
            paper_info['Abstract'] = None

        # 4. Links (PDF and Supplementary Material)
        # These are usually within a <dd class="links"> or just direct <a> tags within the <dl>
        
        pdf_link_tag = dl_entry.find('a', href=re.compile(r'\.pdf$', re.IGNORECASE))
        paper_info['PDF Link'] = requests.compat.urljoin(url, pdf_link_tag['href']) if pdf_link_tag else None

        # Find supplementary material link (common archive/video extensions, not a PDF)
        supp_link_tag = dl_entry.find('a', href=re.compile(r'\.(zip|gz|tgz|rar|mp4|mov|avi|gif)$', re.IGNORECASE))
        if supp_link_tag and '.pdf' not in supp_link_tag['href'].lower(): # Ensure it's not the PDF
            paper_info['Supplementary Material Link'] = requests.compat.urljoin(url, supp_link_tag['href'])
        else:
            paper_info['Supplementary Material Link'] = None
            
        papers_data.append(paper_info)

        # Optional: Print progress for long lists
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1} papers...")

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
        print(df.head().to_string()) # to_string() helps display full content in console
    else:
        print("\nNo data was extracted. Please check the URL and the website's current HTML structure.")
