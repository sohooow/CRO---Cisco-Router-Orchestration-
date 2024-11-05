# coding: utf-8

import asyncio
import threading
import requests
from config import Configuration
from notifier import Notifier
from errors import Errors
from multiprocessing import Pool
from distutils.util import strtobool
from datetime import datetime

class Checker():

    def convert_urls(self,urls, env):
        if (env == 'Production'):
            env_url = ''
        else:
            env_url = '-' + env.lower()
        results = []
        for url in urls:
            results += [f'https://{url}{env_url}.mbww.net']
        return results

    def __init__(self):
        config = Configuration()
        self.servers_to_check = {env:self.convert_urls(config[('URLs')].split(';'), env) for env in ['Production','Staging', 'QA', 'Test']}
        self.is_any_error = False
        self.check_frequency = int(config["CheckerFrequency"])
        self.notification_already_sent = False
        self.last_errors = Errors()

    def _check_and_add_error(self, environment,url, running_url, errors):
        print(running_url)
        is_any_error = False
        config = Configuration()
        timeout = int(config["Timeout"])
        try:
            r = requests.get(running_url, timeout=timeout)
            if r.status_code != 200:
                raise Exception(f"Status code {r.status_code} : {r.reason}")
            if r.elapsed.total_seconds() >= timeout:
                raise Exception(f"Response time of the server is too long ({r.elapsed.total_seconds()}s).")                      
        except Exception as e:
            is_any_error = True
            errors.add_error(environment, url, str(e))
        return is_any_error

    def check_errors(self):
        errors = Errors()
        arguments=[]
        for environment in self.servers_to_check.keys():
            for url in self.servers_to_check[environment]:

                running_url = url + "/isrunning"
                arguments += [(environment,url, running_url, errors)]

        with Pool() as pool:
            errors_return = pool.starmap(self._check_and_add_error, arguments)
        self.is_any_error = any(errors_return)
        errors.update_time()
        return errors

    async def _run_infinite_while(self):
        config = Configuration()
        overtime = 0
        last_send_time = datetime.now()
        was_any_error = False
        send_email = strtobool(config['SendEmail'])
        temporary_disabled_email = False
        default_overtime = int(config['Overtime'])
        
        env_to_disable = config["EnvironmentsWithoutEmail"].split(";")
        while True:
            try:
                new_errors = self.check_errors()
                was_any_error = len(self.last_errors.error_log.keys()) > 0
                environments = new_errors.error_log.keys()
                if len(new_errors.error_log) > len(self.last_errors.error_log):
                    overtime = 0
                self.last_errors = new_errors
                temporary_disabled_email = all([environment in env_to_disable for environment in environments])
                if self.is_any_error and send_email and not temporary_disabled_email:
                    if (datetime.now()-last_send_time).total_seconds() >= overtime:
                        self.send_notifications(self.notification_already_sent)
                        last_send_time = datetime.now()
                        overtime = overtime + default_overtime
                        overtime = 86400 if overtime > 86400 else overtime 
                else:
                    overtime = 0
                    self.notification_already_sent = False
                if was_any_error and self.is_any_error == False:
                    self.send_notifications()
                    was_any_error = False
                await asyncio.sleep(self.check_frequency)
            except Exception:
                pass

    def send_notifications(self, reminder = False):
        try:
            notifier = Notifier()
            config = Configuration()
            body = self.last_errors.get_string_report()
            subject = config['CheckerErrorSubject'] if self.is_any_error else config['CheckerNoErrorSubject']
            if reminder:
                subject = config['CheckerReminderSubject']
            notifier.send(config['CheckerPeopleToNotify'].split(';'),subject,body)
            self.notification_already_sent = True
            self.last_errors.set_notification_sent()
        except Exception as e:
            self.last_errors.set_notification_sent(False)

    def run_in_background(self):
        loop = asyncio.new_event_loop()
        threading.Thread(target=loop.run_forever, args=()).start()
        asyncio.run_coroutine_threadsafe(self._run_infinite_while(), loop)


