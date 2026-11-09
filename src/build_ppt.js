/* Build the 9-slide paper-introduction deck (QEvasion, EMNLP 2024 Findings),
 * following the course template structure. Run from the project root:
 *   node src/build_ppt.js
 */
const pptxgen = require("pptxgenjs");
const path = require("path");

const FIG = path.join(__dirname, "..", "results", "figures");
const OUT = path.join(__dirname, "..", "..", "论文介绍-QEvasion回答清晰度分类.pptx");

// ---- palette (BACKGROUND -> PRIMARY -> ACCENT) ----
const BG_DARK = "16324F";   // deep navy (title / closing)
const BG_LIGHT = "F7F8FA";  // off-white (content)
const PRIMARY = "1F4E79";   // structural blue
const ACCENT = "E8A33D";    // amber, sparing use
const TEXT = "1F2937";
const MUTED = "64748B";
const LIGHTLINE = "D8DEE6";

const F = "微软雅黑";
const W = 13.33, H = 7.5, M = 0.55;

let p = new pptxgen();
p.layout = "LAYOUT_WIDE";
p.author = "课程汇报";
p.title = "QEvasion: Response Clarity Classification";

const bu = () => ({ code: "2022", indent: 12 });

function kicker(s, text, dark = false) {
  s.addText(text, { x: M, y: 0.42, w: 6, h: 0.32, fontSize: 12.5, bold: true,
    color: dark ? ACCENT : ACCENT, fontFace: F, charSpacing: 3, margin: 0 });
}
function slideTitle(s, text, dark = false) {
  s.addText(text, { x: M, y: 0.72, w: W - 2 * M, h: 0.75, fontSize: 30, bold: true,
    color: dark ? "FFFFFF" : TEXT, fontFace: F, margin: 0 });
}
function pageNo(s, n) {
  s.addText(String(n).padStart(2, "0"), { x: W - 1.05, y: H - 0.62, w: 0.55, h: 0.4,
    fontSize: 12, color: MUTED, fontFace: "Arial", align: "right", margin: 0 });
}
function srcNote(s, text, dark = false) {
  s.addText(text, { x: M, y: H - 0.58, w: 9.6, h: 0.36, fontSize: 11,
    color: dark ? "9FB2C6" : MUTED, fontFace: F, margin: 0 });
}

/* ================= Slide 1 — 标题页 ================= */
{
  const s = p.addSlide();
  s.background = { color: BG_DARK };
  // right-side illustration in a rounded frame
  const imgH = 6.3, imgW = imgH * 0.838; // cover_art ratio
  s.addImage({ path: path.join(FIG, "cover_art.png"),
    x: W - imgW - 0.55, y: (H - imgH) / 2, w: imgW, h: imgH });

  s.addText("论文介绍 · 自然语言处理课程汇报", { x: M, y: 0.85, w: 6.4, h: 0.35,
    fontSize: 13, bold: true, color: ACCENT, fontFace: F, charSpacing: 2, margin: 0 });
  s.addText("\u201CI Never Said That\u201D", { x: M, y: 1.45, w: 7.6, h: 1.15,
    fontSize: 44, bold: true, color: "FFFFFF", fontFace: F, margin: 0 });
  s.addText("A Dataset, Taxonomy and Baselines on Response Clarity Classification",
    { x: M, y: 2.62, w: 7.5, h: 0.95, fontSize: 19, color: "C9D7E6", fontFace: F,
      italic: true, margin: 0 });
  s.addText("回答清晰度分类：数据集、分类法与基线 —— 问答回避检测与跨场景迁移",
    { x: M, y: 3.62, w: 7.6, h: 0.5, fontSize: 15.5, bold: true, color: ACCENT,
      fontFace: F, margin: 0 });

  s.addText([
    { text: "作者：", options: { bold: true, color: "9FB2C6" } },
    { text: "Konstantinos Thomas, Giorgos Filandrianos, Maria Lymperaiou, Chrysoula Zerva, Giorgos Stamou（雅典国立技术大学）", options: { color: "E6EDF5" } },
  ], { x: M, y: 4.55, w: 7.6, h: 0.75, fontSize: 13, fontFace: F, margin: 0 });
  s.addText([
    { text: "会议：", options: { bold: true, color: "9FB2C6" } },
    { text: "Findings of EMNLP 2024（2024.findings-emnlp.300）", options: { color: "E6EDF5" } },
  ], { x: M, y: 5.28, w: 7.6, h: 0.4, fontSize: 13, fontFace: F, margin: 0 });
  s.addText("汇报人：你的名字        日期：2026 年 12 月", { x: M, y: 6.15, w: 7.6,
    h: 0.4, fontSize: 14, bold: true, color: "FFFFFF", fontFace: F, margin: 0 });
  srcNote(s, "与实验报告对应的论文：QEvasion 数据集与回答清晰度分类基线", true);
}

