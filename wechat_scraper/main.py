"""
微信公众号文章抓取工具 - 主程序
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict

from .scraper import WeChatScraper
from .parser import MarkdownParser


def save_article(article_md: str, filename: str, output_dir: Path) -> bool:
    """
    保存文章到文件

    Args:
        article_md: Markdown格式的文章内容
        filename: 文件名
        output_dir: 输出目录

    Returns:
        是否保存成功
    """
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(article_md)

        print(f"✓ 已保存: {filename}")
        return True

    except Exception as e:
        print(f"✗ 保存失败 {filename}: {e}")
        return False


def scrape_wechat_account(
    account_name: str,
    output_dir: str = "articles",
    max_pages: int = 10,
    ignore_images: bool = True
) -> None:
    """
    抓取微信公众号所有文章

    Args:
        account_name: 公众号名称
        output_dir: 输出目录
        max_pages: 最大翻页数
        ignore_images: 是否忽略图片
    """
    print(f"\n{'='*60}")
    print(f"微信公众号文章抓取工具")
    print(f"{'='*60}\n")
    print(f"目标公众号: {account_name}")
    print(f"输出目录: {output_dir}")
    print(f"最大页数: {max_pages}")
    print(f"忽略图片: {'是' if ignore_images else '否'}\n")

    # 创建抓取器和解析器
    scraper = WeChatScraper()
    parser = MarkdownParser(ignore_images=ignore_images)

    # 创建输出目录
    output_path = Path(output_dir) / account_name
    output_path.mkdir(parents=True, exist_ok=True)

    # 获取文章列表
    print(f"\n{'='*60}")
    print("第一步: 获取文章列表")
    print(f"{'='*60}\n")

    articles = scraper.get_article_list(account_name, max_pages=max_pages)

    if not articles:
        print("\n未获取到任何文章！可能的原因：")
        print("1. 公众号名称不正确")
        print("2. 网络问题或被反爬虫限制")
        print("3. 搜狗微信搜索暂时不可用")
        return

    # 下载并保存文章
    print(f"\n{'='*60}")
    print(f"第二步: 下载文章内容 (共 {len(articles)} 篇)")
    print(f"{'='*60}\n")

    success_count = 0
    failed_count = 0

    for idx, article in enumerate(articles, 1):
        title = article.get('title', '无标题')
        link = article.get('link', '')

        print(f"\n[{idx}/{len(articles)}] {title}")

        if not link:
            print("  ✗ 跳过: 没有链接")
            failed_count += 1
            continue

        # 获取文章详细内容
        article_detail = scraper.get_article_content(link)

        if not article_detail:
            print("  ✗ 获取内容失败")
            failed_count += 1
            continue

        # 转换为Markdown
        article_md = parser.create_article_markdown(article_detail)

        if not article_md:
            print("  ✗ 转换Markdown失败")
            failed_count += 1
            continue

        # 生成文件名
        filename = parser.sanitize_filename(f"{title}.md")

        # 保存文章
        if save_article(article_md, filename, output_path):
            success_count += 1
        else:
            failed_count += 1

    # 输出统计信息
    print(f"\n{'='*60}")
    print("抓取完成！")
    print(f"{'='*60}")
    print(f"总文章数: {len(articles)}")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"保存位置: {output_path.absolute()}")
    print(f"{'='*60}\n")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="微信公众号文章抓取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python -m wechat_scraper.main --account "中科星图"
  python -m wechat_scraper.main --account "中科星图" --output ./my_articles --max-pages 20
        """
    )

    parser.add_argument(
        '--account',
        '-a',
        required=True,
        help='公众号名称'
    )

    parser.add_argument(
        '--output',
        '-o',
        default='articles',
        help='输出目录 (默认: articles)'
    )

    parser.add_argument(
        '--max-pages',
        '-m',
        type=int,
        default=10,
        help='最大翻页数 (默认: 10)'
    )

    parser.add_argument(
        '--include-images',
        action='store_true',
        help='保留图片链接 (默认忽略)'
    )

    args = parser.parse_args()

    try:
        scrape_wechat_account(
            account_name=args.account,
            output_dir=args.output,
            max_pages=args.max_pages,
            ignore_images=not args.include_images
        )
    except KeyboardInterrupt:
        print("\n\n用户中断，程序退出。")
        sys.exit(0)
    except Exception as e:
        print(f"\n发生错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
