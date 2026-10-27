---
name: ffmpeg
description: "Use when converting, cutting, stitching or streaming video/audio from the command line — ffmpeg -i / -ss / -t, fps and scale filters, CRF and preset for H.264/H.265, -hwaccel decoding, hls muxer with hls_time and hls_segment_filename, RTSP/UDP ingestion, frame extraction for textures. FFmpeg 9.0.2. Also for \"moov atom not found\", non-monotonic DTS warnings, colour shifts from missing -pix_fmt/-color_range, and ffprobe checks before batch jobs."
tags:
  - ffmpeg
  - video
  - transcode
  - hls
  - rtsp
  - gis
  - cli
---

> **官网：** <https://ffmpeg.org/>
>
> **官方文档：** <https://ffmpeg.org/ffmpeg.html>（滤镜 <https://ffmpeg.org/ffmpeg-filters.html>，封装格式 <https://ffmpeg.org/ffmpeg-formats.html>）
>
> **下载：** <https://ffmpeg.org/download.html>（源码与各平台静态构建）
>
> **包管理器：** `apt install ffmpeg` / `brew install ffmpeg` / `winget install Gyan.FFmpeg` / 官方静态包（最新 9.0.2，截至 2026-10）
>
> **版本：** 9.0.2（`release/9.0` 分支的最新补丁版）；上一分支 8.1.3，更早 7.1.x | 上游无 GitHub Release tag，版本以 <https://ffmpeg.org/releases/> 与 RELEASE_NOTES 为准
>
> **许可证：** LGPL-2.1-or-later（默认）；若构建启用了 `--enable-gpl` 且实际用到 GPL 部分（如 libx264/libx265），整个 FFmpeg 转为 GPL-2.0-or-later——多数发行版与「full build」静态包属于后者，商用集成前先看 `ffmpeg -version` 的构建配置

## 概述

FFmpeg 是一套处理音视频的命令行工具与库：`ffmpeg` 转码/裁剪/拼接/推流，`ffprobe` 只读探测，`ffplay` 预览。它不做创意编辑，而是把「解码 → 滤镜链 → 编码」这条流水线暴露成参数，适合放进脚本、CI 与批处理。对 GIS/三维场景而言，它最常见的角色是把视频变成「可以计算的东西」：帧序列、纹理、切片、时间戳对齐的影像源。

核心概念只有四个：

- **输入输出**：`-i` 声明输入，其余裸参数是输出文件；一个命令可以有多个输入与输出
- **流选择**：`-map` 决定哪些流进入哪个输出（默认每种类型只取一路）
- **滤镜链**：`-vf`（视频）/`-af`（音频）/`-filter_complex`（多输入），用逗号串联
- **编解码参数**：`-c:v` / `-crf` / `-preset` / `-pix_fmt` 决定画质与体积

## 安装

### 包管理器（推荐，最省事）

```bash
# Debian / Ubuntu
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows（winget）
winget install Gyan.FFmpeg
```

### 官方静态构建 / 源码

```bash
# 下载页提供各平台静态包（含完整编码器），解压后把 bin 加入 PATH
# https://ffmpeg.org/download.html

# 源码编译（裁剪出自定义编解码集）
./configure --prefix=/usr/local --enable-gpl --enable-libx264 --enable-libx265
make -j$(nproc) && sudo make install
```

### 验证

```bash
ffmpeg -version        # 第一行含版本与构建配置
ffprobe -version
ffmpeg -hide_banner -encoders 2>/dev/null | grep -E 'libx264|libx265|aac'
ffmpeg -hide_banner -hwaccels    # 列出本机可用的硬件加速后端
```

## 核心命令

### 探测：先 ffprobe 再动手

批处理前永远先探测，避免用错帧率、色彩或时长：

```bash
# 一行摘要（分辨率/编码/帧率/时长）
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,codec_name,duration \
  -of default=noprint_wrappers=1 input.mp4

# JSON（便于脚本消费）
ffprobe -v error -print_format json -show_format -show_streams input.mp4
```

### 裁剪与切段

