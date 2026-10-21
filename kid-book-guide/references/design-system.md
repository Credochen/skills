# 设计系统：浅色童趣风单页导读

目标观感：**奶油色纸张 + 粉彩贴纸 + 手绘感插画**。不用深色底、不用玻璃拟态、不用渐变文字。
所有页面必须**单文件、零外部依赖**（便于离线双击打开、便于发给家长）。

## 一、设计令牌

```css
:root{
  /* 纸张与文字 */
  --cream:#FFFBF3;   --paper:#FFFFFF;
  --ink:#33305A;     --ink-soft:#6C688E;   --ink-faint:#9A96B4;
  --line:#EDE4D5;    --dark:#3B3563;

  /* 五个粉彩色（卡片底色用 *-soft，文字用主色） */
  --purple:#7C6BFF;  --purple-soft:#EFEBFF;
  --orange:#FF9E3D;  --orange-soft:#FFF0DE;
  --pink:#FF7EA8;    --pink-soft:#FFE9F0;
  --teal:#2FC5AB;    --teal-soft:#E2FAF5;
  --yellow:#FFC93C;  --yellow-soft:#FFF6DA;

  --radius:26px;
}
```

- 正文字号 `16.5px / 1.9`（童书排版要松），窄屏降到 `16px`。
- 容器 `.wrap{max-width:1060px;padding:0 22px}`。
- 板块间距 `section{padding:46px 0 6px}`。
- 字体栈固定：`"PingFang SC","Hiragino Sans GB","Source Han Sans SC","Microsoft YaHei",system-ui`。**不要引用网络字体。**
- 页面底色 = 3 个大半径径向渐变（暖黄/淡紫/淡青，透明度 .09–.16）+ 26px 点阵网格。这是"纸张感"的来源，别删。

## 二、每册一套主色（系列感靠这个）

只换"主色 + 主色软底"，其余令牌不动，读者一眼就知道是同一套书。

| 册 | 主色 | 软底 | 辅助 | 气质 |
|---|---|---|---|---|
| Ⅰ | `#7C6BFF` 紫 | `#EFEBFF` | 粉 | 好奇、谜团 |
| Ⅱ | `#2F7A63` 墨绿 | `#E4F5EE` | 紫 | 森林、博弈 |
| Ⅲ | `#B2832C` 暗金 | `#FBF0D4` | 紫 | 时间、告别 |
| Ⅳ（备用）| `#2B6CB0` 海蓝 | `#E3F0FB` | 青 | 远航、冷静 |

换色要改的位置：封面 `kicker` 渐变、`h1 .hl` 高亮、`section .title h2` 高亮渐变（可保持不变）、`acts` 第 N 幕圆点、`details.beat[open]` 边框、`.bno` 底色、`.top` 按钮色。
**高亮条统一用黄→粉渐变**，不随主色变——这是全系列的视觉签名。

模板默认主色是暗金。**换色不能只改 4 个变量**，还有 7 处硬编码的颜色（渐变与投影）。以"暗金 → 墨绿"为例，完整替换清单（共 11 处，缺一处就会露出旧色）：

```
--gold:#B2832C                              → #2F7A63
--gold-deep:#8A621A                         → #22604D
--gold-soft:#FBF0D4                         → #E4F5EE
--gold-line:#EBD6A5                         → #C6EBDF
linear-gradient(120deg,#8A621A,#D3A94F)     → 120deg,#22604D,#5FB99B   （封面 kicker）
rgba(138,98,26,.26)                         → rgba(47,122,99,.26)      （kicker 投影）
rgba(178,131,44,.16)                        → rgba(47,122,99,.14)      （封面投影）
rgba(178,131,44,.09)                        → rgba(47,122,99,.08)      （.tale 投影）
rgba(178,131,44,.14)                        → rgba(47,122,99,.14)      （2 处：beat[open] / finale）
#E7D3A8                                     → #C6EBDF                   （beat[open] 边框）
color:#8A621A                               → color:#22604D            （finale .q）
```