/* ================= Slide 2 — 研究背景和问题陈述 ================= */
{
  const s = p.addSlide();
  s.background = { color: BG_LIGHT };
  kicker(s, "BACKGROUND & PROBLEM");
  slideTitle(s, "研究背景和问题陈述");

  // left column: 3 rows
  const rows = [
    ["研究领域", "对话问答中的回答质量分析：政治访谈、客服会话与安全对话中，回答是否\u201C实质回应了提问\u201D比情感倾向更关键。"],
    ["研究问题", "现有 QA 数据集假定回答质量均匀，缺乏对回避/模糊回答的统一定义、标注数据与基线模型：什么是\u201C清晰的回答\u201D？如何自动判别？"],
    ["重要性", "支撑新闻事实核查、访谈质量自动评估、客服质检与对话安全合规；回避行为分析也是政治传播研究的长期命题。"],
  ];
  let y = 1.85;
  for (const [head, body] of rows) {
    s.addText(head, { x: M, y, w: 1.9, h: 0.45, fontSize: 16, bold: true,
      color: PRIMARY, fontFace: F, margin: 0 });
    s.addText(body, { x: 2.55, y: y - 0.03, w: 6.6, h: 1.35, fontSize: 13.5,
      color: TEXT, fontFace: F, margin: 0, lineSpacingMultiple: 1.25 });
    y += 1.55;
    if (y < 6.2) s.addShape(p.shapes.LINE, { x: M, y: y - 0.28, w: 8.6, h: 0,
      line: { color: LIGHTLINE, width: 1 } });
  }

  // right stat cards
  const stats = [
    ["3,756", "QA 样本对（政治记者会）"],
    ["3 + 9", "粗粒度 + 细粒度两级标签"],
    ["59.2%", "Ambivalent 类占比（不均衡）"],
  ];
  let sy = 1.9;
  for (const [num, label] of stats) {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 9.5, y: sy, w: 3.25, h: 1.42,
      fill: { color: "FFFFFF" }, rectRadius: 0.09,
      shadow: { type: "outer", color: "16324F", blur: 7, offset: 2, angle: 45, opacity: 0.14 } });
    s.addText(num, { x: 9.7, y: sy + 0.14, w: 2.9, h: 0.62, fontSize: 30, bold: true,
      color: num === "59.2%" ? ACCENT : PRIMARY, fontFace: "Arial", margin: 0 });
    s.addText(label, { x: 9.7, y: sy + 0.82, w: 2.9, h: 0.45, fontSize: 11.5,
      color: MUTED, fontFace: F, margin: 0 });
    sy += 1.62;
  }
  pageNo(s, 2);
}

