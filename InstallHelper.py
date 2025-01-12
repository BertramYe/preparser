from os import path,getenv,listdir
from setuptools import Command
from subprocess import check_call
from setuptools.command.install import install
from typing import Literal,Optional
import sys
from platform import system


class BrowserCoreInstaller(Command):
    """
        install the Browser Core
    """
    # description = "Install the specified preparser browser core (chromium, firefox, or webkit)"
    # define command
    # user_options = [
    #     ('browser=', None, 'Specify the preparser browser to install: chromium, firefox, or webkit')
    # ]

    def initialize_options(self):
        self.browser_list = ['chromium','firefox','webkit']
        self.installed_browsers = []
        self.need_recheck_browsers = []
        self.browser_cache_path = None
        self.preched_installed_browsers = self._get_pre_installed_browsers()

    def _get_pre_installed_browsers(self) -> list[str]:
        preched_installed_browsers = []
        os_type = system()
        browser_cache_path = path.expanduser("~/.cache/ms-playwright/") 
        if os_type == "Windows":
            browser_cache_path = path.join(getenv("APPDATA"), "Local", "ms-playwright")  
        if path.exists(browser_cache_path):
            self.browser_cache_path = browser_cache_path
            folder_name_list = listdir(self.browser_cache_path)
            for folder_name in folder_name_list:
                abs_path = path.join(self.browser_cache_path, folder_name)
                if path.isdir(abs_path):
                    for key in self.browser_list:
                        if folder_name.startswith(key):
                            preched_installed_browsers.append(key)
        else:
            preched_installed_browsers = []
        return preched_installed_browsers
    

    def precheck_installed_browsers(self):
        self.installed_browsers = []
        self.need_recheck_browsers = []
        # get the path
        for browser_name in self.browser_list:
            if browser_name in self.preched_installed_browsers:
                print(f'find that browser {browser_name} of preparser installed !')
                operate_choice = self.check_choice_avalible(f" do you want to reinstall,remove or keep it ? (1 : reinstall, 2: remove , 3: keep.): ",['1','2','3'])
                if operate_choice == "3":
                    self.installed_browsers.append(browser_name)
                else:  # "1" or "2"
                    self.operate_browser("uninstall",browser_name)
                    if operate_choice == '1':
                        self.operate_browser("install",browser_name)
                        self.installed_browsers.append(browser_name)
            else:
                self.need_recheck_browsers.append(browser_name)
        

    def init_install_browser(self):
        # if not , just let the user to choose
        print("please choose a preparser browser  to install: ")
        print("[1] chromium, [2] firefox, [3] webkit.")
        choice = self.check_choice_avalible(f'please input a number to choose a browser (1/2/3):',['1','2','3'])
        browser = self.browser_list[int(choice)-1]
        self.operate_browser("install",browser)
        return browser
    
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

    def finalize_options(self):
        if self.installed_browsers.__len__() == 0:
            print("warning: to use preparser, you need at least one of the preparser browsers installed .")
            install_browser = self.init_install_browser()
            self.installed_browsers.append(install_browser)


    def run(self):
        print("checking weather there were preparser browsers' core installed .....")
        self.precheck_installed_browsers()
        recheck_browsers_number  = len(self.need_recheck_browsers)
        total_browsers_number = len(self.browser_list)
        if recheck_browsers_number > 0:
            if recheck_browsers_number < total_browsers_number:
                print(f'there were browsers of preparser not installed {",".join(self.need_recheck_browsers)}.')
                print(f"warning: added more or not won't effect your next process, as you have installed {",".join(self.installed_browsers)} ")
                choice = self.check_choice_avalible('do you still want to add them ? (yes/no) : ',['yes','no'])
                if choice == 'yes':
                    for browser in self.need_recheck_browsers:
                        to_install_choice = self.check_choice_avalible(f'do you want to install {browser} of preparser ? (yes/no) : ',['yes','no'])
                        if to_install_choice == 'yes':
                            self.operate_browser("install",browser)
                            self.installed_browsers.append(install_browser)
            else: # no browser installed 
                install_browser = self.init_install_browser()
                self.installed_browsers.append(install_browser)

        
class PreInstaller(install):
    def run(self):
        print('Prechecking the environment status, before install preparser!!!')
        if 'bdist_wheel' in sys.argv or 'build' in sys.argv:
            # Avoid running the browser installer during the build phase
            print("Skipping browser core installation during build.")
        else:
            # precheck the environment status before install
            print('Prechecking the environment status, before install preparser!!!')
            # Execute playwright install command
            BrowserCoreInstaller(self.distribution).run()
            print("All prechecks finished, begin installing preparser...")
        # excute the default running
        self.run(self)
                
        

