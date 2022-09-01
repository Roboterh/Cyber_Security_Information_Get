"""
这是华云安漏洞预警
https://vti.huaun.com/Vulnerability
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.service import Service
import time
from warning_main import Util

def get_data():
    '''
    获取数据
    '''
    ch_options = webdriver.ChromeOptions()
    #为Chrome配置无头模式
    ch_options.add_argument("--headless")  # 不提供可视化
    ch_options.headless = True
    ch_options.add_argument('--no-sandbox')
    ch_options.add_argument('--disable-dev-shm-usage')
    ch_options.add_argument('blink-settings=imagesEnabled=false') # 不加载图片

    # 在启动浏览器时加入配置

    driver = webdriver.Chrome(options=ch_options)
    data_tmp = []
    #s = Service(r"/usr/local/bin/geckodriver")
    #driver = webdriver.Firefox()
    # driver = webdriver.Firefox(executa)
    driver.get("https://vti.huaun.com/Vulnerability")
    time.sleep(3)

    rent_list = []     # 漏洞名
    cve_list = []      # CVE号
    warning_list = []  # 危险级别
    time_list = []     # 发布时间
    url_list = []      # 详细url
    detail_list = []   # 细节描述

    try:
        rent_list_elem = driver.find_elements(By.XPATH, '//tbody/tr/td[1]/div/a')
        cve_list_elem = driver.find_elements(By.XPATH, '//tbody/tr/td[2]/div')
        warning_list_elem = driver.find_elements(By.XPATH, '//tbody/tr/td[3]/div/span')
        time_list_elem = driver.find_elements(By.XPATH, '//tbody/tr/td[5]/div')
    
        for i in range(len(rent_list_elem)):
            rent_list.append(rent_list_elem[i].text)
            cve_name = str(cve_list_elem[i].text)
            cve_list.append(cve_name.replace(' (2)', ''))
            warning_list.append(warning_list_elem[i].text)
            time_list.append(time_list_elem[i].text)

        for i in rent_list_elem:
            time.sleep(2)
            i.click()
            n = driver.window_handles
            # print("句柄: " + n)
            driver.switch_to.window(n[-1])
            time.sleep(2)
            #print(driver.current_url)
            url_list.append(driver.current_url)
            #detail_list.append(driver.find_element(By.XPATH, "//div[@='detail-content']"))
            #print(driver.page_source)
            detail_list.append(driver.find_element(By.XPATH, "/html/body/div/div/div/section/main/div[1]/div[3]/div[2]/div[3]/div/div[1]/div[2]/div/div").text)
            # print("successful")
            driver.forward()
            driver.switch_to.window(n[0])
    except Exception as e:
        # 如果出现了错误，说明没有抓到对应元素
        Util.sendAPI("huayunan发生错误warning\r\n抓取{}元素失败{}".format(driver.current_url, e))
        Util.logger.error("huayunan发生错误warning\r\n抓取{}元素失败{}".format(driver.current_url, e))
        pass
    
    for i in range(len(rent_list)):
        data_tmp.append({"vuln_name": rent_list[i], "cve_name": cve_list[i], "warning": warning_list[i], 
                         "pushed_at": time_list[i], "cve_url": url_list[i], "detail": detail_list[i]})
    return data_tmp
