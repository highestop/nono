---
name: download-video
description: 使用 yt-dlp 下载视频/音频，支持解析地址、选择画质、自动合并音视频。适用于 YouTube、B 站、Twitter/X 等主流平台。
---

## 依赖工具

- `yt-dlp`：视频解析与下载
- `ffmpeg`：音视频合并（DASH 格式需要）

在执行任何操作前，先检查依赖是否已安装（`which yt-dlp && which ffmpeg`），缺哪个装哪个，直接 `brew install` 无需询问用户。

## 工作流程

### 1. 解析视频格式

```bash
yt-dlp --list-formats <url>
```

- 如果遇到 412 或认证错误（常见于 B 站），加上 `--cookies-from-browser chrome`
- 如果是短链（如 b23.tv），先用 `curl -sI -o /dev/null -w "%{redirect_url}" <url>` 解析完整地址

### 2. 展示可用画质

将解析结果以表格形式展示给用户，包含：分辨率、帧率、编码格式、预估大小。标注哪些需要会员权限。

### 3. 下载

根据用户选择的画质下载，默认下载到当前工作目录：

```bash
yt-dlp --cookies-from-browser chrome -f "<video>+<audio>" -o "<output_dir>/%(title)s.%(ext)s" <url>
```

- 优先选择 `video+audio` 组合格式让 yt-dlp 自动合并
- 如果视频和音频本身合在一起（如 Twitter），直接用单格式 ID 下载
- 下载大文件时使用 `run_in_background` 避免阻塞

### 4. 合并（仅在需要时）

正常情况下 ffmpeg 已安装，yt-dlp 会自动合并。如果因异常导致产生了分离的音视频文件，自动执行合并并删除临时文件，无需询问用户：

```bash
ffmpeg -i <video_file> -i <audio_file> -c copy <output_file>
rm <video_file> <audio_file>
```

## 注意事项

- 下载目录默认为用户当前工作目录，用户指定其他路径时遵循用户指定
- 如果用户只想获取视频直链而不下载，使用 `yt-dlp -g <url>`
- 如果用户想只下载音频，使用 `yt-dlp -x --audio-format mp3 <url>`
- 部分网站（如 B 站）的高画质视频需要登录账号会员，如果格式列表中缺少高画质选项，提醒用户登录账号