用 Python `str.replace` 一次性处理，替换后统计每处命中次数（都应为 1，`rgba(178,131,44,.14)` 为 2），再截图确认封面胶囊不再是金色。

已实战验证的另一套：**海蓝**（用于《小王子》，单本非系列）——
`--gold:#2B6CB0` / `--gold-deep:#1F4E7F` / `--gold-soft:#E3F0FB` / `--gold-line:#BFD9F0`，
渐变 `linear-gradient(120deg,#1F4E7F,#5C9BD6)`，三处投影 `rgba(43,108,176,.26/.14/.08)`，边框 `#BFD9F0`。
替换点的**结构**（11 处）不变，只换右列颜色即可。

## 三、组件清单（模板里都有）

| 类名 | 用途 | 关键点 |
|---|---|---|
| `.hero` + `.cover svg` | 封面 | SVG 场景 `viewBox="0 0 1000 300~330"`，圆角 30，投影柔和 |
| `.oneline .card.c1/.c2/.c3` | 三句话 | 恰好 3 张，粉彩底；也常被借去讲"三个步骤/三堂课"（如狐狸的三堂课） |
| `.people > .person` | 人物档案 | `--accent` 传色；emoji 头像 52px；`.say` 是台词气泡（带引号伪元素） |
| `.graph` + `.graph .cap` | SVG 图容器 | 图注格式 `图 N · 一句话结论` |
| `.acts > .act` | 五/六幕时间线 | 竖向虚线 + 圆点，`:nth-child(n)` 依次换色（最多 6 种） |
| `details.beat` | 章节折叠卡 | `.bno` 编号、`.key` 标签（"发生什么"青/"为什么重要"橙）、箭头旋转 |
| `.wiki .card` | 小百科 | 每张结尾 `.tip` 一行生活类比 |
| `.wfgrid > .wf` | 特殊档案（如面壁者） | `::after` 大问号水印 + `.wfribbon` 结论条 |
| `.tales > .tale` | 童话/隐喻卡 | 右上角圆形序号 + `.ans` 谜底块 |
| `.fgrid` + `.fres` | 公式推导 | 2×2 条件卡 → 箭头 → 暖黄结论卡（窄屏自动 1 列） |
| `.tablewrap > table` | 对比表 | **必须包 wrapper**，`min-width` 让它在窄屏内部滚动 |
| `.quotes` | 金句 | 唯一允许的深色卡（星空点阵），3–5 句 |
| `.think .qitem2` | 讨论题 | 圆形数字 + 虚线卡 |
| `.words .word` | 小词典 | `<dl>` 结构，`em` 放类别 |
| `.finale` | 终章特写 | 玻璃球 + 一句提问，只用在结局 |
| `.trilogy .tl` | 系列导航 | 当前册用 `.now` 且不可点 |
| `.parent` | 给家长 | 暖渐变底，`routes` 三种读法 |
| `.top` | 回到顶部 | `scrollY>600` 显示 |

## 四、组件怎么选（避免"信息塞进 SVG"）

| 信息形态 | 用什么 | 不要用什么 |
|---|---|---|
| 文字多、需要阅读 | HTML 卡片 / 折叠卡 | SVG `<text>` |
| 空间关系、角色连线 | SVG 放射图（≤6 节点） | 长表格 |
| 步骤、时间顺序 | `.acts` 或横向流程 SVG（≤5 步） | 嵌套列表 |
| 两个概念的差异 | 表格 | 两段长文字 |
| 形态变化（前后对比）| 左右并置 SVG | 文字描述 |
| 四条件推一结论 | `.fgrid` + `.fres` | 一段话 |

判定规则：**这张图在 375px 宽的手机上，最长的文字会不会小于 9px？会，就改用 HTML 组件。**
（SVG 整体按宽度缩放，`viewBox` 宽 700 的图在 340px 容器里只剩 0.48 倍，18px 字变 8.6px。）