```bash
# -ss 放在 -i 前 = 快速定位（关键帧级），放后 = 精确但慢
ffmpeg -ss 00:01:30 -i input.mp4 -t 30 -c copy clip.mp4

# 精确到帧（重新编码）
ffmpeg -i input.mp4 -ss 00:01:30 -t 30 -c:v libx264 -crf 20 out.mp4
```

`-c copy` 不重编码，几十秒就能切完几 GB 的文件；但切点会吸附到关键帧，起点可能比预期早几帧。需要帧级精度时只能重编码。

### 抽帧做纹理 / 序列

```bash
# 每秒 1 帧，输出 PNG 序列（GIS 里做纹理或全景源）
ffmpeg -i input.mp4 -vf fps=1 frames/%06d.png

# 指定区间抽帧，并统一缩放到 2048 宽
ffmpeg -ss 00:00:10 -i input.mp4 -t 20 -vf "fps=2,scale=2048:-2" frames/%06d.jpg

# 只抽关键帧（I 帧），常用于粗览
ffmpeg -i input.mp4 -vf "select='eq(pict_type,I)'" -fps_mode passthrough keyframes/%06d.jpg
```

`scale=2048:-2` 里的 `-2` 让高度自动取偶数——编码器对奇数尺寸会报错，这是最常见的一次性踩坑。

### 转码与画质（CRF）

```bash
# H.264：CRF 越小越清晰、体积越大（18–28 是常用区间）
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium -pix_fmt yuv420p out.mp4

# H.265：同画质约省 30–50% 体积，但兼容性与编码耗时更差
ffmpeg -i input.mp4 -c:v libx265 -crf 28 -preset medium -tag:v hvc1 out.mp4

# 两遍定码率（需要严格控制文件大小或上传带宽时）
ffmpeg -i input.mp4 -c:v libx264 -b:v 4M -pass 1 -an -f null /dev/null
ffmpeg -i input.mp4 -c:v libx264 -b:v 4M -pass 2 -c:a aac -b:a 128k out.mp4
```

| 参数 | 作用 | 常用取值 |
|------|------|---------|
| `-crf` | 恒定质量，数值越小越清晰 | H.264 18–28；H.265 加 4–6 |
| `-preset` | 编码速度/压缩率权衡 | `ultrafast` … `veryslow` |
| `-pix_fmt` | 像素格式 | `yuv420p`（兼容性最好） |
| `-movflags +faststart` | 把 moov 移到文件头，边下边播 | 网络分发必加 |
| `-an` / `-vn` | 丢弃音频 / 视频 | 只取一路时 |

### 硬件加速解码

```bash
# 自动选择后端（NVIDIA/Intel/AMD 各自的 hwaccel 名称不同）
ffmpeg -hwaccel auto -i input.mp4 -c:v libx264 -crf 23 out.mp4

# 明确指定（示例：NVDEC）
ffmpeg -hwaccel cuda -i input.mp4 -c:v libx264 -crf 23 out.mp4
```

`-hwaccel` 是**输入侧**选项，只影响解码。官方文档明确写着：多数加速方式是为播放设计的，在现代 CPU 上未必比软件解码快，还要把帧从显存拷回内存——**它主要适合测试，不是默认的生产加速手段**。真正的端到端加速要用硬件编码器（如 `h264_nvenc` / `hevc_nvenc` / `h264_qsv`），代价是画质曲线与软件编码不同。

### 拼接

```bash
# 同一编码参数的分段：用 concat demuxer（快，不重编码）
printf "file '%s'\n" part1.mp4 part2.mp4 > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c copy joined.mp4

# 参数不一致：先用 concat 滤镜统一重编码
ffmpeg -i a.mp4 -i b.mp4 -filter_complex \
  "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 23 joined.mp4
```

`concat` demuxer 要求各段编码参数完全一致（分辨率、帧率、时基），否则会出现音画漂移或解码失败；不一致就退回 concat 滤镜。

### 切片（HLS）

```bash
# 生成 6 秒切片 + m3u8 播放列表
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -c:a aac -b:a 128k \
  -f hls -hls_time 6 -hls_playlist_type vod \
  -hls_segment_filename "out/seg_%03d.ts" out/index.m3u8
```

