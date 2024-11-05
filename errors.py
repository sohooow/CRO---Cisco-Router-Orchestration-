from datetime import datetime
import multiprocessing as mp
import pytz
from config import Configuration

class Error():
    def __init__(self, url, description):
        self.address = url
        self.description = description

class Errors():
    def __init__(self):
        self.update_time()
        self.error_log = mp.Manager().dict()
        self.notification_sent = False

    def set_notification_sent(self, has_been_sent=True):
        self.notification_sent = has_been_sent


    def update_time(self):
        self.time = datetime.now(tz=pytz.timezone("Europe/Paris"))

    def add_error(self, environment, url, description):
        error = Error(url, description)
        if environment not in self.error_log.keys():
            self.error_log[environment] = []
        self.error_log[environment] += [error]
        # if environment not in self.error_log.keys():
        #     self.error_log.update({environment: []})
        # self.error_log[environment].append(error)

    def get_string_report(self):
        config = Configuration()
        environments = self.error_log.keys()
        is_any_error = len(environments) > 0
        body = config['CheckerErrorBody'] if is_any_error else config['CheckerNoErrorBody']
        body = body.replace('\\n', '\n').replace('%DATE%',self.time.strftime('%x')).replace('%TIME%',self.time.strftime('%X'))
        if len(environments) == 1:
            environments_to_show = environments[0]
        else:
            environments_to_show = ', '.join(self.error_log.keys())
            x = environments_to_show.rfind(',')
            environments_to_show = environments_to_show[:x] + ' and' + environments_to_show[x+1:]
        body = body.replace("%ENVIRONMENTS%",environments_to_show)
        return body