/* ================= Slide 3 — 相关工作 ================= */
{
  const s = p.addSlide();
  s.background = { color: BG_LIGHT };
  kicker(s, "RELATED WORK");
  slideTitle(s, "相关工作");

  const cols = [
    ["关键贡献", [
      "QA 答案质量与可信度评估：SQuAD 类抽取式问答关注答案定位，少问\u201C是否真的回答了\u201D",
      "政治传播学对回避（evasion）有定性分类，但停留在人工小规模分析",
      "LLM 评测：GPT-3.5 等模型对\u201C是否被回答\u201D缺乏稳定判断能力",
    ]],
    ["现有不足", [
      "缺少公开、带两级标签的回避检测数据集",
      "回避手法没有统一可计算的分类法",
      "跨域场景（客服/安全对话）缺乏可复用的实验流程",
    ]],
    ["与本文关系", [
      "首次给出两级回答清晰度分类法（3 粗 + 9 细）",
      "构建并开源 QEvasion 数据集（3,756 对，ChatGPT 辅助 + 人工校验）",
      "建立 GPT-3.5 提示与 BERT 系微调双线基线，供跨场景迁移复用",
    ]],
  ];
  let x = M;
  const cw = 3.98;
  for (const [head, items] of cols) {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 1.8, w: cw, h: 4.7,
      fill: { color: head === "与本文关系" ? "16324F" : "FFFFFF" }, rectRadius: 0.1,
      shadow: { type: "outer", color: "16324F", blur: 7, offset: 2, angle: 45, opacity: 0.12 } });
    s.addText(head, { x: x + 0.28, y: 2.05, w: cw - 0.56, h: 0.45, fontSize: 16.5,
      bold: true, color: head === "与本文关系" ? ACCENT : PRIMARY, fontFace: F, margin: 0 });
    s.addText(items.map((t, i) => ({ text: t, options: { bullet: bu(), breakLine: i < items.length - 1,
      color: head === "与本文关系" ? "E6EDF5" : TEXT } })),
      { x: x + 0.28, y: 2.6, w: cw - 0.56, h: 3.7, fontSize: 12.5, fontFace: F,
        paraSpaceAfter: 10, margin: 0, lineSpacingMultiple: 1.16, valign: "top" });
    x += cw + 0.19;
  }
  srcNote(s, "Thomas et al., Findings of EMNLP 2024 · §2 Related Work");
  pageNo(s, 3);
}

/* ================= Slide 4 — 主要贡献 ================= */
{
  const s = p.addSlide();
  s.background = { color: BG_LIGHT };
  kicker(s, "CONTRIBUTIONS");
  slideTitle(s, "主要贡献");

  const items = [
    ["01", "两级回答清晰度分类法", "粗粒度三分类（Clear Reply / Ambivalent / Clear Non-Reply）+ 细粒度九类回避手法（Dodging、Implicit、Deflection、Partial 等），层级映射明确。"],
    ["02", "QEvasion 数据集", "从政治记者会访谈构建 3,756 个\u201C子问题—完整回答\u201D对：ChatGPT 辅助预标 + 3 名标注者人工校验，含标注一致性分析。"],
    ["03", "系统化基线", "GPT-3.5 零/少样本提示 vs BERT/RoBERTa/DeBERTa 微调与参数高效适配；发现微调编码器显著优于 LLM 零样本。"],
    ["04", "挑战定位", "量化长回答截断、类别不均衡（Ambivalent 占 59.2%）与标签边界模糊三大难点，为后续迁移研究提供参照。"],
  ];
  let y = 1.85;
  for (const [num, head, body] of items) {
    s.addText(num, { x: M, y: y - 0.05, w: 0.95, h: 0.85, fontSize: 34, bold: true,
      color: "C8D4E2", fontFace: "Arial", margin: 0 });
    s.addText(head, { x: 1.62, y, w: 10.6, h: 0.42, fontSize: 16, bold: true,
      color: PRIMARY, fontFace: F, margin: 0 });
    s.addText(body, { x: 1.62, y: y + 0.44, w: 10.9, h: 0.72, fontSize: 12.5,
      color: TEXT, fontFace: F, margin: 0, lineSpacingMultiple: 1.18 });
    y += 1.28;
  }
  s.addText("核心思想：把\u201C回答是否满足问题的信息需求\u201D变成可计算的两级分类问题，并用统一基准度量模型的判别能力。",
    { x: M, y: 6.85, w: 12.2, h: 0.45, fontSize: 13, italic: true, color: ACCENT,
      bold: true, fontFace: F, margin: 0 });
  pageNo(s, 4);
}