常用 HLS 参数：`-hls_time`（切片时长）、`-hls_list_size`（列表保留条数，0 表示全部）、`-hls_playlist_type vod|event`、`-hls_segment_filename`（切片命名模板）。直播场景把 `-hls_playlist_type` 换成 `event` 或省略，并配 `-hls_flags delete_segments`。

### 拉流与转推

```bash
# RTSP 摄像头存一段（UDP 优先，丢包就降级 TCP）
ffmpeg -rtsp_transport tcp -i rtsp://user:pass@host:554/stream -t 60 -c copy cam.mp4

# 拉流转 HLS（低延迟直播常用）
ffmpeg -rtsp_transport tcp -i rtsp://host/stream \
  -c:v libx264 -preset veryfast -tune zerolatency -g 50 \
  -f hls -hls_time 2 -hls_list_size 6 -hls_flags delete_segments live/index.m3u8

# 转推到 RTMP
ffmpeg -re -i input.mp4 -c copy -f flv rtmp://host/live/stream
```

`-re` 让输入按原始帧率读取（不加会把文件用最快速度推完）。`-g 50` 控制 GOP 长度，直播切片需要关键帧密度与切片时长匹配。

### 全景 / 等距柱状投影

GIS 与三维场景里常要把全景视频拆成可用素材。`v360` 滤镜可以在等距柱状（`e`）与立方体贴图（`c3x2` / `c6x1` / `c1x6`）之间互转，也能按视场角裁出正视画面：

```bash
# 等距柱状 → 立方体贴图（3x2 布局，输出 6 个面拼成一张图）
ffmpeg -i equirect.mp4 -vf "v360=e:c3x2" cubemap.mp4

# 等距柱状 → 指定朝向的透视画面，便于做纹理对齐
ffmpeg -i equirect.mp4 -vf "v360=e:flat:h_fov=90:v_fov=90:yaw=45:pitch=10" flat.mp4
```

具体参数名与取值范围以 `ffmpeg-filters.html` 的 v360 章节为准（各版本有过增补），批量处理前先用一两帧试参数。

## 典型工作流

### 工作流一：把无人机视频变成 GIS 可用的帧序列

**输入**：一段 4K、25fps、含 GPS 旁注的巡检视频。**输出**：`frames/` 下按序号命名、尺寸统一、色彩可控的 JPEG 序列，供摄影测量或纹理贴图使用。

```bash
# 1. 先探测：确认帧率与色彩，别假设
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,pix_fmt,color_range \
  -of default=noprint_wrappers=1 inspection.mp4

# 2. 每 0.5 秒一帧（fps=2），限制在有效区间，转 sRGB 友好的 yuv420p
ffmpeg -ss 00:00:05 -i inspection.mp4 -t 120 \
  -vf "fps=2,scale=3840:-2" -q:v 2 -pix_fmt yuvj420p frames/%06d.jpg

# 3. 核对数量与尺寸（应为 240 张）
ls frames | wc -l
ffprobe -v error -show_entries stream=width,height -of csv=p=0 frames/000001.jpg
```

要点：`-q:v 2` 是 MJPEG 质量（2 接近无损），比默认值大很多但适合后续重建；抽帧数量要跟摄影测量的重叠度匹配，先小批试跑再全量。

### 工作流二：给三维场景做一段可流式播放的 HLS 预览

**输入**：一段几分钟的演示视频。**输出**：`out/index.m3u8` + `seg_000.ts…`，可直接扔到 Nginx/对象存储给播放器用。

```bash
# 1. 统一成 H.264 + AAC、yuv420p（浏览器兼容性最好）
ffmpeg -i demo.mov -c:v libx264 -crf 23 -preset medium -pix_fmt yuv420p \
  -c:a aac -b:a 128k -movflags +faststart demo.mp4

# 2. 切片
ffmpeg -i demo.mp4 -c copy -f hls -hls_time 6 -hls_playlist_type vod \
  -hls_segment_filename "out/seg_%03d.ts" out/index.m3u8

# 3. 抽查切片与列表是否自洽
head -20 out/index.m3u8
ffprobe -v error -show_entries format=duration -of csv=p=0 out/seg_000.ts
```

## 最佳实践

