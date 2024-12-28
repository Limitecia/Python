#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
利用requests+bs4爬取Quotes to Scrape网站的引言数据

"""

import requests
from bs4 import BeautifulSoup
import random
import time
import os

class GetQuotesData(object):
    """爬取10页的Quotes to Scrape引言数据"""

    base_url = 'http://quotes.toscrape.com/page/'  # 页码直接追加
    quotes_list = []

    def __init__(self):
        pass  # 无需初始化位置或代理

    def get_url_html(self, url):
        """请求页面HTML"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
        }

        for attempt in range(5):  # 尝试最多5次
            print(f"尝试请求URL: {url} (尝试 {attempt + 1}/5)")
            try:
                response = requests.get(url=url, headers=headers, timeout=10)
                response.raise_for_status()
                print(f"成功获取 HTML 内容，长度: {len(response.text)}")
                return response.content
            except requests.exceptions.RequestException as e:
                print(f"请求失败 (尝试 {attempt + 1}/5): {e}")
                time.sleep(random.uniform(1, 3))  # 等待1-3秒后重试
        return None

    def run(self):
        """执行爬取"""
        page_list = range(1, 11)  # 爬取前10页
        file_path = './quotes.md'

        # 打开文件，准备写入
        with open(file_path, 'w', encoding='UTF-8') as dict_file:
            print("文件已打开，准备写入数据...")
            # 写入表头
            dict_file.write('| 引言 | 作者 | 标签 |\n')
            dict_file.write('| --- | --- | --- |\n')

            for page in page_list:
                print(f"开始爬取第{page}页数据")
                boss_url = f"{self.base_url}{page}/"
                print(f"构建的URL: {boss_url}")

                html = self.get_url_html(boss_url)
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    quotes = soup.select('.quote')  # 每个引言块的选择器
                    if not quotes:
                        print(f"未找到引言信息，可能是页面结构发生变化或页面不存在。")
                        # 保存HTML内容用于调试
                        with open(f'page_{page}.html', 'w', encoding='utf-8') as f:
                            f.write(soup.prettify())
                        print(f"第{page}页的HTML内容已保存到 page_{page}.html")
                        continue
                    for quote in quotes:
                        try:
                            # 获取引言信息
                            text = quote.select('.text')[0].get_text().strip()
                            author = quote.select('.author')[0].get_text().strip()
                            tags = [tag.get_text().strip() for tag in quote.select('.tags .tag')]
                            tags_str = ', '.join(tags) if tags else '无'

                            # 写入到文件
                            dict_file.write(f"| {text} | {author} | {tags_str} |\n")
                            print(f"成功写入引言: {text[:30]}...")  # 只打印前30字符
                        except Exception as e:
                            print(f"解析引言信息失败: {e}")
                else:
                    print(f"第{page}页 HTML 获取失败，跳过。")
                time.sleep(random.uniform(2, 5))  # 增加随机延迟

        # 确保文件已生成且包含数据
        if os.path.exists(file_path) and os.path.getsize(file_path) > len('| 引言 | 作者 | 标签 |\n| --- | --- | --- |\n'):
            print(f"文件 {file_path} 已成功生成，包含引言数据。")
        else:
            print(f"文件 {file_path} 为空或仅包含表头，请检查爬取流程。")

# 程序主入口
if __name__ == '__main__':
    gl = GetQuotesData()
    gl.run()