/* ================= Slide 5 — 方法概述 ================= */
{
  const s = p.addSlide();
  s.background = { color: BG_LIGHT };
  kicker(s, "METHOD OVERVIEW");
  slideTitle(s, "方法概述");

  // ---- pipeline diagram (native shapes) ----
  const boxes = [
    ["政治访谈", "视频/文本素材"],
    ["问答对抽取", "子问题 q + 回答 a"],
    ["两级标注", "GPT-3.5 预标 + 人工校验"],
    ["句对编码", "BERT 类模型微调"],
    ["两级分类", "3 类 / 9 类输出"],
  ];
  const bw = 2.14, bh = 1.28, gap = 0.32, y0 = 2.0;
  let x = M;
  for (let i = 0; i < boxes.length; i++) {
    const [head, sub] = boxes[i];
    const last = i === boxes.length - 1;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: y0, w: bw, h: bh,
      fill: { color: last ? PRIMARY : "FFFFFF" }, rectRadius: 0.08,
      shadow: { type: "outer", color: "16324F", blur: 6, offset: 2, angle: 45, opacity: 0.13 } });
    s.addText(head, { x, y: y0 + 0.18, w: bw, h: 0.45, fontSize: 14.5, bold: true,
      align: "center", color: last ? "FFFFFF" : PRIMARY, fontFace: F, margin: 0 });
    s.addText(sub, { x: x + 0.08, y: y0 + 0.66, w: bw - 0.16, h: 0.5, fontSize: 10.5,
      align: "center", color: last ? "C9D7E6" : MUTED, fontFace: F, margin: 0 });
    if (!last) s.addText("\u25B8", { x: x + bw - 0.02, y: y0 + 0.4, w: gap + 0.06, h: 0.5,
      fontSize: 20, color: ACCENT, align: "center", fontFace: "Arial", margin: 0 });
    x += bw + gap;
  }

  // ---- taxonomy tree ----
  s.addText("两级标签体系（层级映射）", { x: M, y: 3.75, w: 6, h: 0.4, fontSize: 15,
    bold: true, color: TEXT, fontFace: F, margin: 0 });
  const root = { x: M, y: 4.28, w: 2.5, h: 0.62, t: "clarity_label" };
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: root.x, y: root.y, w: root.w, h: root.h,
    fill: { color: "16324F" }, rectRadius: 0.07 });
  s.addText(root.t, { x: root.x, y: root.y, w: root.w, h: root.h, fontSize: 13,
    bold: true, align: "center", valign: "middle", color: "FFFFFF", fontFace: F, margin: 0 });
  const leaves = [
    ["Clear Reply", "Explicit"],
    ["Ambivalent", "Dodging · Implicit · General · Deflection · Partial/half-answer"],
    ["Clear Non-Reply", "Declining to answer · Claims ignorance · Clarification"],
  ];
  let ly = 3.9;
  for (const [coarse, fine] of leaves) {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 5.0, y: ly, w: 2.85, h: 0.56,
      fill: { color: "FFFFFF" }, rectRadius: 0.07,
      line: { color: PRIMARY, width: 1.2 } });
    s.addText(coarse, { x: 5.0, y: ly, w: 2.85, h: 0.56, fontSize: 12.5, bold: true,
      align: "center", valign: "middle", color: PRIMARY, fontFace: F, margin: 0 });
    s.addText(fine, { x: 8.05, y: ly, w: 4.7, h: 0.56, fontSize: 10.5,
      valign: "middle", color: MUTED, fontFace: F, margin: 0 });
    s.addShape(p.shapes.LINE, { x: 2.5, y: ly + 0.28, w: 2.5, h: 0,
      line: { color: LIGHTLINE, width: 1, dashType: "dash" } });
    ly += 0.78;
  }

  // ---- how it addresses gaps ----
  s.addText("如何解决相关工作中的不足", { x: M, y: 6.35, w: 6, h: 0.38, fontSize: 14,
    bold: true, color: TEXT, fontFace: F, margin: 0 });
  s.addText([
    { text: "统一分类法替代定性描述 → 数据集 + 基线让回避检测可比较、可复现，也为跨场景迁移提供统一字段适配器（text_a / text_b / label）。", options: {} },
  ], { x: M, y: 6.74, w: 12.2, h: 0.6, fontSize: 12.5, color: TEXT, fontFace: F,
    margin: 0, lineSpacingMultiple: 1.15 });
  pageNo(s, 5);
}

