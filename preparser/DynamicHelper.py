
import sys
from os import path
from subprocess import check_call
from typing import Literal,Optional
from playwright.sync_api import sync_playwright 


Moniter_Notes = list[str,Literal['attached', 'detached', 'hidden', 'visible']] | None

class Dynamicer():
    """
        install the Browser Core
    """
    def __init__(self,ignore_https_errors:bool=False) -> None:
        self.browser_list = ['chromium','firefox','webkit']
        self._async_index = -1
        self._ignore_https_errors = ignore_https_errors
        
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
    
    def _get_dynamic_html(self,url:str,moniter_scope:Moniter_Notes = None) -> str | None:
        try:
            if 0 <= self._async_index < 3:
                with sync_playwright() as p:
                    if self._async_index == 0:
                        browser = p.chromium.launch(headless=True)
                    elif self._async_index == 1:
                        browser = p.firefox.launch(headless=True)
                    else:
                        browser = p.webkit.launch(headless=True)
                
                    page = browser.new_page(ignore_https_errors=self._ignore_https_errors)
                    page.goto(url)
                    html = None
                    if moniter_scope is not None:
                        target_element = page.wait_for_selector(moniter_scope[0],state=moniter_scope[1])
                        if target_element:
                            target_element.scroll_into_view_if_needed()
                            html = target_element.as_element().inner_html()
                            # print(target_element.eval_on_selector_all('.row', 'elements => elements.map(el => el.outerHTML)'))
                        # stop all of rest pages resouce loading to faster the loading speed 
                        page.route("**/*",lambda route,request:route.abort())
                        # html = page.content()
                        # stop specified type of resource loading, here below is the ['image', 'script'] two kind of the resouce type
                        # page.route("**/*", lambda route, request: route.abort() if request.resource_type() in ['image', 'script'] else route.continue_())
                    else:
                        html = page.content()
                    page.close()
                    browser.close()
                    return html
            else:
                return None
        except Exception as err:
            print(f'error when parsing dynamic html , error: {err} !')
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
    
