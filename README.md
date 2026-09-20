# fate-site — 个人公开站点

> 读法：**平时只看 §2**（怎么在 GitHub 上改）；§1 是首次部署记录、已完成；§3 是站点结构，改设计时才看。

对外内容全部来自 `content/site.json`，页面、RSS、sitemap、分享图都由 `build.py` 生成。**改内容只改 json，不直接改 index.html**（会被下次构建覆盖）。

## 1. 首次部署到 GitHub Pages（一次性，约 10 分钟）

1. 在 github.com 新建一个**公开**仓库，名字建议 `fate-site`（不要勾选 README/.gitignore）。
2. 打开终端，进入本文件夹，执行：
   ```bash
   cd "本文件夹路径"
   git init -b main
   git config user.name "Fate"
   git config user.email "你的 GitHub 邮箱"
   git add -A
   git commit -m "launch"
   git remote add origin https://github.com/<你的用户名>/fate-site.git
   git push -u origin main
   ```
   ⚠️ 终端里**不要连注释一起粘**（zsh 会把 `#` 后面的字当参数），一行一行贴。用 SSH 的话把地址换成 `git@github.com:<你的用户名>/fate-site.git`。
3. 仓库页 → Settings → Pages → Build and deployment：Source 选 **Deploy from a branch**，Branch 选 **main / (root)** → Save。约 1 分钟后站点上线：`https://<你的用户名>.github.io/fate-site/`
4. 把这个网址填进 `content/site.json` 的 `meta.site_url`（**末尾要带 `/`**）和 `robots.txt`，然后 `./publish.sh "set site url"`。
5. （可选）绑自己的域名：Pages 页面填 Custom domain，并按提示在域名商加 CNAME 记录；填完后把 `site_url` 改成新域名再发布一次。

## 2. 以后怎么更新（全部在 GitHub 网页上完成，本地不需要任何东西）

**内容源 = `content/site.json`（英文）+ `content/site.zh.json`（中文，写简体）。**
在 github.com 打开文件 → 铅笔图标编辑 → Commit changes。**提交后约 1–2 分钟站点自动更新**：`.github/workflows/build.yml` 会在云端跑 `build.py`，把生成的 `index.html / feed.xml / sitemap.xml / og.png` 提交回仓库，GitHub Pages 随即重发布。进度看仓库的 **Actions** 页；绿勾 = 已上线，红叉 = 内容没过闸（点进去看原因，通常是 JSON 少个逗号或中英条数不一致），**站点保持上一版不变**。

| 场景 | 在 GitHub 上改哪里 |
|---|---|
| 加一条「更新记录」（Updates 区） | `content/site.json` → `updates` 数组末尾加一项 `{"date","title","note"}`，并把 `meta.data_date` 改成同一天；中文版在 `site.zh.json` 同位置加一项 |
| 季度复跑后改评分、工作流状态、成果清单 | `content/site.json` 对应字段（`score`、`workflows[].status`、`outputs`）；中文版同步 |
| 加职业背景 / 自媒体链接 | `content/site.json` → `about.links`：`[{"label":"LinkedIn","url":"..."}]` |
| 换头像 | 仓库根目录上传新的 `avatar.jpg` 覆盖（正方形，≥320px） |
| 改设计 | `src/index.template.html`（样式、交互全在这一个文件） |
| 加新页面 | 在 `src/` 加新模版并在 `build.py` 里加一行输出；或直接在根目录放一个独立 `xxx.html` |

三道闸（任一不过就不出文件、站点不变）：`content/banned_words.txt` 里的公司/产品/竞品名出现在内容里 · 总分与五维均值差 > 0.15 · 中英 JSON 结构或条数不一致。

**本地脚本仍可用但不必须**：`publish.sh` / `launchd/` 是给"在本机批量改完再推"的场景，前提是本机配好了 GitHub 登录；平时用不到。

## 3. 站点结构

```
content/site.json          唯一内容源（英文、已脱敏）
content/banned_words.txt   脱敏禁用词
src/index.template.html    页面模版（设计、样式、交互全在这一个文件）
build.py                   json + 模版 → index.html / feed.xml / sitemap.xml / og.png
add_update.py              往 Updates 追加一条并更新数据日期
publish.sh                 构建 + 提交 + 推送（无改动则跳过）
index.html feed.xml sitemap.xml og.png    生成物，勿手改
.nojekyll robots.txt       GitHub Pages 所需
```

页面分区：Hero（定位一句话 + 季度评分卡）→ 数字条 → I Verdict → II Platform（10 条工作流）→ III Knowledge → IV Work（例行任务 + 成果）→ V Updates（RSS）→ VI About（原则 + 简介 + 链接位）。

设计：纸感编辑风。纸白 `#F4F1EA` / 墨黑 `#17171A` / 朱红 `#C8412B`；标题 Fraunces、正文 Inter、标注 JetBrains Mono；自动深色模式；`/` 键全页过滤；手机端自适应。
