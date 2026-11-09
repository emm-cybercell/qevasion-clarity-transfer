# GitHub 上传指南（大作业第五项：10 分）

`qevasion-project/` 目录已是一个完整可复现的仓库（代码 + 指标 + 预测文件 + 图表）。
大作业要求把代码上传到 GitHub 并把链接写进正文。只需三步：

## 1. 在 GitHub 上创建空仓库

浏览器打开 https://github.com/new ，仓库名建议 `qevasion-clarity-transfer`，
选 Public（课程作业通常要求公开可见），**不要**勾选自动生成 README（本地已有）。

## 2. 本地推送（在 qevasion-project 目录下执行）

```bash
cd qevasion-project
git init
git add .
git commit -m "QEvasion clarity classification: baselines, BERT fine-tuning, QNLI transfer & data efficiency"
git branch -M main
git remote add origin https://github.com/<你的用户名>/qevasion-clarity-transfer.git
git push -u origin main
```

首次推送会要求登录：用浏览器授权（GitHub CLI / Credential Manager）即可。

## 3. 把链接写进大作业正文

打开 `自然语言处理期末大作业-....docx`，把第五节中的
`https://github.com/<你的GitHub用户名>/qevasion-clarity-transfer`
替换为实际仓库地址（两处：正文与括号说明）。

> `.gitignore` 已排除模型权重（约 420MB）与原始压缩数据，仓库只含代码、
> 指标 JSON、预测 CSV、图表与日志，通常 < 20MB。如需附上模型权重，
> 可在 GitHub Release 中以附件形式上传。
