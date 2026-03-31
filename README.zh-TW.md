# responses-third-party-prompt-cache-patch

這是一個可放上 GitHub 的包裝 repo，用來分發 `responses-third-party-prompt-cache-patch` 這個 OpenClaw skill。

這個 skill 會對**已安裝的 OpenClaw `dist/` bundle** 套用一個**本地 patch**，讓第三方 OpenAI-compatible Responses endpoint 不會再被 OpenClaw 剝掉 `prompt_cache_key` 和 `prompt_cache_retention`。

## 直接貼進 OpenClaw

如果你想讓 OpenClaw 直接抓取安裝指南並在目標機器上執行 install/apply workflow，可直接貼這一行：

```text
Fetch and follow instructions from https://raw.githubusercontent.com/tsunheimat/openclaw-responses-prompt-cache-patch/refs/heads/main/.openclaw/INSTALL.md
```

要用 **raw URL**，不是 GitHub `blob/...` 頁面。`.openclaw/INSTALL.md` 已經寫成 OpenClaw 專用執行指南：安裝 skill、跑 dry-run、套用 patch、重啟 gateway、回報結果。

## 適合誰使用

如果你符合以下情況，這個 repo 適合你：

- 你在自己的機器或伺服器上運行 OpenClaw
- 你使用第三方 OpenAI-compatible Responses endpoint
- 你需要讓 prompt-cache 相關欄位穿過 OpenClaw bundle layer
- 你可以接受對已安裝的 OpenClaw `dist/` 檔案做本地 patch

如果你想要的是以下其中一種，這個 repo **不適合**：

- 上游 OpenClaw 原始碼修復
- 純 config 解法
- 已發布 marketplace / registry 安裝流程

## Repo 內容

```text
.
├── .openclaw/INSTALL.md
├── .gitignore
├── README.md
├── README.zh-TW.md
└── skill/
    └── responses-third-party-prompt-cache-patch/
        ├── SKILL.md
        └── scripts/
            ├── _bundle_patch_common.py
            ├── patch_prompt_cache.py
            └── revert_prompt_cache.py
```

repo 根目錄放的是對外說明文件；可安裝的 skill 內容則維持在 `skill/responses-third-party-prompt-cache-patch/` 之下，方便之後獨立封裝或分發。

## 其他文件

- 技術說明：[`docs/TECHNICAL-OVERVIEW.md`](docs/TECHNICAL-OVERVIEW.md)
- 免責聲明：[`docs/DISCLAIMER.md`](docs/DISCLAIMER.md)

## 重要風險

- apply script 會直接寫入已安裝的 OpenClaw `dist/` 目錄
- 這是**本地 patch**，不是上游正式修復；升級或重裝 OpenClaw 後，可能需要重新套用
- apply 或 rollback 後都必須重啟 gateway：
  ```bash
  openclaw gateway restart
  ```
- 只把 skill 資料夾複製進去，**不代表 patch 已啟用**；你必須實際執行 apply script

## 安裝到另一台 OpenClaw 機器

1. 先把這個 repo 帶到目標機器上。若你是在 GitHub 上看這個 repo，可以用 **Code → Download ZIP**、用頁面上的實際 URL `git clone`，或用 `scp` / `rsync` 複製既有 checkout。
2. 在 clone 或解壓後的 repo 根目錄，把 skill 複製到 OpenClaw workspace skills 目錄：
   ```bash
   mkdir -p ~/.openclaw/workspace/skills
   cp -R ./skill/responses-third-party-prompt-cache-patch ~/.openclaw/workspace/skills/
   ```
3. 進入安裝好的 skill 目錄：
   ```bash
   cd ~/.openclaw/workspace/skills/responses-third-party-prompt-cache-patch
   ```
4. 先做 dry-run：
   ```bash
   python3 scripts/patch_prompt_cache.py --dry-run
   ```
5. 正式套用 patch：
   ```bash
   python3 scripts/patch_prompt_cache.py
   ```
6. 重啟 OpenClaw Gateway：
   ```bash
   openclaw gateway restart
   ```

如果你想看 OpenClaw 專用、可直接執行 install/apply 的指南，可參考 [`.openclaw/INSTALL.md`](.openclaw/INSTALL.md)。

Raw URL：
`https://raw.githubusercontent.com/tsunheimat/openclaw-responses-prompt-cache-patch/refs/heads/main/.openclaw/INSTALL.md`

## Apply / rollback 指令

請在已安裝的 skill 目錄內執行：

```bash
cd ~/.openclaw/workspace/skills/responses-third-party-prompt-cache-patch
python3 scripts/patch_prompt_cache.py --dry-run
python3 scripts/patch_prompt_cache.py
openclaw gateway restart
```

Rollback：

```bash
cd ~/.openclaw/workspace/skills/responses-third-party-prompt-cache-patch
python3 scripts/revert_prompt_cache.py
openclaw gateway restart
```

## 分發說明

- 這個 repo 的定位是乾淨、可直接放 GitHub 的分發包裝層
- 如果之後這個 skill 發到 ClawHub，那會是另一條安裝路徑；但這個 repo 仍可作為手動安裝 fallback 與較接近 source-of-truth 的分發方式
- patch 和 rollback 的核心邏輯都保留在 skill scripts 內；這個 repo 不改變它們的行為
