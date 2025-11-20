"""
HTML到Markdown转换工具
"""

import html2text
import re
from typing import Dict


class MarkdownParser:
    """HTML到Markdown转换器"""

    def __init__(self, ignore_images: bool = True):
        """
        初始化转换器

        Args:
            ignore_images: 是否忽略图片（不保留图片链接）
        """
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = ignore_images
        self.h2t.ignore_emphasis = False
        self.h2t.body_width = 0  # 不自动换行
        self.h2t.unicode_snob = True
        self.h2t.skip_internal_links = True

    def html_to_markdown(self, html_content: str) -> str:
        """
        将HTML转换为Markdown

        Args:
            html_content: HTML内容

        Returns:
            Markdown格式的文本
        """
        if not html_content:
            return ""

        try:
            # 转换为Markdown
            markdown = self.h2t.handle(html_content)

            # 清理多余的空行
            markdown = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown)

            # 去除首尾空白
            markdown = markdown.strip()

            return markdown

        except Exception as e:
            print(f"HTML转Markdown时出错: {e}")
            return ""

    def create_article_markdown(self, article_data: Dict) -> str:
        """
        创建完整的文章Markdown文档

        Args:
            article_data: 文章数据字典，包含title, author, pub_time, content_html, url

        Returns:
            完整的Markdown文档
        """
        title = article_data.get('title', '无标题')
        author = article_data.get('author', '未知作者')
        pub_time = article_data.get('pub_time', '')
        url = article_data.get('url', '')
        content_html = article_data.get('content_html', '')

        # 转换正文
        content_md = self.html_to_markdown(content_html)

        # 构建完整的Markdown文档
        markdown_doc = f"""# {title}

**作者**: {author}
**发布时间**: {pub_time}
**原文链接**: {url}

---

{content_md}
"""

        return markdown_doc

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        清理文件名，移除不合法的字符

        Args:
            filename: 原始文件名

        Returns:
            清理后的文件名
        """
        # 移除或替换不合法的文件名字符
        illegal_chars = r'[<>:"/\\|?*\x00-\x1f]'
        filename = re.sub(illegal_chars, '_', filename)

        # 限制文件名长度
        max_length = 200
        if len(filename) > max_length:
            filename = filename[:max_length]

        return filename.strip()
