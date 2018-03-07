import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

class HTMLTable():
    """A scraped HTML table."""
    
    def __init__(self, soup):
        self._soup = soup
    
    @property
    def soup(self):
        return self._soup
    
    @property
    def shape(self):
        n_rows = 0
        n_cols = 0
        for row in self.rows:
            row_cols = HTMLTable._cols_in(row)
            if row_cols > 0:
                n_rows += 1
                # Find the max number of columns in any row
                n_cols = max(n_cols, row_cols)
        return n_rows, n_cols

    @property
    def rows(self):
        """All top-level rows of HTML table."""
        results = list()
        children = [
            child for child in self.soup.children if child.name in [
                'tr', 'thead', 'tbody',
            ]
        ]
        for child in children:
            if child.name in ['thead', 'tbody',]:
                results.extend([row for row in child.find_all('tr')])
            else:
                results.append(child)
        return results
        
    def unspan(self, soup=False, repeat_span=False):
        """Text or HTML from table, removing rowspan/colspan structure."""
        return self._unspan_cells(soup=soup, repeat_span=repeat_span)

    def to_df(self, repeat_span=False):
        """DataFrame from HTML table, removing rowspan/colspan structure."""
        cells = self._unspan_cells(soup=False, repeat_span=repeat_span)
        n_rows, n_cols = cells.shape
        return pd.DataFrame(
            index=range(n_rows),
            columns=range(n_cols),
            data=cells,
        )

    def _unspan_cells(self, soup=False, repeat_span=False):
        # Table dimension is rows x max number of columns in any row
        n_rows, n_cols = self.shape
        # Start with empty array of generic objects
        cells = np.empty((n_rows, n_cols), dtype=object)
        # Loop through rows
        rows_left_in_span = dict()
        for i, row in enumerate(self.rows):
            cols = row.find_all(['td', 'th'])
            col_index = 0 # where we are in the actual columns of this particular row
            cols_left_in_span = 0 # where we are within a colspan in this row
            for j in range(n_cols):
                # j is which column in the (initially empty) table we are currently at
                if j in rows_left_in_span:
                    # this table column is part of a rowspan
                    if repeat_span:
                        cells[i, j] = cells[i - 1, j] # get value from one row up
                    else:
                        cells[i, j] = np.nan # if don't want repeated values, just put NaN
                    # Reduce count of rows left in span; if done with this span, delete the span reference
                    rows_left_in_span[j] -= 1
                    if rows_left_in_span[j] == 0:
                        del rows_left_in_span[j]
                elif cols_left_in_span > 0:
                    # this table column is part of a colspan
                    if repeat_span:
                        cells[i, j] = cells[i, j - 1] # get value from one column to the left
                    else:
                        cells[i, j] = np.nan # if don't want repeated values, just put NaN
                    # Redue count of columns left in span
                    cols_left_in_span -= 1
                else:
                    # Don't know yet if this cell is stand-alone, or beginning of a new rowspan/colspan
                    # Get the actual cell from the soup object; remember col_index != j
                    col = cols[col_index]
                    # if we want raw soup, save that otherwise just get the cleaned cell text
                    if soup:
                        cells[i, j] = col
                    else:
                        cells[i, j] = HTMLTable._clean(col)
                    col_index += 1
                    # Check if this is beginning of a new colspan
                    col_span = int(col['colspan']) if col.has_attr('colspan') else 0
                    if col_span > 0:
                        # Yes, so keep track of how many other table columns to use in span
                        cols_left_in_span = col_span - 1
                    # Check if this is the beginning of a new rowspan
                    row_span = int(col['rowspan']) if col.has_attr('rowspan') else 0
                    if row_span > 0:
                        # Yes, so keep track of how many other table rows to use in span
                        rows_left_in_span[j] = row_span - 1
        return cells
    
    @staticmethod
    def _clean(cell):
        # credit Andy Roche blog post for ideas on how to clean cells
        #   https://roche.io/2016/05/scrape-wikipedia-with-python
        # remove any references
        refs = cell.find_all('sup', {'class': 'reference'})
        if refs:
            for ref in refs:
                ref.extract()
        sortkeys = cell.find_all('span', {'class': 'sortkey'})
        if sortkeys:
            for ref in sortkeys:
                ref.extract()
        text_items = cell.find_all(text=True)
        wo_footnotes = [text for text in text_items if text[0] != '[']
        return ''.join(wo_footnotes).replace('\xa0', ' ').replace('\n', ' ').strip()
                
    
    @staticmethod
    def _cols_in(row):
        tags = [child for child in row.children if child.name]
        cols = 0
        for tag in tags:
            cols += int(tag['colspan']) if tag.has_attr('colspan') else 1
        return cols

class HTMLTables():
    """One or more scraped HTML tables from a URL."""

    def __init__(self, url, headers=None, table_class=None):
        self._url = url
        self._response = requests.get(
            url,
            allow_redirects=False,
            headers=headers,
            timeout=15,
        )
        self._response.raise_for_status()
        soup = BeautifulSoup(self._response.content, 'html.parser')
        tables = soup.find_all('table', table_class)
        self._tables = [HTMLTable(table) for table in tables]

    def __getitem__(self, k):
        return self._tables[k]

    def __len__(self):
        return len(self._tables)

    def __iter__(self):
        return iter(self._tables)

