#!/usr/bin/env python3
"""
微信文章批量URL抓取工具
从URL列表文件批量抓取文章
"""

import sys
import argparse
from pathlib import Path
from wechat_scraper.scraper import WeChatScraper
from wechat_scraper.parser import MarkdownParser


def read_urls_from_file(file_path: str):
    """
    从文件读取URL列表

    Args:
        file_path: URL列表文件路径

    Returns:
        URL列表
    """
    urls = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if line and not line.startswith('#'):
                    urls.append(line)
        return urls
    except Exception as e:
        print(f"读取URL文件失败: {e}")
        return []


def scrape_batch_articles(urls, output_dir: str = "articles", ignore_images: bool = True):
    """
    批量抓取文章

    Args:
        urls: URL列表（可以是列表或文件路径）
        output_dir: 输出目录
        ignore_images: 是否忽略图片
    """
    # 如果是文件路径，读取URL
    if isinstance(urls, str):
        print(f"从文件读取URL列表: {urls}")
        url_list = read_urls_from_file(urls)
    else:
        url_list = urls

    if not url_list:
        print("没有找到任何URL！")
        return

    print(f"\n{'='*60}")
    print(f"微信文章批量抓取")
    print(f"{'='*60}\n")
    print(f"总共 {len(url_list)} 个URL")
    print(f"输出目录: {output_dir}\n")

    # 创建抓取器和解析器
    scraper = WeChatScraper()
    parser = MarkdownParser(ignore_images=ignore_images)

    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    success_count = 0
    failed_count = 0

    # 批量抓取
    for idx, url in enumerate(url_list, 1):
        print(f"\n[{idx}/{len(url_list)}] 正在处理...")
        print(f"URL: {url[:80]}...")

        try:
            # 获取文章内容
            article_detail = scraper.get_article_content(url)

            if not article_detail:
                print("  ✗ 获取内容失败")
                failed_count += 1
                continue

            title = article_detail.get('title', '无标题')
            print(f"  标题: {title}")

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
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(article_md)

            print(f"  ✓ 已保存: {filename}")
            success_count += 1

        except Exception as e:
            print(f"  ✗ 处理失败: {e}")
            failed_count += 1

    # 输出统计
    print(f"\n{'='*60}")
    print("批量抓取完成！")
    print(f"{'='*60}")
    print(f"总URL数: {len(url_list)}")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"保存位置: {output_path.absolute()}")
    print(f"{'='*60}\n")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="微信文章批量URL抓取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python scrape_batch.py --file urls.txt
  python scrape_batch.py -f urls.txt -o ./my_articles

URL文件格式（每行一个URL）:
  https://mp.weixin.qq.com/s/...
  https://mp.weixin.qq.com/s/...
  # 这是注释，会被忽略
  https://mp.weixin.qq.com/s/...
        """
    )

    parser.add_argument(
        '--file',
        '-f',
        required=True,
        help='URL列表文件路径'
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
        scrape_batch_articles(
            urls=args.file,
            output_dir=args.output,
            ignore_images=not args.include_images
        )

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
