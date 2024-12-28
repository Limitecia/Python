import requests
from bs4 import BeautifulSoup
import time
import random


class GetBossData(object):
    """爬取Boss直聘职位数据"""
    domain = 'https://www.zhipin.com'
    base_url = 'https://www.zhipin.com/c101280600/?query='
    position = ''
    # SecretId 和 SecretKey
    secret_id = "oxf8kld793tnp4g46uw9"
    secret_key = "ejckm7enbhs9i9w3j8g5cg1q2ccno63g"
    api_url = "https://dps.kdlapi.com/api/getdps/"
    username = "d4455409888"
    password = "eezl5z2x"

    def __init__(self, position):
        self.position = position
        self.valid_proxies = self.update_proxies()  # 动态获取有效代理

    def update_proxies(self):
        """通过API获取代理列表并清理"""
        try:
            params = {
                "secret_id": self.secret_id,
                "signature": self.secret_key,
                "num": 20,  # 获取20个代理
                "pt": 1,  # HTTP(S) 代理类型
                "format": "text",
                "sep": 1  # 换行分隔
            }
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            # 获取代理列表并清理多余字符
            proxy_ips = response.text.strip().split("\n")
            valid_proxies = []
            for proxy_ip in proxy_ips:
                clean_proxy_ip = proxy_ip.strip().replace("\r", "")  # 去除 `\r`
                proxy = {
                    "http": f"http://{self.username}:{self.password}@{clean_proxy_ip}",
                    "https": f"http://{self.username}:{self.password}@{clean_proxy_ip}"
                }
                valid_proxies.append(proxy)
            print(f"成功获取代理列表: {valid_proxies}")
            return valid_proxies
        except requests.exceptions.RequestException as e:
            print(f"获取代理列表失败: {e}")
            return []

    def get_random_proxy(self):
        """随机选择一个代理"""
        if not self.valid_proxies:
            raise Exception("没有可用的代理，请检查代理池或API接口！")
        return random.choice(self.valid_proxies)

    def get_url_html(self, url, cookie):
        """请求页面html"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'cookie': cookie
        }

        for _ in range(5):  # 尝试最多 5 次
            proxies = self.get_random_proxy()
            print(f"使用代理: {proxies}")
            try:
                response = requests.get(url=url, headers=headers, proxies=proxies, timeout=10)
                response.raise_for_status()
                return response.content
            except requests.exceptions.RequestException as e:
                print(f"代理连接失败: {e}")
                time.sleep(2)  # 等待 2 秒后重试
        return None

    def run(self):
        """执行爬虫"""
        page_list = range(1, 11)
        # 打开文件，准备写入
        with open('job.md', 'a', encoding='UTF-8') as dict_file:
            # 清空文件内容
            dict_file.seek(0)
            dict_file.truncate()
            dict_file.write('| 岗位 | 区域 | 薪资 | 年限信息 | 公司名称 | 公司信息 | 链接 |')
            dict_file.write('\n| --- | --- | --- | --- | --- | --- | --- |')
            # 分页爬取数据
            for page in page_list:
                print('开始爬取第' + str(page) + '页数据')
                boss_url = self.base_url + str(self.position) + f'&page={page}&ka=page-{page}'
                cookie_val = 'your_cookie_here'  # 替换为有效的cookie
                html = self.get_url_html(boss_url, cookie_val)
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    job_list = soup.select('.job-list ul li')
                    for job_li in job_list:
                        # 单条职位信息
                        url = self.domain + job_li.select('.job-title a')[0].attrs['href']
                        title = job_li.select('.job-title a')[0].get_text()
                        area = job_li.select('.job-title .job-area')[0].get_text()
                        salary = job_li.select('.job-limit .red')[0].get_text()
                        year = job_li.select('.job-limit p')[0].get_text()
                        company = job_li.select('.info-company h3')[0].get_text()
                        industry = job_li.select('.info-company p')[0].get_text()
                        info = {
                            'title': title,
                            'area': area,
                            'salary': salary,
                            'year': year,
                            'company': company,
                            'industry': industry,
                            'url': url
                        }
                        print(info)
                        # 写入职位信息
                        info_demo = '\n| %s | %s | %s | %s | %s | %s | %s |'
                        dict_file.write(info_demo % (title, area, salary, year, company, industry, url))
                else:
                    print(f"第{page}页爬取失败，跳过。")
                time.sleep(random.uniform(2, 5))  # 增加随机延迟

# 程序主入口
if __name__ == '__main__':
    # 实例化
    job_name = input('请输入职位关键字：').strip()
    if job_name == '':
        print('关键字为空，请重新尝试')
        exit(0)
    gl = GetBossData(job_name)
    # 执行脚本
    gl.run()
