#!/usr/bin/env python3
"""
从单篇文章URL自动抓取整个公众号的所有文章
自动提取公众号名称并批量抓取
"""

import sys
import argparse
from pathlib import Path
from wechat_scraper.scraper import WeChatScraper
from wechat_scraper.parser import MarkdownParser


def scrape_account_from_article_url(
    article_url: str,
    output_dir: str = "articles",
    max_pages: int = 10,
    ignore_images: bool = True
):
    """
    从单篇文章URL自动抓取整个公众号的所有文章

    Args:
        article_url: 微信文章URL
        output_dir: 输出目录
        max_pages: 最大翻页数
        ignore_images: 是否忽略图片
    """
    print(f"\n{'='*60}")
    print(f"从文章URL自动抓取整个公众号")
    print(f"{'='*60}\n")
    print(f"文章链接: {article_url[:80]}...")
    print(f"输出目录: {output_dir}")
    print(f"最大页数: {max_pages}\n")

    # 创建抓取器和解析器
    scraper = WeChatScraper()
    parser = MarkdownParser(ignore_images=ignore_images)

    # 第一步：从文章URL提取公众号名称
    print(f"{'='*60}")
    print("第一步：提取公众号信息")
    print(f"{'='*60}\n")

    account_name = scraper.get_account_name_from_url(article_url)

    if not account_name:
        print("\n✗ 无法提取公众号名称！")
        print("可能的原因：")
        print("1. URL无效或文章已被删除")
        print("2. 网络问题")
        print("3. 文章页面结构发生变化")
        return False

    # 第二步：获取该公众号的文章列表
    print(f"\n{'='*60}")
    print(f"第二步：获取 {account_name} 的文章列表")
    print(f"{'='*60}\n")

    articles = scraper.get_article_list(account_name, max_pages=max_pages)

    if not articles:
        print("\n未获取到任何文章！可能的原因：")
        print("1. 公众号名称不完全匹配")
        print("2. 搜狗微信搜索暂时不可用")
        print("3. 网络问题或被反爬虫限制")
        print("\n建议：尝试使用批量URL抓取方式（scrape_batch.py）")
        return False

    # 第三步：下载并保存文章
    print(f"\n{'='*60}")
    print(f"第三步：下载文章内容 (共 {len(articles)} 篇)")
    print(f"{'='*60}\n")

    # 创建输出目录
    output_path = Path(output_dir) / account_name
    output_path.mkdir(parents=True, exist_ok=True)

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
        file_path = output_path / filename

        # 保存文章
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(article_md)

            print(f"  ✓ 已保存: {filename}")
            success_count += 1

        except Exception as e:
            print(f"  ✗ 保存失败: {e}")
            failed_count += 1

    # 输出统计信息
    print(f"\n{'='*60}")
    print("抓取完成！")
    print(f"{'='*60}")
    print(f"公众号: {account_name}")
    print(f"总文章数: {len(articles)}")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"保存位置: {output_path.absolute()}")
    print(f"{'='*60}\n")

    return True


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="从单篇文章URL自动抓取整个公众号的所有文章",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python scrape_from_article.py --url "https://mp.weixin.qq.com/s/..."
  python scrape_from_article.py -u "https://mp.weixin.qq.com/s/..." --max-pages 20

工作流程:
  1. 访问文章URL，自动提取公众号名称
  2. 使用公众号名称搜索所有历史文章
  3. 批量下载并保存为Markdown格式
        """
    )

    parser.add_argument(
        '--url',
        '-u',
        required=True,
        help='微信文章URL（任意一篇该公众号的文章）'
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
        help='最大翻页数 (默认: 10，每页约10篇文章)'
    )

    parser.add_argument(
        '--include-images',
        action='store_true',
        help='保留图片链接 (默认忽略)'
    )

    args = parser.parse_args()

    try:
        success = scrape_account_from_article_url(
            article_url=args.url,
            output_dir=args.output,
            max_pages=args.max_pages,
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
