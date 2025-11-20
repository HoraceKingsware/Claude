# 微信公众号文章抓取工具

一个用于抓取微信公众号历史文章并保存为 Markdown 格式的 Python 工具。

## 功能特点

- 🔍 **三种抓取模式**：公众号搜索、单篇URL、批量URL
- 📝 自动将文章转换为 Markdown 格式（包含标题、作者、时间、正文）
- 💾 批量下载并本地保存
- 🎯 支持自定义抓取页数和输出目录
- 🚀 简单易用的命令行接口
- 🖼️ 可选择保留或忽略图片链接

## 安装依赖

```bash
pip install -r requirements.txt
```

## 三种使用方式

### 方式一：通过公众号名称搜索抓取（推荐批量抓取）

通过搜狗微信搜索获取公众号文章列表：

```bash
python run.py --account "中科星图"
```

优点：可以批量获取历史文章
缺点：可能受搜狗微信搜索限制

### 方式二：直接URL抓取单篇文章（推荐单篇抓取）

如果你有文章链接，直接抓取单篇文章：

```bash
python scrape_single.py --url "https://mp.weixin.qq.com/s/..."
```

优点：快速、准确、不依赖搜索
缺点：需要手动获取URL

### 方式三：批量URL抓取（推荐已知文章列表）

将多个文章URL放在文件中批量抓取：

1. 创建URL列表文件（如 `urls.txt`）：
```
https://mp.weixin.qq.com/s/...
https://mp.weixin.qq.com/s/...
https://mp.weixin.qq.com/s/...
```

2. 运行批量抓取：
```bash
python scrape_batch.py --file urls.txt
```

优点：批量处理、稳定可靠
缺点：需要预先收集URL

## 详细使用说明

### 方式一：公众号搜索抓取参数

```bash
python run.py [选项]
```

**参数说明**：
- `--account, -a`: **(必需)** 公众号名称
- `--output, -o`: 输出目录 (默认: `articles`)
- `--max-pages, -m`: 最大翻页数 (默认: 10，每页约10篇文章)
- `--include-images`: 保留图片链接 (默认忽略)

**示例**：
```bash
# 基本用法
python run.py --account "中科星图"

# 抓取更多页数
python run.py --account "中科星图" --max-pages 50

# 自定义输出目录
python run.py --account "中科星图" --output ./中科星图文章
```

### 方式二：单篇URL抓取参数

```bash
python scrape_single.py [选项]
```

**参数说明**：
- `--url, -u`: **(必需)** 微信文章URL
- `--output, -o`: 输出目录 (默认: `articles`)
- `--include-images`: 保留图片链接 (默认忽略)

**示例**：
```bash
# 抓取单篇文章
python scrape_single.py --url "https://mp.weixin.qq.com/s?__biz=..."

# 自定义输出目录
python scrape_single.py -u "https://mp.weixin.qq.com/s/..." -o ./my_articles
```

### 方式三：批量URL抓取参数

```bash
python scrape_batch.py [选项]
```

**参数说明**：
- `--file, -f`: **(必需)** URL列表文件路径
- `--output, -o`: 输出目录 (默认: `articles`)
- `--include-images`: 保留图片链接 (默认忽略)

**示例**：
```bash
# 从文件批量抓取
python scrape_batch.py --file urls.txt

# 自定义输出目录
python scrape_batch.py -f urls.txt -o ./中科星图文章
```

## 输出格式

文章将保存为以下格式：

```
articles/
└── 中科星图/
    ├── 文章标题1.md
    ├── 文章标题2.md
    └── ...
```

每篇文章的 Markdown 格式：

```markdown
# 文章标题

**作者**: 作者名称
**发布时间**: 2024-01-01
**原文链接**: https://...

---

文章正文内容...
```

## 技术说明

### 工作原理

1. 通过搜狗微信搜索获取公众号文章列表
2. 遍历文章链接，获取每篇文章的详细内容
3. 使用 BeautifulSoup 解析 HTML 内容
4. 使用 html2text 将 HTML 转换为 Markdown
5. 保存到本地文件

### 依赖库

- `requests`: HTTP 请求
- `beautifulsoup4`: HTML 解析
- `html2text`: HTML 转 Markdown
- `lxml`: XML/HTML 解析器
- `fake-useragent`: 随机 User-Agent

## 注意事项

1. **访问频率限制**：
   - 程序已内置延时机制（每个请求间隔1-2秒）
   - 如遇到反爬虫限制，建议降低 `--max-pages` 参数

2. **搜狗微信搜索限制**：
   - 搜狗微信搜索可能会有访问限制
   - 建议分批次抓取，避免一次性抓取过多

3. **文章链接时效性**：
   - 微信文章链接可能会过期
   - 建议及时保存重要文章

4. **图片处理**：
   - 默认不保存图片链接（使用 `--include-images` 可保留）
   - 图片链接可能失效，建议另行下载图片

## 项目结构

```
.
├── wechat_scraper/
│   ├── __init__.py       # 包初始化
│   ├── scraper.py        # 抓取逻辑
│   ├── parser.py         # Markdown 转换
│   └── main.py           # 主程序
├── run.py                # 快速启动脚本
├── requirements.txt      # 依赖列表
└── README.md             # 说明文档
```

## 常见问题

**Q: 提示"未获取到任何文章"怎么办？**

A: 可能的原因：
- 公众号名称输入错误
- 网络问题或被反爬虫限制
- 搜狗微信搜索暂时不可用

建议：检查公众号名称是否正确，稍后重试

**Q: 能抓取多少篇文章？**

A: 取决于 `--max-pages` 参数，每页约10篇文章。默认10页约100篇。

**Q: 抓取速度很慢？**

A: 为了避免被反爬虫，程序有延时机制。这是正常现象。

## 免责声明

本工具仅供学习交流使用，请遵守相关法律法规和网站使用条款。
使用本工具产生的一切后果由使用者自行承担。

## 开源协议

MIT License

## 作者

Claude Code

## 更新日志

### v1.0.0 (2024-11-20)
- 初始版本发布
- 支持基本的文章抓取功能
- 支持 Markdown 格式转换