## 五、已知坑与修法（全部踩过）

1. **标题高亮条消失**：`h2::after{z-index:-1}` 会被 `body` 背景挡住。
   → 改用 `h2{display:inline-block;background-image:linear-gradient(90deg,#FFE9A8,#FFD0DF);background-size:100% 12px;background-position:0 88%;background-repeat:no-repeat;}`。
   深色卡（`.quotes`）里要覆盖成 `background-image:none`。
2. **卡片右上角水印压住标题**：`.wf::after` 的大问号会盖住身份文字。
   → 给 `.wfhead{padding-right:38px}`，水印色降到 `#F6F2FF`。
3. **整页横向溢出**：`table{min-width:620px}` 没包 `.tablewrap{overflow-x:auto}`。
   修好后 `document.documentElement.scrollWidth === clientWidth`。
4. **截图右侧被裁**：macOS headless Edge 的 `--window-size=1200` 实际 `clientWidth≈1263`。
   → 截图宽度按 `clientWidth` 给（如 `--window-size=500,...` 看手机版），或先量再截。
5. **中文路径 file:// 打不开**：`"file://$src"` 变量拼接会失败（页面变成目录列表）。
   → 直接写字面量绝对路径，或先 URL 编码。
6. **首个折叠卡全关**：读者不知道能点。
   → 载入时 `document.querySelector('details.beat').open = true`。
7. **`details` 里的标签和正文错位**：`.key` 是 inline 时正文会绕到标签下方。
   → `p{display:flex;gap:9px}` + `.key{flex:0 0 auto;margin-top:4px}`。
8. **emoji 当图标但不显示**：某些系统字体缺失会显示豆腐块。
   → 关键信息不要只靠 emoji 承载，一律配文字。
9. **封面插画的主体在手机上糊成一小团**：`viewBox` 宽 1000 时，若主体（人/猫/船）只有 40px 高，在 350px 宽的手机上只剩 14px，等于消失。
   → 主体高度按 `viewBox` 1000 基准做到 **≥ 60px**；已经画小了就用 `<g transform="translate(x,y) scale(1.4)">` 单独放大，并同步调整它脚下的地面/石头，别让主体悬空或压住文字。

## 六、无障碍与礼貌

- 每张 SVG 加 `role="img"` 与 `aria-label="一句话描述画面"`。
- 所有正文对比度 ≥ 7:1（`--ink` on `--cream` 达标；**不要**用 `--ink-faint` 写正文，只用于注释/图注）。
- `.say` 的引号由伪元素生成，原文里不要再写一遍引号。
- 中文引号用「」或""，代码/属性里只用 ASCII 引号。

## 七、验证流程（三件套）

```bash
# 1) 结构与链接自检（见 scripts/check_page.py）
python3 ~/.workbuddy/skills/kid-book-guide/scripts/check_page.py /abs/path/page.html

# 2) 桌面端首屏截图
"/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
  --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
  --virtual-time-budget=2500 --window-size=1200,2600 \
  --screenshot=/tmp/p_top.png "file:///abs/path/page.html"

# 3) 手机端
".../Microsoft Edge" --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
  --virtual-time-budget=2000 --window-size=500,2200 \
  --screenshot=/tmp/p_m.png "file:///abs/path/page.html"
```

要看页面中段（截图只能拍首屏）时，复制一份临时文件把前面的 section 隐藏：

```python
css = '<style>.hero,#oneline,#people{display:none !important;}</style>'
open('/tmp/preview.html','w').write(html.replace('</head>', css+'\n</head>'))
```

**目视检查清单**：标题高亮条在不在 · 中文有没有被截断 · SVG 文字是否可读 · 卡片水印有没有压字 · 表格是否内部滚动 · 深色卡文字是否为浅色 · 页脚正常收尾。
