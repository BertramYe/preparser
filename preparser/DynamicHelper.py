
import sys
from os import path
from subprocess import check_call
from typing import Literal,Optional
from playwright.sync_api import sync_playwright 

class Dynamicer():
    """
        install the Browser Core
    """
    def __init__(self) -> None:
        self.browser_list = ['chromium','firefox','webkit']
        self._async_index = -1
        
    def _check_dynamic_async_env(self) -> int:
        installed_browser_index = -1
        try:
            with sync_playwright() as p:
                browser_Bundle_List = [
                        p.chromium,
                        p.firefox,
                        p.webkit
                ]
                for i,browser_budle in enumerate(browser_Bundle_List):
                    if path.exists(browser_budle.executable_path):
                        installed_browser_index = i
                        break
            if installed_browser_index == -1:
                installed_browser_index = self.init_install_browser()
            # else:
                # because so far is in the use checking, so no need add the re-install logical
                # fro the precheck and install will added into the setup logical in the future
        except Exception as error:
            print(f"error: when check the preparser browser bundle, error:{error} !!!")
            print(f'please try again, if failed again, please reinstall preparser !!!')
        finally:
            self._async_index = installed_browser_index
            return installed_browser_index
    
    def _get_dynamic_html(self,url:str) -> str | None:
        try:
            if 0 <= self._async_index < 3:
                with sync_playwright() as p:
                    if self._async_index == 0:
                        browser = p.chromium.launch(headless=True)
                    elif self._async_index == 1:
                        browser = p.firefox.launch(headless=True)
                    else:
                        browser = p.webkit.launch(headless=True)
                    page = browser.new_page()
                    page.goto(url)
                    html = page.content()
                    browser.close()
                    return html
            else:
                return None
        except Exception as err:
            print(f'error when doing dynamic html parse , error: {err} !')
            return None

    def init_install_browser(self):
        # if not , just let the user to choose
        print("please choose a preparser browser  to install: ")
        print("[1] chromium, [2] firefox, [3] webkit.")
        choice = self.check_choice_avalible(f'please input a number to choose a browser (1/2/3):',['1','2','3'])
        browser = self.browser_list[int(choice)-1]
        self.operate_browser("install",browser)
        return int(choice)-1         

    def operate_browser(self,command_type:Literal["install","uninstall"], browser_name:str):
        # install specified browser
        print(f"{command_type}ing preparser browser {browser_name} ...")
        check_call([sys.executable, "-m", "playwright", command_type, browser_name])    

    def check_choice_avalible(self, alert_message: str, valid_choices: list[str]) -> Optional[str]:
        while True:
            choice = input(alert_message)
            if choice in valid_choices:
                return choice
            else:
                print(f"Invalid choice, available choices: {','.join(valid_choices)}. Please try again.")
    
