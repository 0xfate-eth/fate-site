# Fate — personal website

Fate 的个人网站：[0xfate.me](https://0xfate.me/) · [繁體中文](https://0xfate.me/zh-index.html) · [English](https://0xfate.me/index.html)

网站源码保存在本仓库，使用 Python 生成中英文静态页面，并通过 GitHub Pages 发布。

## 源码与文件

| 文件 | 用途 |
| --- | --- |
| `site-data.json` | 中英文页面内容、案例、思考和时间轴 |
| `site-build.py` | 生成页面及相关资源 |
| `build.py` | 正式版本构建入口 |
| `site-source.css`、`site.js` | 样式与交互 |
| `site-contact.json` | 现有公开联系邮箱的编码 |
| `v4-*.jpg`、`avatar.jpg`、`og.png` | 案例图片、头像和分享图片 |
| `.github/workflows/build.yml` | 自动构建流程 |
| `content/banned_words.txt` | 构建时使用的现有内容检查清单 |

根目录的 HTML、`styles.css`、`feed.xml`、`sitemap.xml` 和 `robots.txt` 是生成文件。旧版单页使用的 `content/site.json`、`content/site.zh.json` 和 `src/index.template.html` 保留作历史文件，不是当前多页面网站的内容源。

## 本地预览

需要 Python 3.12 或更新版本，不需要安装额外 Python 包。在仓库目录运行：

```bash
python3 -B site-build.py --output /tmp/fate-site-preview
python3 -B -m http.server 8767 --bind 127.0.0.1 --directory /tmp/fate-site-preview
```

浏览器打开 `http://127.0.0.1:8767/zh-index.html` 或 `http://127.0.0.1:8767/index.html`。预览版本带有预览标记，并禁止搜索引擎收录。

## 构建与部署

在仓库目录执行 `python3 -B build.py`，会在仓库根目录生成正式版页面及资源。`main` 分支的相关源码变更会触发 [GitHub Actions](https://github.com/0xfate-eth/fate-site/actions) 构建；GitHub Pages 从该分支发布网站。提交后需分别查看该次构建、Pages 部署及线上页面。

读取公开仓库不需要登录。修改仓库需要当前工具具备该仓库的写入权限；浏览器登录状态与其他 AI 工具或命令行的授权不一定共享。
