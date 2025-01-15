from bs4 import BeautifulSoup
from re import Pattern,search
# from .TaskHelper import Tasker  # ready for the futures functions

class Tooler():
    """
       an Object to help manage some of the additional tools of preparser
    """
    def __init__(self,start_threading:bool = False,threading_numbers:int=3) -> None:
        #  here below defines the parameters for the futures optimise
        self.start_threading = start_threading
        self.threading_numbers = threading_numbers
        

    
    def decode_script_content_into_html(self,script_conetnt:str,script_pattern: str | Pattern[str] | None = None,transfer_soup:bool=False) -> tuple[str,BeautifulSoup | None] | None:
        """
            help decode the string label content that contains the encode string like `\\u003` and so on into the html content string

            Parameters:
                script_conetnt (str): the content from the script tag that you can get from `innerHtml` or `innerText`.
                script_pattern (str | Pattern[str] | None): to match the Pattern or string, default is None, it means that just decode the whole string.
                transfer_soup (bool): wheather help transfer the decode string into the BeautifulSoup Object .

        """
        try:
            clear_conetnt = script_conetnt.strip(' ')
            if clear_conetnt.__len__() > 0:
                if script_pattern:
                    match = search(script_pattern, clear_conetnt)
                    if match:
                        clear_conetnt = match.group(1)
                decoded_html = clear_conetnt.encode('utf-8').decode('unicode_escape')
                decode_soup = None
                if transfer_soup:
                    decode_soup = BeautifulSoup(decoded_html, 'html.parser')
                return [decoded_html,decode_soup]
            else:
                return None
        except Exception as error:
            print(f"error: when decoding the encode html content, error: {error} !!!!")
            return None

    def find_all_betweem_same_level_nodes(self,start_node:BeautifulSoup | None =None,
                           end_node:BeautifulSoup | None =None,
                           include_start_node:bool=False,
                           include_end_node:bool=False,
                           parent_node:BeautifulSoup | None = None
                           ) -> BeautifulSoup | None:
        """   
            this function is help finding out the website elements nodes between specified two same level elements notes and finally return a new BeautifulSoup Object
            
            Parameters:
                start_node (BeautifulSoup | None): The start elements nodes, defaut is None, which means from the target first one element to start get the element node
                end_node (BeautifulSoup | None):  The end elements nodes, defaut is None, which means from the last element to start get the element node
                include_start_node (bool): when get the element nodes, weather include the start node, default is False.
                include_end_node (bool): when get the element nodes, weather include the end node, default is False.
                parent_node (BeautifulSoup | None): the parent element node which contained the start_node and end_node, 
                                                    if you set it , we just find the node in current nodes' children element, 
                                                    also default it can be None,which will be the parent node of the start_node or end_node.
        """
        
        
        if (not start_node)  and (not end_node):
            print("error: start_node and end_node are both None !!!")
            return None
        valid_numbers = 0
        parent = parent_node if parent_node else (start_node.parent if start_node else end_node.parent)
        parent_chidren_list = list(parent.children)
        if start_node:
            start_index = parent.index(start_node) + 1
        else:
            start_index = 1
        if end_node:
            end_index = parent.index(end_node)
        else:
            end_index = parent_chidren_list.__len__()
        if include_start_node:
            valid_numbers += 1
            start_index -= 1  
        if include_end_node:
            valid_numbers += 1
            end_index += 1
        between_nodes_list = parent_chidren_list[start_index:end_index]
        if len(between_nodes_list) == valid_numbers:
            print('no sibling nodes between the start_node and end_node !!!')
            return None
        else:
            html_str = ''.join(str(node) for node in between_nodes_list)
            return BeautifulSoup(html_str, 'html.parser')


    def get_per_table_data(self,table_soup:BeautifulSoup) -> list[list[str]]:
        """
            get the table datas from the standard element of table, which has 1 row head at most.
        
        """
        final_tables_row = []
        # thead
        thead = table_soup.find('thead')
        if thead:
            thead_th:list[BeautifulSoup] = thead.find('tr').find_all('th')  # default the table only one title tr of thead
            th_datas = []
            for th in thead_th:
                # th_tx = repr(th.get_text(strip=True)).strip("'")
                th_tx = th.get_text(strip=True)   # strip=True: get ride of the emply space from start and end
                th_datas.append(th_tx)
            final_tables_row.append(th_datas)       
        # tbody
        tbody = table_soup.find('tbody')
        if tbody:
            tbody_tr:list[BeautifulSoup] = tbody.find_all('tr')
            for tr in tbody_tr:
                tr_datas = []
                tds:list[BeautifulSoup] = tr.find_all('td')
                for td in tds:
                    # td_txt = repr(td.get_text(strip=True)).strip("'")
                    td_txt = td.get_text(strip=True)    # strip=True: get ride of the emply space from start and end
                    tr_datas.append(td_txt)
                final_tables_row.append(tr_datas)
        return final_tables_row
    