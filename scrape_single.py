#!/usr/bin/env python3
"""
微信文章URL直接抓取工具
直接从URL抓取单篇文章，无需搜索
"""

import sys
import argparse
from pathlib import Path
from wechat_scraper.scraper import WeChatScraper
from wechat_scraper.parser import MarkdownParser


def scrape_single_article(url: str, output_dir: str = "articles", ignore_images: bool = True):
    """
    从URL直接抓取单篇文章

    Args:
        url: 微信文章URL
        output_dir: 输出目录
        ignore_images: 是否忽略图片
    """
    print(f"\n{'='*60}")
    print(f"微信文章直接抓取")
    print(f"{'='*60}\n")
    print(f"文章链接: {url[:80]}...")
    print(f"输出目录: {output_dir}\n")

    # 创建抓取器和解析器
    scraper = WeChatScraper()
    parser = MarkdownParser(ignore_images=ignore_images)

    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 获取文章内容
    print("正在获取文章内容...")
    article_detail = scraper.get_article_content(url)

    if not article_detail:
        print("\n✗ 获取文章内容失败！")
        print("可能的原因：")
        print("1. URL无效或文章已被删除")
        print("2. 网络问题")
        print("3. 文章需要登录查看")
        return False

    # 转换为Markdown
    print("正在转换为Markdown格式...")
    article_md = parser.create_article_markdown(article_detail)

    if not article_md:
        print("\n✗ 转换Markdown失败！")
        return False

    # 生成文件名
    title = article_detail.get('title', '无标题')
    filename = parser.sanitize_filename(f"{title}.md")
    file_path = output_path / filename

    # 保存文章
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(article_md)

        print(f"\n{'='*60}")
        print("✓ 抓取成功！")
        print(f"{'='*60}")
        print(f"标题: {title}")
        print(f"作者: {article_detail.get('author', '未知')}")
        print(f"发布时间: {article_detail.get('pub_time', '未知')}")
        print(f"保存位置: {file_path.absolute()}")
        print(f"{'='*60}\n")
        return True

    except Exception as e:
        print(f"\n✗ 保存文件失败: {e}")
        return False


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="微信文章URL直接抓取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python scrape_single.py --url "https://mp.weixin.qq.com/s/..."
  python scrape_single.py -u "https://mp.weixin.qq.com/s/..." -o ./my_articles
        """
    )

    parser.add_argument(
        '--url',
        '-u',
        required=True,
        help='微信文章URL'
    )

    parser.add_argument(
        '--output',
        '-o',
        default='articles',
        help='输出目录 (默认: articles)'
    )

    parser.add_argument(
        '--include-images',
        action='store_true',
        help='保留图片链接 (默认忽略)'
    )

    args = parser.parse_args()

    try:
        success = scrape_single_article(
            url=args.url,
            output_dir=args.output,
            ignore_images=not args.include_images
        )
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n用户中断，程序退出。")
        sys.exit(0)
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