1. **先 `-ss` 后 `-i`**：需要快就用输入侧定位 + `-c copy`；需要精确再把 `-ss` 放输出侧并重编码。
2. **网络分发必加 `-movflags +faststart`**：否则要下完整个文件才能播。
3. **`-pix_fmt yuv420p` 是兼容性保险**：很多播放器/浏览器不吃 `yuv444p` 或 10bit。
4. **别迷信 `-hwaccel`**：它只加速解码，官方文档说多数后端是为播放设计的；端到端提速要用硬件编码器，并重新校准 CRF。
5. **批处理前先 `ffprobe`**：分辨率、帧率、色彩范围、时长都可能与文件名暗示的不一致。
6. **`-c copy` 之前确认参数一致**：编码不同、时基不同、音轨数量不同都会让 copy 失败或产出坏文件。
7. **对 GOP 有要求时显式设 `-g`**：默认 GOP 由编码器决定，切片/直播需要可预测的关键帧间隔。
8. **日志别丢**：`-hide_banner` 保留错误行即可；排查时加 `-loglevel warning` 或 `-v verbose`。

## 常见问题

| 问题 | 原因与解决 |
|------|-----------|
| `moov atom not found` | MP4 录制/传输中断导致 moov 未写入；若源是流，改用 `-movflags +faststart` 重新封装或从流重新采集 |
| 大量 `Non-monotonous DTS in output stream` | 多段拼接或变帧率输入的时间戳不连续；加 `-fflags +genpts` 或改用 concat 滤镜统一重编码 |
| 输出画面颜色发灰 / 过曝 | 色彩范围与矩阵没对齐：显式加 `-color_range tv -colorspace bt709`，并确认 `-pix_fmt` 一致 |
| `height not divisible by 2` / 编码器报奇数尺寸 | 缩放时用 `scale=w:-2`（`-2` 自动取偶数），不要用 `-1` |
| `Unknown encoder 'libx264'` | 发行版构建未启用 GPL 编码器；换自带 libx264 的构建（官方静态包或 `--enable-gpl` 自编） |
| `-hwaccel cuda` 报 `Cannot load libcuda.so` / 无效 | 显卡驱动或构建不含该后端；先 `ffmpeg -hwaccels` 看实际支持项，或退回软件解码 |
| HLS 切片在播放器里卡住 | 切片时长与 GOP 不匹配（`-hls_time` 小于关键帧间隔会切不动）；设 `-g` 使关键帧对齐切片边界 |
| RTSP 拉流频繁超时 | UDP 丢包；加 `-rtsp_transport tcp`，必要时用 `-timeout 5000000`（微秒）控制 socket 读写超时（老脚本里的 `-stimeout` 已废弃） |
| 老脚本里的 `-vsync 0` / `-vsync vfr` 不再生效 | `-vsync` 已被 `-fps_mode` 取代（9.x 文档里只有 `-fps_mode`）：`0` → `passthrough`，`vfr` → `vfr`，`cfr` → `cfr` |

## 相关技能

- **gdal** — 帧序列/正射影像的后续处理（重投影、金字塔、COG）：[../../gis/gdal/SKILL.md](../../gis/gdal/SKILL.md)
- **openlayers** — 在 Web 端播放/叠加这些视频与切片产物的地图侧对照：[../../gis/openlayers/SKILL.md](../../gis/openlayers/SKILL.md)
- **blender** — 把帧序列做成纹理或渲染序列时的三维侧工具：[../../cad/blender/SKILL.md](../../cad/blender/SKILL.md)
- **docker-compose** — 把推流/切片服务容器化时的编排方式：[../docker-compose/SKILL.md](../docker-compose/SKILL.md)

## 参考资源

- 官方文档：<https://ffmpeg.org/ffmpeg.html> ｜ 滤镜：<https://ffmpeg.org/ffmpeg-filters.html> ｜ 格式：<https://ffmpeg.org/ffmpeg-formats.html>
- 编解码器参数：<https://ffmpeg.org/ffmpeg-codecs.html>
- 发布列表：<https://ffmpeg.org/releases/> ｜ 下载：<https://ffmpeg.org/download.html>
- 9.0 发布说明：<https://github.com/FFmpeg/FFmpeg/blob/release/9.0/RELEASE_NOTES>
- 许可证说明：<https://ffmpeg.org/legal.html>
