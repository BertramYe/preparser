
import requests
from bs4 import BeautifulSoup
from typing import Callable,Literal,Any 
from urllib.parse import urlparse
from .TaskHelper import Tasker

# typing 
Json_Data = dict[str, Any]

#  Object
class PreParser():
    """
        A slight PreParser oject to handle the parsing task with threading pools or other methods from webpage urls or api urls.

        Parameters:
            url_list (list): The list of URLs to parse from. Default is an empty list.
            request_call_back_func (Callable[[str,BeautifulSoup | Dict[str, Any]], Any] | None): A callback function according to the parser_mode to handle the `BeautifulSoup` object or request `json` Object. and if you want to show your business process failed, you can return `None`, otherwise please return a `not None` Object.  
            parser_mode (Literal['html','api']): the pre-parsing datas mode,default is html, 
                                                `html`: use the bs4 to parse the datas, and return an BeautifulSoup Object. 
                                                `api`: use request only and return an json object.
            cached_data (bool): weather cache the parsed datas, defalt is False.
            start_threading (bool): Whether to use threading pool for parsing the data. Default is False.
            threading_mode (Literal['map','single']): to run the task mode,default is `single` 
                                                `map`: use the `map` func of the theading pool to distribute tasks.
                                                `single`: use the `submit` func to distribute the task one by one into the theading pool.
            stop_when_task_failed (bool) : wheather need stop when you failed to get request from a Url,default is True
            threading_numbers (int): The maximum number of threads in the threading pool. Default is 3.
            checked_same_site (bool): wheather need add more headers info to pretend requesting in a same site to parse datas, default is True,to resolve the CORS Block.
        Attributes:
            url_list (list): The list of URLs to parse from.
            request_call_back_func (Callable[[str,BeautifulSoup | Dict[str, Any]], bool] | None): The callback function to process the BeautifulSoup Or Json object.
            parser_mode (Literal['html','api']): the preparse  datas mode.
            cached_data (bool): weather to cache the parse datas.
            start_threading (bool): Whether to use threading pool.
            threading_mode (Literal['map','single']): to run the task mode.
            stop_when_task_failed (bool) : wheather need stop when you failed to get request from a Url.
            threading_numbers (int): The maximum number of threads.
            checked_same_site (bool): wheather need add more headers info to pretend requesting in a same site to parse datas, to resolve the CORS Block.
    """
    def __init__(self, 
                 url_list: list[str] = [],
                 request_call_back_func: Callable[[str,BeautifulSoup | Json_Data], Any ] | None = None,
                 parser_mode:Literal['html','api'] = 'html',
                 cached_data:bool = False,
                 start_threading: bool = False,
                 threading_mode:Literal['map','single'] = 'single',
                 stop_when_task_failed:bool = True,
                 threading_numbers: int = 3,
                 checked_same_site:bool = True
                ) -> None:
        self.to_parse_urls = url_list
        self.start_threading = start_threading
        self.threading_numbers = threading_numbers
        self.cached_data = cached_data
        self.cached_request_datas = {}
        self.request_call_back_func = request_call_back_func
        self.parser_mode:Literal['html','api'] = parser_mode
        self.checked_same_site:bool = checked_same_site
        self.stop_when_task_failed = stop_when_task_failed
        self.threading_mode:Literal['map','single'] = threading_mode
        self.tasker = Tasker(self.threading_mode,self._pre_parse_datas,self.to_parse_urls,self.threading_numbers,self.cached_data,self.stop_when_task_failed)
        self._stop_running = False

    def _pre_parse_datas(self, url: str) -> BeautifulSoup | Json_Data | Any:
        print(f'Start the parse task from the url:{url} !!!')
        if url is None or url.__len__() == 0:
            print(f'warning: invalid parse url: {url} !!!!')
            return None
        try:
            headers = self._create_request_headers(url)
            respos = requests.get(url, headers=headers)
            if respos.status_code == 200:
                to_pass_next_data = None
                if self.parser_mode == 'html':
                    to_pass_next_data = BeautifulSoup(respos.text, 'html.parser')
                elif self.parser_mode == 'api':
                    to_pass_next_data = respos.json()
                else:
                    print(f'invalid parser_mode : {self.parser_mode}')
                    return None
                if self.request_call_back_func and to_pass_next_data != None:
                    handled_result = self.request_call_back_func(url,to_pass_next_data)
                    if handled_result is None:
                        # return to_pass_next_data
                        print(f"warning: parsing by function({self.request_call_back_func})with url({url}) get None Result !!!")
                    #     return None
                    # else:
                    return handled_result
                else:
                    return to_pass_next_data
            else:
                print(f"something unknow happend when parsing the datas with the url:({url}), response_status_code:{respos.status_code},response:{respos}!!!")
                return None            
        except Exception as err:
            print(
                f'there were an error when parsing from url: {url}, error: {err} !!!')
            return None
        finally:
            print(f'end the parse task from the url:{url} !!!')

    def start_parse(self)-> Json_Data:
        print('start  parse data task !!!')
        self._stop_running = False
        self.cached_request_datas = {}
        if self.to_parse_urls.__len__() == 0:
            print(f"to parse urls can't be empty !!!")
            return self.cached_request_datas
        else:
            if self.start_threading:
                self.tasker.start_task()
                self.cached_request_datas = self.tasker.task_result_dict
                self._stop_running = True
            else:
                for url in self.to_parse_urls:
                    prepar_result = self._pre_parse_datas(url)
                    if self.cached_data:
                        self.cached_request_datas[url] = prepar_result
                    if (not prepar_result) and self.stop_when_task_failed:
                        print(f'parsing task terminated as the get None data from url ({url})')
                        break
                    if self._stop_running:
                        break
        print('ended parse data task !!!')
        return self.cached_request_datas

    def stop_parse(self):
        """
          stop current parse process 
        """
        self.cached_request_datas = self.tasker.task_result_dict
        self._stop_running = True
        if self.start_threading:
            self.tasker.terminal_task()
            
    def _create_request_headers(self,url:str) -> dict[str,str]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",  # recieved data types
            "Accept-Language": "en-US,en;q=0.9",   # recied language type, this is option
            "Connection": "keep-alive", 
        }
        if self.checked_same_site:
            parse_url = urlparse(url)
            clear_hosts = f"{parse_url.scheme}://{parse_url.hostname}:{parse_url.port}" if parse_url.port else f"{parse_url.scheme}://{parse_url.hostname}"
            clear_url = f"{clear_hosts}{parse_url.path}"
            # use when cheched same site
            headers = {
                **headers,
                "Origin": clear_hosts,  # request domain
                "Referer": clear_url,  # request url, no need query info
                "Sec-Fetch-Site": "same-origin",  # same domain, hide the request action
                "Sec-Fetch-Mode": "cors",  # cors , resoved No 'Access-Control-Allow-Origin' header 
                "Sec-Fetch-Dest": "empty",  # target file types, it can be the  html, image and so on, details can reference : https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Sec-Fetch-Dest
            }
        return headers


def find_all_betweem_same_level_nodes(start_node:BeautifulSoup | None =None,
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


def get_per_table_data(table_soup:BeautifulSoup) -> list[list[str]]:
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

                


