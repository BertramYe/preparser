# Description

this is a sight Parser to help you pre_parser the datas from `specified website url or api`, it help you get ride of the duplicate coding to get the request from the `specified url and speed up the process with the threading pool` and you just need focused on the bussiness proceess coding after you get the specified  request response from the `specified webpage or api urls`

# Attention

as this slight pre_parser  was just based the module of the `requests` and `beautifulsoup4`, which mainly was used to parse the data from the `api` and page randered as `static html`, so it can't directly parsed datas that need waiting the whole website pages was loaded, but for this function , maybe I will added later in future.

```bash

python version >= 3.9 

```

# How to use

## install

```bash
$ pip install preparser
```



> Github Resouce ➡️ [Github Repos](https://github.com/BertramYe/preparser) 

> and also just feel free to fork and modify this codes. if you like current project, star ⭐ it please, uwu.

> PyPI: ➡️ [PyPI Publish](https://pypi.org/project/preparser/)  

## parameters

here below are some of the parameters you can use for initai the Object `PreParser` from the package `preparser`:


|        Parameters      | Type                | Description                                               |
| ---------------------  | -----------------   |--------------------------------------------------------   |
| url_list               | list                | The list of URLs to parse from. Default is an empty list. |
| request_call_back_func | Callable or None    | A callback function according to the parser_mode to handle the `BeautifulSoup` object or request `json` Object. and if you want to show your business process failed, you can return `None`, otherwise please return a `not None` Object.        |
|  parser_mode           | `'html'` or `'api'` | The pre-parsing datas mode,default is `'html'`.<br/>  `html`: use the bs4 to parse the datas, and return an `BeautifulSoup` Object. <br/> `api` :  use requests only and return an `json` object. <br/>  **and all of them you can get it when you set the `request_call_back_func`, otherwise get it via the object of `PreParer(....).cached_request_datas`    |
| cached_data | bool | weather cache the parsed datas, defalt is False. |
| start_threading | bool | Whether to use threading pool for parsing the data. Default is `False`.|
| threading_mode | `'map'` or `'single'` | to run the task mode, default is `single`. <br/>  `map`: use the `map` func of the theading pool to distribute tasks. <br/> `single`: use the `submit` func to distribute the task one by one into the theading pool. |
| stop_when_task_failed | bool | wheather need stop when you failed to get request from a Url,default is `True` |
| threading_numbers | int | The maximum number of threads in the threading pool. Default is `3`. |
| checked_same_site | bool |  wheather need add more headers info to pretend requesting in a same site to parse datas, default is `True`,to resolve the `CORS` Block. |


## example

```python

#  test.py
from preparser import PreParser,BeautifulSoup,Json_Data,Filer


def handle_preparser_result(url:str,preparser_object:BeautifulSoup | Json_Data) -> bool:
    # here you can just write the bussiness logical you want
    
    # attention：
    # preparser_object type depaned on the `parser_mode` in the `PreParser`:
    #               'api' : preparser_object is the type of a Json_Data
    #               'html' : preparser_object is the type of a BeautifulSoup 
    
    ........
    
    # for the finally return:
    # if you want to show current result is failed just Return a None, else just return any object which is not None.
    return preparser_object


if __name__ == "__main__":
    
    #  start the parser
    url_list = [
        'https://example.com/api/1',
        'https://example.com/api/2',
        .....
    ]
  
    parser = PreParser(
        url_list=url_list,
        request_call_back_func=handle_preparser_result,
        parser_mode='api',    # this mode depands on you set, you can use the "api" or "html"
        start_threading=True,
        threading_mode='single',
        cached_data=True,
        stop_when_task_failed=False,
        threading_numbers=3,
        checked_same_site=True
    )
    
    #  start parse
    parser.start_parse()

    # when all task finished, you can get the all task result result like below:
    all_results = parser.cached_request_datas
    
    # if you want to terminal, just execute the function here below
    # parser.stop_parse()

    # also you can use the Filer to save the final result above
    # and also find the datas in the `result/test.json` 
    filer = Filer('json')
    filer.write_data_into_file('result/test',[all_result])

```


# Get Help

Get help ➡️ [Github issue](https://github.com/BertramYe/preparser/issues)

