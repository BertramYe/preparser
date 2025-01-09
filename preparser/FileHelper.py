from typing import Literal,Any
from os import makedirs
from os.path import dirname
from json import dump


FileType = Literal['txt','json']

class Filer():
    """
        a simple file object to help process file result
        
        Parameters:
            file_type ( Literal['txt','json'] ): to save or read files type, so far mainly support `txt` and `json`, but future will add more
    """
    def __init__(self,file_type:FileType='txt') -> None:
        self.file_type:FileType = file_type

    def write_data_into_file(self,new_file_name:str,datas:list[Any],ensure_json_ascii:bool=False):
        """
            a function to help save the result from the object preparser result into txt or json file

            Parameters:
                new_file_name ( str ): to save the result filename , if file existed, will empty the file content and rewrite `datas` into it, else will auto help create a new file.
                datas: (list[Any]) : to save the files datas, which should be a `list` Obeject
                ensure_json_ascii (bool) : for the json file content writing, as from the object `PreParser` result, which no need ensure_ascii , otherwise may result the content ascii can't be decoded, just keep default False is ok.
        """
        
        file_name = f'{new_file_name}.{self.file_type}'
        # 获取文件夹路径
        dir_path = dirname(file_name)

        # 确保文件夹存在，若不存在则创建
        makedirs(dir_path, exist_ok=True)
        try:
            print(f'begin to save datas into file: {file_name} !')
            if self.file_type == 'txt' or self.file_type == 'json':
                with open(file_name,'w',encoding="utf-8")  as file:
                    if self.file_type == 'json':
                        dump(datas, file, indent=4,ensure_ascii=ensure_json_ascii)
                    else:
                        file.writelines(datas)
            else:
                print(f'failed to save datas into file: {file_name}, as current file type not support, file_type: {self.file_type}')
            print(f'successd to save datas into file: {file_name} !')
        except Exception as err:
            print(f'failed to save datas into file: {file_name}, error: {err}')