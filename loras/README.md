# LoRA 说明（只放文档，不分发模型文件）

Civitai 上的 LoRA 许可普遍禁止二次分发，所以这个文件夹**只放说明，不放 `.safetensors` 文件**。请从下表链接（免费账号）下载到模型根目录的 `loras/` 下，保持文件名一致，然后校验：

```
python scripts/download_models.py --root <模型根目录> --check-only
```

每个文件的 SHA-256 见 [../models/models.toml](../models/models.toml)。

| 文件（放到 `loras/` 下） | 风格 / 训练目标 | 来源与训练集说明 | 实测强度 | 备注 |
|---|---|---|---|---|
| `z3zz4-k2-4_c1-st5000.safetensors` | z3zz4 画师风格，Krea 2 上训练 | [Civitai #2750764](https://civitai.com/models/2750764)，训练细节以作者页面为准 | **0.95**（Turbo，"Teto 海报风"，本仓库工作流与画廊的默认风格）；0.55 是参考图复刻配方 | 本仓库所有示例图的风格来源 |
| `BArtstyle-KREA2-V1-1.safetensors` | 蔚蓝档案（Blue Archive）平涂画风 | [Civitai #29215](https://civitai.com/models/29215)，作者 4BEraser | 0.75 | V1-1 在杂乱拼贴里保脸更干净；V2 容易闭眼、碎脸 |
| `Yoneyama_Mai_Krea2.safetensors` | 米山舞画师风格 | [Civitai #2629905](https://civitai.com/models/2629905) | 0.45 | INT4 底模上叠三个 LoRA 会糊成噪点 |
| `krea2_style_reference.safetensors` | 风格参考 LoRA（ostris，AI-Toolkit 训练） | [Comfy-Org/Krea-2](https://huggingface.co/Comfy-Org/Krea-2) / [ostris](https://huggingface.co/ostris/krea2_turbo_style_reference) | 按工作流 | 喂一张参考图，让输出吃它的风格；在 models.toml 里可自动下载 |

## 在工作流里切换

`assets/workflows/krea2_turbo_z3zz4_api.json` 固定加载 z3zz4@0.95。不改 JSON 也能换：

```
python scripts/run_workflow.py <工作流> --prompt-file prompt.txt --lora "BArtstyle-KREA2-V1-1.safetensors:0.75"
```

`--lora 文件名:强度` 可重复，按顺序对应工作流里第 n 个 LoRA 节点。

## 相关文件夹

| 文件夹 | 内容 |
|---|---|
| [`models/`](../models/) | 模型清单 models.toml（底模 / 文本编码器 / VAE / 分割模型的文件名、URL、SHA-256） |
| [`skills/*/assets/`](../skills/anime-illustration/assets/) | 素材：提示词样例（`prompts/`）与 ComfyUI 工作流（`workflows/`），在各 skill 内 |
| [`docs/final-frames/`](../docs/final-frames/) | 最终单图（画廊成品，含配方标注） |
| [`docs/comparisons/`](../docs/comparisons/) | 对比图（修复前后等） |
| [`examples/`](../skills/anime-illustration/examples/) | 完整案例：素材 + 蒙版 + 对比 + 最终图逐文件拆解 |