/* ================= Slide 6 — 数学公式 ================= */
{
  const s = p.addSlide();
  s.background = { color: BG_LIGHT };
  kicker(s, "KEY FORMULAS");
  slideTitle(s, "数学公式（选主要公式）");

  const rows = [
    ["formula_input.png", "输入编码", "问题 q 与回答 a 拼接后经 BERT 编码，[CLS] 位置向量承载跨句交互信息。"],
    ["formula_softmax.png", "分类分布", "线性头 + softmax 得到每个清晰度类别的后验概率。"],
    ["formula_loss.png", "交叉熵损失", "微调目标：最小化真实类别与预测分布的交叉熵。"],
    ["formula_macrof1.png", "Macro-F1", "评估口径：对每个类别独立计算 F1 后取平均，对类别不均衡鲁棒。"],
  ];
  let y = 1.78;
  for (const [img, head, note] of rows) {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: M, y, w: 5.6, h: 0.92,
      fill: { color: "FFFFFF" }, rectRadius: 0.08,
      line: { color: LIGHTLINE, width: 1 } });
    s.addImage({ path: path.join(FIG, img), x: M + 0.25, y: y + 0.13, w: 5.1, h: 0.66 });
    s.addText(head, { x: 6.45, y: y + 0.02, w: 2.4, h: 0.4, fontSize: 14.5, bold: true,
      color: PRIMARY, fontFace: F, margin: 0 });
    s.addText(note, { x: 6.45, y: y + 0.4, w: 6.25, h: 0.52, fontSize: 11.5,
      color: MUTED, fontFace: F, margin: 0, lineSpacingMultiple: 1.1 });
    y += 1.12;
  }
  s.addText("直觉：跨句自注意力让模型逐点核对\u201C回答是否覆盖问题的每个信息点\u201D；Macro-F1 保证少数类（Clear Non-Reply，10.3%）不被多数类淹没。",
    { x: M, y: 6.5, w: 12.2, h: 0.75, fontSize: 12.5, color: TEXT, fontFace: F,
      margin: 0, lineSpacingMultiple: 1.2 });
  pageNo(s, 6);
}

