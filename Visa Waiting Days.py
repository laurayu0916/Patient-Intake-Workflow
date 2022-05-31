import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def visa_time(country):
    country_dic = {'China':['Shanghai', 'Beijing', 'Guangzhou', 'Shenyang'],
                   'Venezuela':['Caracas'],
                   'Canada': ['Ottawa', 'Toronto']}
    browser = webdriver.Chrome(executable_path='/Users/yuxiaomeng/Documents/chromedriver')
    browser.get('https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/wait-times.html')

    xpath_input = '/html/body/div[3]/div[7]/div[2]/div[1]/div[2]/div[4]/div/div[2]/div[1]/div/form/input[1]'
    xpath_change = '//*[@id="visa_plan_ahead_rwd"]/div[2]/div[2]/div/span'

    list_of_city = country_dic[country]

    my_input = browser.find_element_by_xpath(xpath_input)
    visa = {}
    for el in list_of_city:
        my_input.send_keys(el)
        my_input.send_keys(Keys.ENTER)
        time.sleep(1)
        visitor_value = browser.find_element_by_class_name('num_days_visitor').text.replace('Calendar Days', '').replace('Calendar Day', '')
        student_value = browser.find_element_by_class_name('num_days_student_exchange').text.replace('Calendar Days', '').replace('Calendar Day', '')
        other_value = browser.find_element_by_class_name('num_days_other').text.replace('Calendar Days', '').replace('Calendar Day', '')
        lst = [visitor_value,student_value,other_value]
        for i in range(len(lst)):
            str = lst[i]
            if str[-1] == ' ':
                str = str.replace(' ', '')
                lst[i] = str
        visa[el] = lst
        change = browser.find_element_by_xpath(xpath_change)
        change.click()

    visa = pd.DataFrame(visa)
    visa.index = ['Visitor Visa', 'Student Visa', 'Other Visas']
    browser.close()
    return visa

country_name = input('Please Enter the Country: ')
print(visa_time(country_name))
