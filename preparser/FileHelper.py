from typing import Literal,Any
from os import makedirs
from os.path import dirname,exists,abspath
from json import dump,load


FileType = Literal['txt','json']

class Filer():
    """
        a simple file object to help process file result
        
        Parameters:
            file_type ( Literal['txt','json'] ): to save or read files type, so far mainly support `txt` and `json`, but future will add more
    """
    def __init__(self,file_type:FileType='txt') -> None:
        self._available_file_types = ['txt','json']
        self._file_type:FileType = file_type
    
    def __filter_file_types(self,file_path_without_type:str) -> str | None:
        if self._file_type in self._available_file_types:
            return abspath(f'{file_path_without_type}.{self._file_type}')
        else:
            print(f'error: so fare , the type {self._file_type} is not supported by the preparser, only {','.join(self._available_file_types)} is avaliable')
            return None

    def write_data_into_file(self,new_file_name:str,datas:list[Any],ensure_json_ascii:bool=False):
        """
            a function to help save the result from the object preparser result into txt or json file

            Parameters:
                new_file_name ( str ): to save the result filename , if file existed, will empty the file content and rewrite `datas` into it, else will auto help create a new file.
                datas: (list[Any]) : to save the files datas, which should be a `list` Obeject
                ensure_json_ascii (bool) : for the json file content writing, as from the object `PreParser` result, which no need ensure_ascii , otherwise may result the content ascii can't be decoded, just keep default False is ok.
        """
        abs_file_path = self.__filter_file_types(new_file_name)
        if abs_file_path:
            # get file's dir path
            dir_path = dirname(abs_file_path)
            # make sure files existed
            makedirs(dir_path, exist_ok=True)
            try:
                print(f'begin to save datas into file: {abs_file_path} !')
                with open(abs_file_path,'w',encoding="utf-8")  as file:
                    if self._file_type == 'json':
                        dump(datas, file, indent=4,ensure_ascii=ensure_json_ascii)
                    else:
                        file.writelines(datas)
                print(f'successd to save datas into file: {abs_file_path} !')
            except Exception as err:
                print(f'failed to save datas into file: {abs_file_path}, error: {err}')
    
    def read_datas_from_file(self,file_name:str):
        """
            a function to help get the content from txt or json file

            Parameters:
                file_name ( str ): to read the result filename , it can include absolute or relative path of the files, but the filename can't include files type, 
                                   which already was defined when the `Filer` class was initial, otherwise, if you want specified the file type, 
                                   you can change the property `_file_type` after you initial the `Filer` class .
                                   for example,if you want read a `result.txt` file, file_name can't be `./test/result.txt`, but the `./test/result` is ok.
        """
        abs_file_path = self.__filter_file_types(file_name)
        if abs_file_path:
            try:
                if exists(abs_file_path):
                    with open(abs_file_path,'r',encoding="utf-8")  as file:
                        if self._file_type == 'json':
                            return load(file)
                        else:
                            return file.read()
                else:
                    print(f"read file {file_name} failed, error: we can't find out current file from the path: {abs_file_path}")
                    return None
            except Exception as error:
                print(f"read file {abs_file_path} failed, error: {error}")
                return None
        else:
            return None