/* ================= Slide 7 — 实验设置 ================= */
{
  const s = p.addSlide();
  s.background = { color: BG_LIGHT };
  kicker(s, "EXPERIMENTAL SETUP");
  slideTitle(s, "实验设置");

  const rows = [
    ["数据集", "QEvasion（本文复现基准）：train 3,448 / test 308；另迁移至 GLUE-QNLI（train 20,000 / dev 3,000，seed=42 分层抽样）"],
    ["任务", "输入 = question + interview_answer 文本对；输出 = 3 类清晰度（粗）/ 9 类回避手法（细）"],
    ["评估指标", "Accuracy、Macro-F1、类别级 Precision / Recall / F1、混淆矩阵"],
    ["模型", "多数类基线 · TF-IDF + 逻辑回归 · SBERT（冻结）+ LR · BERT-base 句对微调；论文另报告 GPT-3.5 提示与参数高效适配"],
    ["工具/框架", "PyTorch + HuggingFace Transformers + scikit-learn；RTX 4060 Laptop（fp16）；seed=42 全程固定"],
    ["关键超参", "max_len=384（longest-first 截断）、epochs=4、batch=16、lr=2e-5、AdamW(wd=0.01)、warmup 10%"],
  ];
  let y = 1.82;
  for (const [head, body] of rows) {
    s.addShape(p.shapes.RECTANGLE, { x: M, y: y + 0.06, w: 0.16, h: 0.16,
      fill: { color: ACCENT } });
    s.addText(head, { x: M + 0.34, y: y - 0.05, w: 1.85, h: 0.45, fontSize: 14.5,
      bold: true, color: PRIMARY, fontFace: F, margin: 0 });
    s.addText(body, { x: 2.75, y: y - 0.05, w: 10.0, h: 0.72, fontSize: 12.5,
      color: TEXT, fontFace: F, margin: 0, lineSpacingMultiple: 1.12 });
    y += 0.82;
  }
  srcNote(s, "复现环境与配置已开源（代码仓库随实验报告提交），全部结果可一键复现");
  pageNo(s, 7);
}

/* ================= Slide 8 — 实验结果与分析 ================= */
{
  const s = p.addSlide();
  s.background = { color: BG_LIGHT };
  kicker(s, "RESULTS & ANALYSIS");
  slideTitle(s, "实验结果与分析");

  // left: native bar chart of our reproduction
  s.addText("复现结果：QEvasion 测试集（Acc / Macro-F1）", { x: M, y: 1.7, w: 7, h: 0.4,
    fontSize: 14.5, bold: true, color: TEXT, fontFace: F, margin: 0 });
  s.addChart(p.charts.BAR, [
    { name: "Accuracy", labels: ["多数类", "TF-IDF+LR", "SBERT+LR", "BERT 微调"],
      values: [0.669, 0.545, 0.513, 0.714] },
    { name: "Macro-F1", labels: ["多数类", "TF-IDF+LR", "SBERT+LR", "BERT 微调"],
      values: [0.267, 0.416, 0.420, 0.556] },
  ], {
    x: M, y: 2.15, w: 7.1, h: 3.6, barDir: "col",
    chartColors: [PRIMARY, ACCENT],
    chartArea: { fill: { color: "F7F8FA" } },
    catAxisLabelColor: MUTED, valAxisLabelColor: MUTED,
    catAxisLabelFontSize: 11, valAxisLabelFontSize: 10,
    valAxisMaxVal: 0.8, valAxisMinVal: 0, valAxisMajorUnit: 0.2,
    valGridLine: { color: "E2E8F0", size: 0.5 }, catGridLine: { style: "none" },
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: TEXT,
    dataLabelFontSize: 10, dataLabelFormatCode: "0.000",
    showLegend: true, legendPos: "b", legendFontSize: 11, legendColor: MUTED,
  });

  // right: confusion matrix + findings
  s.addImage({ path: path.join(FIG, "fig3_cm_bert_coarse.png"), x: 8.35, y: 1.72,
    w: 4.35, h: 3.6 });
  s.addText("主要发现", { x: 8.35, y: 5.5, w: 3, h: 0.38, fontSize: 14, bold: true,
    color: PRIMARY, fontFace: F, margin: 0 });
  s.addText([
    { text: "微调 > 一切冻结表示：BERT 的 Macro-F1 比最强基线高约 0.14", options: { bullet: bu(), breakLine: true } },
    { text: "多数类陷阱：Accuracy 0.669 但 Macro-F1 仅 0.267", options: { bullet: bu(), breakLine: true } },
    { text: "错误集中于 Clear Reply \u2194 Ambivalent 边界（占误判约 80%）", options: { bullet: bu() } },
  ], { x: 8.35, y: 5.88, w: 4.45, h: 1.35, fontSize: 11.5, color: TEXT,
    fontFace: F, paraSpaceAfter: 6, margin: 0, valign: "top" });
  srcNote(s, "数据：本文复现（seed=42，官方测试集 n=308）；论文原报告中 BERT 类基线同样显著优于 GPT-3.5 零样本提示");
  pageNo(s, 8);
}

