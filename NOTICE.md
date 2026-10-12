# 版权与授权说明

## 一、本仓库包含什么

- **汉化词条表** `dict/rd_zh.tsv` —— 界面英文原文与中文译文的对照表
- **词条维护工具** `tools/` —— 从 RenderDoc 源码抽取可翻译文案、校验词条格式的脚本
- **截图** `docs/` —— 汉化前后对比
- **汉化版安装包**（在 Releases 里）—— 自带 RenderDoc 1.46 完整本体的安装程序

## 二、两套许可，分清楚

| 覆盖范围 | 许可 | 文件 |
|---|---|---|
| 本仓库的**词条译文**、工具脚本、文档 | **CC BY-SA 4.0** | [`LICENSE`](LICENSE) |
| **RenderDoc 本体**及其全部源码与二进制 | **MIT** | [`LICENSE-RenderDoc`](LICENSE-RenderDoc) |

### 词条与文档：CC BY-SA 4.0

`dict/rd_zh.tsv` 的**中文译文**、`tools/` 下的脚本、README 与本文档，
版权归 **星空汉化** 所有，以 **CC BY-SA 4.0** 授权：

- ✅ 可以自由使用、修改、再分发，**包括商用**
- ✅ 用在自己的项目里、拿去做别的软件的汉化，都可以
- ⚠️ **修改后的词条表必须以同样的许可公开**（ShareAlike），并保留署名

### RenderDoc：MIT

> RenderDoc is a free MIT licensed stand-alone graphics debugger.
>
> Copyright (c) 2015-2026 Baldur Karlsson
> Copyright (c) 2014 Crytek
> Copyright (c) 1998-2018 Third party code and tools
>
> 项目主页：https://renderdoc.org/
> 源码仓库：https://github.com/baldurk/renderdoc

MIT 许可允许任何人自由使用、复制、修改、合并、发布、分发、再授权乃至销售本软件，
唯一的要求是**保留版权声明与许可条款**。

因此：

- Releases 里的安装包**自带 RenderDoc 完整本体**是**合法**的，属于 MIT 明确允许的再分发
- MIT 许可原文随包附带（装好后见安装目录下的 `LICENSE.rtf`），
  本仓库的 [`LICENSE-RenderDoc`](LICENSE-RenderDoc) 是同一份条款

## 三、不在本授权范围内的内容

以下内容**不属于**本仓库的授权范围：

- **RenderDoc 程序本体**及其全部源码、二进制、界面英文原文 —— 归 Baldur Karlsson 所有，
  以 MIT 许可发布（见上文）
- **「RenderDoc」名称与相关商标** —— 归其权利人所有
- **第三方组件**（Qt、Python、zlib、OpenSSL、AMD / SPIRV 相关工具等）——
  各有自己的许可，随包附带的 `LICENSE.rtf` 与其安装目录内的说明为准
- **用 RenderDoc 抓取、导出的任何内容**（抓帧文件、材质、模型、着色器等）——
  那属于其原始权利人，是否可以分发取决于**你和原权利人的协议**，与本汉化无关

## 四、其它

本汉化**不修改 RenderDoc 的功能**，界面文字以外的行为与原版一致。

本汉化为无偿公益汉化，完全免费分享。如果你是付费购买到的，请及时联系卖家申请退款。
