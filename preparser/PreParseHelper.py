
import requests
from bs4 import BeautifulSoup
from typing import Callable,Literal,Any 
from urllib.parse import urlparse
from .TaskHelper import Tasker
from .DynamicHelper import Dynamicer,Moniter_Notes
# typing 
Json_Data = dict[str, Any]

#  Object
class PreParser():
    """
        A slight PreParser oject to handle the parsing task with threading pools or other methods from webpage urls or api urls.

        Parameters:
            url_list(list):The list of URLs to parse from. Default is an empty list.
            request_call_back_func (Callable[[str,BeautifulSoup | Dict[str, Any]], Any] | None):A callback function according to the parser_mode to handle the `BeautifulSoup` object or request `json` Object. and if you want to show your business process failed, you can return `None`, otherwise please return a `not None` Object.  
            parser_mode(Literal['html','api']): the pre-parsing datas mode,default is html, 
                                                `html`: parse the content from static html, and return an `BeautifulSoup` Object. 
                                                `api`: parse the datas from an api, and return the `json` Object.
                                                `html_dynamic`: parse  from  the whole webpage html content and return an `BeautifulSoup` Object, even the content that generated by the dynamic js code.
            cached_data(bool): weather cache the parsed datas, defalt is False.
            start_threading(bool): Whether to use threading pool for parsing the data. Default is False.
            threading_mode(Literal['map','single']): to run the task mode,default is `single`. 
                                                `map`: use the `map` func of the theading pool to distribute tasks.
                                                `single`: use the `submit` func to distribute the task one by one into the theading pool.
            stop_when_task_failed(bool): wheather need stop when you failed to get request from a Url,default is True.
            threading_numbers(int): The maximum number of threads in the threading pool. Default is 3.
            checked_same_site(bool): wheather need add more headers info to pretend requesting in a same site to parse datas, default is True,to resolve the CORS Block.
            html_dynamic_scope(list[str,Literal['attached', 'detached', 'hidden', 'visible']] | None): point and get the specied scope dom of the whole page html, default is None, which stands for the whole page dom.
                                                                                                        else if this value was set, the parameter should be a list(2) Object.
                                                                                                        1. the first value is a tag <a href="https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelector"> selecter</a>.
                                                                                                        for example, 'div#main' mean a div tag with 'id=main', 'div.test' will get the the first matched div tag with 'class = test'. 
                                                                                                        but don't make the selecter too complex or matched the mutiple parent dom, otherwise you can't get their inner_html() correctly or time out.
                                                                                                        and finally you can get the BeautifulSoup object of the inner_html from this selecter selected tag in the `request_call_back_func`.
                                                                                                        2. the secound value should be one of the values below:
                                                                                                          `attached`: wait for element to be present in DOM
                                                                                                          `detached`: wait for element to not be present in DOM.
                                                                                                          `hidden`: wait for element to have non-empty bounding box and no `visibility:hidden`. Note that element,without any content or with `display:none` has an empty bounding box and is not considered visible.
                                                                                                          `visible`: wait for element to be either detached from DOM, or have an empty bounding box or `visibility:hidden`. This is opposite to the 'visible' option. 
            ssl_certi_verified(bool): wheather need verify the ssl certi when requesting datas from urls, default is True, which means will verify the ssl certi to make the requesting safe.
        
        Attributes:
            url_list(list):The list of URLs to parse from.
            request_call_back_func(Callable[[str,BeautifulSoup | Dict[str, Any]], bool] | None): The callback function to process the BeautifulSoup Or Json object.
            parser_mode(Literal['html','api']): the preparse  datas mode.
            cached_data(bool): weather to cache the parse datas.
            start_threading(bool): Whether to use threading pool.
            threading_mode(Literal['map','single']): to run the task mode.
            stop_when_task_failed(bool): wheather need stop when you failed to get request from a Url.
            threading_numbers(int): The maximum number of threads.
            checked_same_site(bool): wheather need add more headers info to pretend requesting in a same site to parse datas, to resolve the CORS Block.
            html_dynamic_scope(list[str,Literal['attached', 'detached', 'hidden', 'visible']] | None): to get and load specified scope html nodes resouce.
            ssl_certi_verified(bool): wheather need verify the ssl certi when requesting datas from urls. 
    """
    def __init__(self, 
                 url_list: list[str] = [],
                 request_call_back_func: Callable[[str,BeautifulSoup | Json_Data], Any ] | None = None,
                 parser_mode:Literal['html','api','html_dynamic'] = 'html',
                 cached_data:bool = False,
                 start_threading: bool = False,
                 threading_mode:Literal['map','single'] = 'single',
                 stop_when_task_failed:bool = True,
                 threading_numbers: int = 3,
                 checked_same_site:bool = True,
                 html_dynamic_scope:Moniter_Notes= None,  # await loaded contions
                 ssl_certi_verified:bool = True
                ) -> None:
        self.to_parse_urls = url_list
        self.start_threading = start_threading
        self.threading_numbers = threading_numbers
        self.cached_data = cached_data
        self.cached_request_datas = {}
        self.request_call_back_func = request_call_back_func
        self.parser_mode:Literal['html','api','html_dynamic'] = parser_mode
        self.checked_same_site:bool = checked_same_site
        self.stop_when_task_failed = stop_when_task_failed
        self.threading_mode:Literal['map','single'] = threading_mode
        self.tasker = Tasker(self.threading_mode,self._pre_parse_datas,self.to_parse_urls,self.threading_numbers,self.cached_data,self.stop_when_task_failed)
        self._request_ssl_verified = ssl_certi_verified
        self.dynamicer= Dynamicer(ignore_https_errors = not ssl_certi_verified)
        self._stop_running = False
        self._async_bundle_index = self._get_aync_bundle_index()
        self._html_dynamic_scope = html_dynamic_scope

    
    def _get_aync_bundle_index(self) -> int:
        if self.parser_mode == 'html_dynamic':
            avalibe_bundle_index = self.dynamicer._check_dynamic_async_env()
            if avalibe_bundle_index == -1:
                self._async_bundle_index = -1
                self.stop_parse()
            else:
                return avalibe_bundle_index
        else:
            return -1
    
    def _get_synamic_soup(self,url:str) -> BeautifulSoup | None:
        if self._async_bundle_index >= 0:
            html = self.dynamicer._get_dynamic_html(url,self._html_dynamic_scope)
            if html:
               return BeautifulSoup(html, 'html.parser')
        return None
        

    def _pre_parse_datas(self, url: str) -> BeautifulSoup | Json_Data | Any:
        print(f'Start the parse task from the url:{url} !!!')
        if url is None or url.__len__() == 0:
            print(f'warning: invalid parse url: {url} !!!!')
            return None
        try:
            to_pass_next_data = None
            headers = self._create_request_headers(url)
            if self.parser_mode == 'html_dynamic':
                to_pass_next_data = self._get_synamic_soup(url)
            else:
                if self.parser_mode not in ['html','api']:
                    print(f'invalid parser_mode : {self.parser_mode}')
                    return None
                else:
                    respos = requests.get(url, headers=headers,verify=self._request_ssl_verified)
                if respos.status_code == 200:
                    if self.parser_mode == 'html':
                        to_pass_next_data = BeautifulSoup(respos.text, 'html.parser')
                    else:  # self.parser_mode == 'api'
                        to_pass_next_data = respos.json() 
                else:
                    print(f"something unknow happend when parsing the datas with the url:({url}), response_status_code:{respos.status_code},response:{respos}!!!")
                    return None 
            if (self.request_call_back_func is not None ) and (to_pass_next_data is not None):
                handled_result = self.request_call_back_func(url,to_pass_next_data)
                if handled_result is None:
                    # return to_pass_next_data
                    print(f"warning: parsing by function({self.request_call_back_func})with url({url}) get None Result !!!")
                return handled_result
            else:
                return to_pass_next_data
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




                


