import os
import time
from selenium import webdriver

import config


class WebDriver:
    def __init__(self, browser="firefox"):
        if browser == "firefox":
            self.driver = self.init_firefox()
        elif browser == "chrome":
            self.driver = self.init_chrome()

    def init_firefox(self):
        self.profile = webdriver.FirefoxOptions()
        self.profile.set_preference(
            "services.sync.prefs.sync.browser.download.manager.showWhenStarting", False)
        self.profile.set_preference("print.always_print_silent", True)
        self.profile.set_preference("print.show_print_progress", False)
        self.profile.set_preference(
            "browser.download.show_plugins_in_list", False)
        self.profile.set_preference("browser.download.folderList", 2)
        self.profile.set_preference(
            "browser.download.dir",
            config.DOWNLOAD_PATH)
        self.profile.set_preference(
            "browser.download.manager.showWhenStarting", False)
        self.profile.set_preference("browser.aboutConfig.showWarning", False)
        self.profile.set_preference("print.print_headerright", "")
        self.profile.set_preference("print.print_headercenter", "")
        self.profile.set_preference("print.print_headerleft", "")
        self.profile.set_preference("print.print_footerright", "")
        self.profile.set_preference("print.print_footercenter", "")
        self.profile.set_preference("print.print_footerleft", "")
        self.profile.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "application/pdf;text/html")
        driver = webdriver.Firefox(options=self.profile)
        driver.get("about:config")
        time.sleep(1)

        script = """
        var prefs = Components.classes["@mozilla.org/preferences-service;1"].getService(Components.interfaces.nsIPrefBranch);
        prefs.setBoolPref("print.always_print_silent", true);
        prefs.setCharPref("print_printer", "Print to File");
        prefs.setBoolPref("print.printer_Print_to_File.print_to_file", true);
        prefs.setBoolPref(
    "print.printer_Print_to_File.show_print_progress", true);
        """
        driver.execute_script(script)

        return driver

    def init_chrome(self):
        return self.init_firefox()

    def download_pdf(self, url, file_path):
        ld1 = set(os.listdir(config.DOWNLOAD_PATH))

        self.driver.get("about:config")
        time.sleep(1)

        script = f"""
        var prefs = Components.classes["@mozilla.org/preferences-service;1"].getService(Components.interfaces.nsIPrefBranch);
        prefs.setCharPref(
    "print.printer_Print_to_File.print_to_filename", "{file_path}");"""

        self.driver.execute_script(script)
        self.driver.get(url)
        self.driver.execute_script("window.print();")
        time.sleep(2)
        for _ in range(100):
            self.driver.execute_script("window.scrollBy(0,50)")
        file_name = set()
        wait = 0
        while len(file_name) == 0 and wait < 30:
            ld2 = set(os.listdir(config.DOWNLOAD_PATH))
            file_name = ld2 - ld1
            if len(file_name) == 1:
                return file_name.pop()

            wait += 1
            time.sleep(1)

        return ""

    def quit(self):
        self.driver.quit()

    def __del__(self):
        self.quit()
