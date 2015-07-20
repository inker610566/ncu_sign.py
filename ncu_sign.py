from selenium import webdriver
from datetime import datetime
from datetime import timedelta
from random import randint
from time import sleep
from sys import stdout

def log(s):
    stdout.write("ncu_sign: %s\n" % s)
    stdout.flush()

def login(browser, url, username, password):
    browser.get(url)
    user = browser.find_element_by_id("userid_input")
    user.send_keys(username)

    pw = browser.find_element_by_name("j_password")
    pw.send_keys(password)

    submit = browser.find_element_by_name("submit")
    submit.click()

def getProjectNumber(username, password):
    browser = webdriver.Firefox()
    login(browser, "http://140.115.182.62/PartTime/parttime.php/query", username, password)
    table = browser.find_element_by_tag_name("table")
    result = len(table.find_elements_by_tag_name("tr")) -1
    browser.close()
    return result


def sign_in(username, password, project_no):
    browser = webdriver.Firefox()
    login(browser, "http://140.115.182.62/PartTime/parttime.php/signin", username, password)
    # click radio
    table = browser.find_elements_by_tag_name("table")[1]
    tr = table.find_elements_by_tag_name("tr")[project_no]
    radio = tr.find_element_by_name("signin")
    radio.click()
    browser.find_element_by_id("submit").click()
    browser.close()

def sign_out(username, password):
    browser = webdriver.Firefox()
    login(browser, "http://140.115.182.62/PartTime/parttime.php/signout", username, password)
    # click radio
    table = browser.find_elements_by_tag_name("table")[0]
    tr = table.find_elements_by_tag_name("tr")[1]
    radio = tr.find_element_by_name("signout")
    radio.click()
    browser.find_element_by_name("submit").click()
    browser.close()

class NotOnTimeException(Exception):
    def __init__(self):
        pass


def sign_in_and_sign_out(username, password, start, end, project_no):
    '''
    :param username:
    :param password:
    :param start:
    :param end:
    :param project_no: start from 1
    :return:
    '''
    if start < datetime.now():
        raise NotOnTimeException
    start -= timedelta(seconds=randint(300, 1700))
    log("intend to sign-in at %s" % start.strftime("%Y/%m/%d %H-%M-%S"))
    d = start - datetime.now()
    if d > timedelta(seconds=0):
        log("sleep %s seconds" % d.seconds)
        sleep(d.seconds)
    #sign_in(username, password, 1)
    sign_in(username, password, project_no)

    end += timedelta(seconds=randint(300, 1700))
    log("intend to sign-out at %s" % end.strftime("%Y/%m/%d %H-%M-%S"))
    d = end - datetime.now()
    log("sleep %s seconds" % d.seconds)
    sleep(d.seconds)
    sign_out(username, password)



def getNextHour(hour):
    x = datetime.now()
    x = datetime(year=x.year, month=x.month, day=x.day, hour=hour, minute=0, second=0)
    if x > datetime.now():
        return x
    else:
        return x + timedelta(days=1)

class ProjectTooMuchException(Exception):
    def __init__(self):
        pass

def sign_in_daemon(username, password):

    # First execution
    pn = getProjectNumber(username, password)
    if pn >= 3:
        raise ProjectTooMuchException

    while True:
        # first project start at 6:00 - delta ~ 14:00 + delta
        try:
            sign_in_and_sign_out(username, password, getNextHour(6), getNextHour(14), 1)
        except NotOnTimeException:
            pass

        # second project start at  15:00 - delta ~ 23:00 + delta
        try:
            sign_in_and_sign_out(username, password, getNextHour(15), getNextHour(23), 2)
        except NotOnTimeException:
            pass


    #browser = webdriver.Firefox()

if __name__ == "__main__":
    import secret
    sign_in_daemon(secret.username, secret.password)
	


