"""
微信公众号文章抓取器
"""

import requests
import time
import re
import random
from typing import List, Dict, Optional
from urllib.parse import quote
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class WeChatScraper:
    """微信公众号文章抓取器"""

    def __init__(self, retry_times: int = 3):
        """
        初始化抓取器

        Args:
            retry_times: 请求失败时的重试次数
        """
        self.ua = UserAgent()
        self.session = requests.Session()
        self.sogou_search_url = "https://weixin.sogou.com/weixin"
        self.sogou_article_url = "https://weixin.sogou.com/weixin"
        self.retry_times = retry_times

    def _get_headers(self, referer: str = None) -> Dict[str, str]:
        """
        获取请求头，模拟真实浏览器

        Args:
            referer: 来源URL

        Returns:
            请求头字典
        """
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
        }

        if referer:
            headers['Referer'] = referer

        return headers

    def _random_sleep(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """
        随机延时，模拟人工操作

        Args:
            min_seconds: 最小延时秒数
            max_seconds: 最大延时秒数
        """
        sleep_time = random.uniform(min_seconds, max_seconds)
        time.sleep(sleep_time)

    def _request_with_retry(self, url: str, params: Dict = None, referer: str = None) -> Optional[requests.Response]:
        """
        带重试机制的请求

        Args:
            url: 请求URL
            params: 请求参数
            referer: 来源URL

        Returns:
            响应对象，失败返回None
        """
        for attempt in range(self.retry_times):
            try:
                # 每次重试前随机延时
                if attempt > 0:
                    retry_delay = 2 ** attempt + random.uniform(0, 1)
                    print(f"  第 {attempt + 1} 次重试，等待 {retry_delay:.1f} 秒...")
                    time.sleep(retry_delay)

                response = self.session.get(
                    url,
                    params=params,
                    headers=self._get_headers(referer=referer),
                    timeout=30
                )

                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    print(f"  请求过于频繁 (HTTP 429)，等待后重试...")
                    time.sleep(5)
                else:
                    print(f"  HTTP 状态码: {response.status_code}")

            except requests.exceptions.Timeout:
                print(f"  请求超时...")
            except requests.exceptions.RequestException as e:
                print(f"  请求异常: {e}")

        return None

    def search_official_account(self, account_name: str) -> Optional[str]:
        """
        搜索公众号，获取公众号主页链接

        Args:
            account_name: 公众号名称

        Returns:
            公众号主页链接，如果未找到返回None
        """
        print(f"正在搜索公众号: {account_name}")

        params = {
            'type': 1,  # 1表示搜索公众号
            'query': account_name,
        }

        try:
            response = self._request_with_retry(
                self.sogou_search_url,
                params=params,
                referer='https://weixin.sogou.com/'
            )

            if not response:
                print(f"搜索失败")
                return None

            soup = BeautifulSoup(response.text, 'lxml')

            # 查找公众号链接
            account_link = soup.find('a', {'uigs': 'account_name_0'})
            if account_link and account_link.get('href'):
                print(f"找到公众号主页")
                return account_link['href']

            print("未找到公众号")
            return None

        except Exception as e:
            print(f"搜索公众号时出错: {e}")
            return None

    def get_article_list(self, account_name: str, max_pages: int = 10) -> List[Dict]:
        """
        获取公众号文章列表

        Args:
            account_name: 公众号名称
            max_pages: 最大翻页数

        Returns:
            文章信息列表
        """
        print(f"开始获取 {account_name} 的文章列表...")
        articles = []

        params = {
            'type': 2,  # 2表示搜索文章
            'query': account_name,
            'page': 1,
        }

        for page in range(1, max_pages + 1):
            params['page'] = page
            print(f"正在获取第 {page} 页...")

            try:
                # 随机延时，模拟人工操作
                self._random_sleep(2, 4)

                response = self._request_with_retry(
                    self.sogou_article_url,
                    params=params,
                    referer='https://weixin.sogou.com/'
                )

                if not response:
                    print(f"获取第 {page} 页失败")
                    break

                soup = BeautifulSoup(response.text, 'lxml')

                # 查找文章列表
                news_list = soup.find_all('div', class_='txt-box')

                if not news_list:
                    print(f"第 {page} 页没有找到文章，停止翻页")
                    break

                for news in news_list:
                    try:
                        # 提取文章标题和链接
                        title_tag = news.find('h3')
                        if not title_tag:
                            continue

                        link_tag = title_tag.find('a')
                        if not link_tag:
                            continue

                        title = link_tag.get_text(strip=True)
                        link = link_tag.get('href', '')

                        # 提取发布时间
                        time_tag = news.find('span', class_='s2')
                        pub_time = time_tag.get_text(strip=True) if time_tag else ''

                        # 提取摘要
                        summary_tag = news.find('p', class_='txt-info')
                        summary = summary_tag.get_text(strip=True) if summary_tag else ''

                        if title and link:
                            article = {
                                'title': title,
                                'link': link,
                                'pub_time': pub_time,
                                'summary': summary
                            }
                            articles.append(article)
                            print(f"  - {title}")

                    except Exception as e:
                        print(f"解析文章信息时出错: {e}")
                        continue

                print(f"第 {page} 页获取到 {len(news_list)} 篇文章")

            except Exception as e:
                print(f"获取第 {page} 页时出错: {e}")
                break

        print(f"\n总共获取到 {len(articles)} 篇文章")
        return articles

    def get_article_content(self, url: str) -> Optional[Dict]:
        """
        获取文章详细内容

        Args:
            url: 文章链接

        Returns:
            文章内容字典
        """
        try:
            # 随机延时，模拟人工操作
            self._random_sleep(1, 2)

            response = self._request_with_retry(
                url,
                referer='https://mp.weixin.qq.com/'
            )

            if not response:
                print(f"获取文章内容失败")
                return None

            # 设置正确的编码
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'lxml')

            # 提取文章标题
            title_tag = soup.find('h1', class_='rich_media_title')
            title = title_tag.get_text(strip=True) if title_tag else ''

            # 提取作者/公众号名称
            author_tag = soup.find('span', class_='rich_media_meta_nickname')
            if not author_tag:
                author_tag = soup.find('strong', class_='profile_nickname')
            if not author_tag:
                author_tag = soup.find('div', id='js_name')
            if not author_tag:
                author_tag = soup.find('a', class_='rich_media_meta_link')
            if not author_tag:
                author_tag = soup.find('span', class_='rich_media_meta_text')
            author = author_tag.get_text(strip=True) if author_tag else ''

            # 提取发布时间
            time_tag = soup.find('em', id='publish_time')
            if not time_tag:
                time_tag = soup.find('span', class_='rich_media_meta rich_media_meta_text')
            pub_time = time_tag.get_text(strip=True) if time_tag else ''

            # 提取正文内容
            content_tag = soup.find('div', class_='rich_media_content')
            if not content_tag:
                content_tag = soup.find('div', id='js_content')

            content_html = str(content_tag) if content_tag else ''

            return {
                'title': title,
                'author': author,
                'pub_time': pub_time,
                'content_html': content_html,
                'url': url
            }

        except Exception as e:
            print(f"获取文章内容时出错: {e}")
            return None

    def get_account_name_from_url(self, url: str) -> Optional[str]:
        """
        从文章URL中提取公众号名称

        Args:
            url: 微信文章URL

        Returns:
            公众号名称，如果提取失败返回None
        """
        print(f"正在从文章中提取公众号信息...")

        try:
            # 随机延时
            self._random_sleep(1, 2)

            response = self._request_with_retry(
                url,
                referer='https://mp.weixin.qq.com/'
            )

            if not response:
                print("无法访问文章")
                return None

            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')

            # 尝试多种方式提取公众号名称
            account_name = None

            # 方法1: 查找 rich_media_meta_nickname (span标签) - 最常见的方式
            nickname_tag = soup.find('span', class_='rich_media_meta_nickname')
            if nickname_tag:
                account_name = nickname_tag.get_text(strip=True)

            # 方法2: 查找 profile_nickname
            if not account_name:
                nickname_tag = soup.find('strong', class_='profile_nickname')
                if nickname_tag:
                    account_name = nickname_tag.get_text(strip=True)

            # 方法3: 查找 js_name
            if not account_name:
                name_tag = soup.find('div', id='js_name')
                if name_tag:
                    account_name = name_tag.get_text(strip=True)

            # 方法4: 查找 rich_media_meta_link (a标签)
            if not account_name:
                meta_tag = soup.find('a', class_='rich_media_meta_link')
                if meta_tag:
                    account_name = meta_tag.get_text(strip=True)

            # 方法5: 查找任何包含公众号信息的 meta 标签
            if not account_name:
                meta_tag = soup.find('span', class_='rich_media_meta_text')
                if meta_tag:
                    account_name = meta_tag.get_text(strip=True)

            if account_name:
                print(f"✓ 找到公众号: {account_name}")
                return account_name
            else:
                print("✗ 未能提取公众号名称")
                return None

        except Exception as e:
            print(f"提取公众号名称时出错: {e}")
            return None
