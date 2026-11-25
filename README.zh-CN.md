# claude-x-gemini

**一个 Claude Code 插件：你在 Claude Code 里点名 Gemini，Gemini 自己读文件、把事情讲给你听；聊清楚后，Claude Code 复核并动手。**

[English](README.md) · **中文** · [▶ 宣传片（36 秒）](#宣传片)

<p align="center">
  <img src="assets/kazik-post.png" alt="@数字生命卡兹克 的帖子：Google：沟通极舒服的模型+审美不错+粗心大意+狗屎的Harness+随便用；Claude：沟通还不错的模型+审美极佳+一般严谨+无敌的Harness+就是不给你用你打我啊略略略。" width="720"><br>
  <sub>出发点是这条判断：<a href="https://x.com/Khazix0918/status/2124680457623425334">@数字生命卡兹克</a>。Gemini 最好聊，Claude 的 Harness 最强。这个插件让两者各做擅长的事。</sub>
</p>

## 30 秒看懂

| | |
|---|---|
| **它是什么** | Claude Code 的一个 skill。它通过 Google 的 Antigravity CLI（`agy`）调用 Gemini。 |
| **解决什么** | 你想把项目弄懂、把想法聊透。Gemini 讲得好，但你不想让它碰代码。 |
| **怎么分工** | Gemini：只读文件，讲解，陪你聊。Claude Code：转交，复核，改代码，跑命令。 |
| **什么时候运行** | 只在你点名 Gemini 时。原因：Gemini 读到的文件会发给 Google。 |
| **需要什么** | Claude Code；`agy` 已登录 Google 账户；Python 3.9+；macOS 或 Linux。 |

## 宣传片

36 秒，有声音。先在 3D 场景里把一次请求走一遍，再进 Claude Code 看真实录屏。

https://github.com/user-attachments/assets/57481c38-c895-4408-a6e7-ff36017b7f11

<sub>播放不了时：[下载 mp4](assets/claude-x-gemini-film-zh.mp4)。</sub>

## 一次请求怎么走

<p align="center">
  <img src="assets/flow-zh.png" alt="五步循环：① 你在 Claude Code 里说“让 Gemini 讲讲这段在做什么”；② Claude Code 把要读的文件交给 Gemini；③ Gemini 的回答“我来给你讲清楚”原样回到你面前，可以接着问；④ 聊清楚后，handoff 交回 Claude Code；⑤ Claude Code 接着做：改好，跑过。" width="100%">
</p>

1. **你说一句。** 在 Claude Code 里点名 Gemini，例如“让 Gemini 讲讲这段在做什么”。
2. **Claude Code 转交。** 它只告诉 Gemini 该读哪些文件，自己不先读。
3. **Gemini 回答你。** 它自己读文件。回答原样到你面前，不经 Claude 压缩。你可以接着问。
4. **Gemini 写 handoff。** 聊清楚后，它写下三件事：你要什么，还没定什么，它自己的建议。
5. **Claude Code 动手。** 它先对照你的原话和文件复核 handoff，再改代码、跑命令。

第 3 步可以重复任意多次。这五步是工具，不是流水线：Claude 可以只用其中一步，也可以随时停。

## 安装

**1. 安装 Antigravity CLI 并登录一次**

```bash
brew install --cask antigravity-cli
```

```bash
agy
```

用 Google 账户登录后退出即可。（Gemini CLI 已不再服务个人账户，所以用 `agy`。）

**2. 在 Claude Code 里安装插件**

```
/plugin marketplace add pursurer/claude-x-gemini
/plugin install claude-x-gemini@claude-x-gemini
```

不用插件市场也可以：把 `skills/claude-x-gemini/` 复制到你项目的 `.claude/skills/`。这个文件夹自成一体。

**3. 检查（可选）**

```bash
python3 skills/claude-x-gemini/scripts/relay.py doctor
```

它检查 `agy`、登录、额度和可用模型，不消耗对话轮次。

## 怎么用

对 Claude Code 说话即可。每句话里要点名 Gemini。

| 你说 | 发生什么 |
|---|---|
| “让 Gemini 讲讲这个仓库是怎么组织的。” | **讲解。** Gemini 读文件并讲解，回答原样交给你。 |
| “问问 Gemini：为什么不在这里加缓存？” | **对话。** 追问在同一段对话里继续。Claude 转述你的意思，补上 Gemini 缺的背景。 |
| “好，取 Gemini 的简报。” | **Handoff。** Gemini 写下你要什么、还没定什么、它的建议。Claude 复核后动手。 |
| “让 Gemini 也独立出一份方案。” | **第二方案。** Gemini 只看你的原话，不看 Claude 的草稿。Claude 合并，并告诉你哪里不同。 |

可选项：

- **讲解风格**（默认关闭，你要求时才开）：`plain`、`eli5`、`feynman`、`expert`，或 `--html` 交互页面。
- **语言**：你和 Claude 用什么语言，Gemini 就用什么语言。
- **项目说明**：在项目根目录放 `.claude-x-gemini.md`（受众、术语、语气），它会附在每次请求后面。
- **输出位置**：`.claude-x-gemini/`。用环境变量 `CLAUDE_X_GEMINI_DIR` 修改。

## 你能得到什么

- **Claude 花很少的 token。** 阅读是 agent 最大的开销。这里由 Gemini 读，Claude 只点名文件。
- **Gemini 的原话。** 讲解不经过 Claude 总结，直接到你手里。
- **复核过的 handoff。** Gemini 粗心，而且说得很笃定。测试中它把峰时说成了半价时段，Claude 的复核查了出来。你的原话永远优先于 Gemini 的总结。
- **Gemini 碰不到你的代码。** 它只读。疑似密钥文件被禁止读取。
- **几乎没有固定 prompt。** Claude 用自己的话写给 Gemini。固定的句子只有四句，每一句都改变过测试结果。

## 和其他做法的区别

| | 单独用 Google 的 CLI（`agy`） | Gemini 给 Claude 打工（其他 `agy` 插件） | **claude-x-gemini** |
|---|---|---|---|
| 你和谁说话 | Gemini | Claude | **弄懂时和 Gemini，干活时和 Claude** |
| 谁改文件 | Gemini，在 Gemini 的 Harness 里 | Gemini，需授予写权限 | **只有 Claude** |
| 谁复核结果 | 你自己 | Claude | **Claude，对照你的原话和文件** |
| 带回给 Claude 什么 | 没有，是另一个会话 | 代码、diff、摘要 | **你要什么、还没定什么、Gemini 的建议，分开写** |

怎么选：

- 想让 Gemini 在 Google 的 Harness 里直接干活：单独用 `agy`。
- 想在写代码上省 Claude 的 token：用打工型插件，例如 [antigravity-for-claude-code](https://github.com/yuting0624/antigravity-for-claude-code)。
- 想和 Gemini 把项目弄懂、把想法聊透，又只让 Claude 碰代码：用 claude-x-gemini。

卡兹克的原话：

> Gemini = 沟通极舒服的模型 + 审美不错 + 粗心大意 + 狗屎的Harness<br>
> Claude = 沟通还不错的模型 + 审美极佳 + 一般严谨 + 无敌的Harness

他的答案是让 Claude 站中间，Gemini 坐在旁边当军师。这个插件照这个思路做。

## 局限与安全

- **Gemini 只读。** 它不能写文件，不能执行命令。它读到的工作区文件会发给 Google。
- **密钥文件。** 每次运行前，插件按精确路径禁止读取疑似密钥文件（`.env*`、私钥、凭据）。原因：Antigravity CLI 1.5.16 的通配符和正则禁止规则在测试中无效。
- **诱饵测试**（agy 1.5.16，2026 年 11 月）：我们放入假密钥，让 Gemini 用所有工具去找。它没有搜索和列目录工具，读 `.env` 被拒绝，没有泄露任何值。以后的 `agy` 如果加入搜索工具，结果可能改变。
- **可用模型取决于套餐。** 2026 年 11 月：学生版 Google AI Pro 在 Antigravity 里只有 Gemini 3.8 Flash；付费 Pro 和 Ultra 可用 Gemini 4 Neon。
- **省 token 的数据不是我们测的。** 它来自一个相关项目在编码任务上的实测：整件事交出去、主控不读材料，成本约 0.58 倍；逐个文件交出去，成本 1.33–1.68 倍（[antigravity-for-claude-code](https://github.com/yuting0624/antigravity-for-claude-code)）。

## 给 Agent 的速查

如果你是读这个仓库的 agent，这一节够用。完整流程在 [`skills/claude-x-gemini/SKILL.md`](skills/claude-x-gemini/SKILL.md)。

- **触发条件**：只在人点名 Gemini 时使用。不要主动调用。
- **入口**：`python3 skills/claude-x-gemini/scripts/relay.py <命令>`，在项目根目录运行。只用 Python 标准库。

| 命令 | 作用 |
|---|---|
| `explain --brief <文件> --slug <主题>` | 把你写的简报交给 Gemini。Gemini 读简报点名的文件并讲解。可加 `--style`、`--html`、`--model`、`--effort`。 |
| `say "<话>"` | 把人的意思送进最近一段对话，打印 Gemini 的回复。`--new` 开新对话。 |
| `handoff` | Gemini 写下人要什么、还没定什么、它的建议。 |
| `models` | 列出这个账户可用的模型。 |
| `doctor` | 检查 `agy`、登录、额度和模型。不消耗轮次。 |

- **你必须做的事**：只点名文件，不要先读；Gemini 的回答原样交给人，不总结、不改写；按 handoff 动手前，先对照人的原话和项目文件复核；两者不一致时，以人的原话为准并询问。
- **输出**：`.claude-x-gemini/`（或 `$CLAUDE_X_GEMINI_DIR`）。
- **失败时**：运行 `doctor`，把结果告诉人。不要自己代写讲解。

## 仓库里有什么

```
.claude-plugin/                  插件与市场清单
skills/claude-x-gemini/          一个自成一体的 skill（Agent Skills 规范）
  SKILL.md                       给 Claude 看的流程
  scripts/relay.py               explain · say · handoff · models · doctor
  assets/handoff.md              唯一固定发给 Gemini 的要求
  assets/styles/*.md             可选讲解风格，每个一行
assets/                          主页图片和宣传片
```

## 致谢

- [@数字生命卡兹克](https://x.com/Khazix0918/status/2124680457623425334)：模型画像，以及“Claude 站中间”的思路。
- [antigravity-for-claude-code](https://github.com/yuting0624/antigravity-for-claude-code)：只读 `agy` 设置与实测数据。
- [Andrej Karpathy](https://x.com/karpathy/status/2105819303471976479)：约 80% 的 ASD-STE100（`plain` 风格）。
- [understanding-ladder](https://github.com/ChangWenC/understanding-ladder)：“不删任何内容”。
- 仓库结构参考：[Agent Skills 规范](https://agentskills.io/specification)、[anthropics/skills](https://github.com/anthropics/skills)、[obra/superpowers](https://github.com/obra/superpowers)、[mattpocock/skills](https://github.com/mattpocock/skills)。
- 流程图里的 Gemini 和 Claude 标志是各自公司的商标，只用来指代产品。
- 宣传片素材：香港城市模型 Jack M Simmons（CC BY）、MacBook 模型 jackbaeten（CC BY），均来自 Sketchfab；高程数据 Terrain Tiles（Mapzen、NASA SRTM）；配乐 Focus Minimal，来自 [huashu-motion](https://github.com/alchaincyf/huashu-motion) 的曲库。

## 许可

[MIT](LICENSE)