/* ================= Slide 9 — 讨论 + 大作业完成计划 ================= */
{
  const s = p.addSlide();
  s.background = { color: BG_DARK };
  kicker(s, "DISCUSSION & PLAN", true);
  slideTitle(s, "讨论与大作业完成计划", true);

  const cols = [
    ["重要发现", [
      "跨句交互表征是清晰度判别的关键增益来源",
      "零样本直接迁移失效：QEvasion 模型直接用于 QNLI 仅 0.49 Acc（等于多数类）",
      "粗细两级标签在预测层面并不自动一致（双模型一致率仅 0.35）",
    ]],
    ["挑战", [
      "长回答（最长 2,117 词）截断损失信息",
      "细粒度尾部类样本过少（最少 79 条）",
      "官方划分存在 38.3% 访谈级来源重叠（泄漏风险）",
    ]],
    ["潜在改进", [
      "先粗后细的层级建模（coarse-to-fine）",
      "滑动窗口编码长回答 + 对比式数据增广",
      "访谈级去重划分与跨域（客服/安全对话）验证",
    ]],
  ];
  let x = M;
  const cw = 3.98;
  for (const [head, items] of cols) {
    s.addText(head, { x, y: 1.75, w: cw, h: 0.42, fontSize: 16, bold: true,
      color: ACCENT, fontFace: F, margin: 0 });
    s.addText(items.map((t, i) => ({ text: t, options: { bullet: bu(),
      breakLine: i < items.length - 1, color: "E6EDF5" } })),
      { x, y: 2.25, w: cw, h: 2.6, fontSize: 12.5, fontFace: F, paraSpaceAfter: 9,
        margin: 0, lineSpacingMultiple: 1.18, valign: "top" });
    x += cw + 0.19;
  }

  // plan timeline
  s.addText("大作业完成计划", { x: M, y: 5.15, w: 4, h: 0.42, fontSize: 16, bold: true,
    color: ACCENT, fontFace: F, margin: 0 });
  const steps = [
    ["已完成", "QEvasion 基线与 BERT 微调、错误分析"],
    ["已完成", "QNLI 迁移 + 数据效率（10/30/100%）"],
    ["已完成", "扩展：粗—细粒度标签层级一致性分析"],
    ["待完成", "期末论文定稿 + 代码上传 GitHub"],
  ];
  let sx = M;
  const sw = 2.98;
  for (let i = 0; i < steps.length; i++) {
    const [tag, txt] = steps[i];
    const done = tag === "已完成";
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: sx, y: 5.65, w: sw, h: 1.15,
      fill: { color: done ? "1F4E79" : "0F2438" }, rectRadius: 0.08,
      line: { color: done ? "1F4E79" : "3A6491", width: 1 } });
    s.addText(tag, { x: sx + 0.18, y: 5.78, w: sw - 0.36, h: 0.34, fontSize: 12,
      bold: true, color: done ? "9FD0FF" : ACCENT, fontFace: F, margin: 0 });
    s.addText(txt, { x: sx + 0.18, y: 6.12, w: sw - 0.36, h: 0.6, fontSize: 11,
      color: "E6EDF5", fontFace: F, margin: 0, lineSpacingMultiple: 1.1 });
    if (i < steps.length - 1) s.addText("\u25B8", { x: sx + sw - 0.04, y: 6.0,
      w: 0.24, h: 0.4, fontSize: 16, color: ACCENT, align: "center", fontFace: "Arial", margin: 0 });
    sx += sw + 0.1;
  }
  pageNo(s, 9);
}

p.writeFile({ fileName: OUT }).then(() => console.log("saved", OUT));
