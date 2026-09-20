# fate-site — 个人公开站点

> 读法：第一次部署看 §1（10 分钟）；以后每次更新只看 §2（1 分钟）；§3 是站点结构，改设计时才看。

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

## 2. 以后怎么更新（自动更新的机制）

**内容源 = `content/site.json`。** 三种更新方式，由轻到重：

| 场景 | 做法 |
|---|---|
| 加一条「更新记录」（Updates 区）| `python3 add_update.py "标题" "一句话说明"` → `./publish.sh` |
| 季度复跑地图后改评分、工作流、成果 | 直接编辑 `content/site.json` 对应字段 → `./publish.sh` |
| 加职业背景 / 自媒体链接 | 编辑 `about.links`（`[{"label":"LinkedIn","url":"..."}]`）→ `./publish.sh` |
| 改中文版 | 编辑 `content/site.zh.json`（**写简体即可**，构建时 OpenCC 自动转繁体；结构、条数必须与英文版一致，不一致会拒绝构建）。首次需 `pip3 install opencc-python-reimplemented` |
| 换头像 | 覆盖根目录 `avatar.jpg`（正方形，≥320px）|

`publish.sh` 做四件事：构建 → 有改动才 commit → push → 写 `publish.log`。没改动时静默退出，所以**可以挂到定时任务每天跑一次**，只要 json 变了站点就自动更新（launchd 示例在 `launchd/` 目录，装完必须看 `publish.log` 有没有「checked」行才算跑起来了）。

`build.py` 的三道闸，任一不过就不出文件：
- `content/banned_words.txt` 里的公司/产品/竞品名出现在内容里 → 拒绝构建（脱敏保险丝，可自行加词）
- 总分与五维均值差 > 0.15 → 拒绝（防止只改一处）
- 日期格式、site_url 末尾斜杠

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
