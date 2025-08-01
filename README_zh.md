<div align="center">

# Self-Foveate: Enhancing Diversity and Difficulty of Synthesized Instructions from Unsupervised Text via Multi-Level Foveation

</div>

<div align="center" style="font-size: 15pt">

<a href='https://arxiv.org/abs/2507.23440'><img src='https://img.shields.io/badge/Arxiv-PDF-purple'></a>
<a href='https://aclanthology.org/2025.findings-acl.380/'><img src='https://img.shields.io/badge/ACL-PDF-red'></a>

<h4 align="center">
    <p>
        <a href="README.md">English</a> | <b>中文</b>
    </p>
</h4>

</div>


## 🎊 最新消息 <!-- omit in toc -->

- [2025.07.30] 我们的论文"Self-Foveate: Enhancing Diversity and Difficulty of Synthesized Instructions from Unsupervised Text via Multi-Level Foveation"已发表在Findings of ACL 2025中！📄 [[论文](https://aclanthology.org/2025.findings-acl.380/)]


## 📜 简介 <!-- omit in toc -->

Self-Foveate是一种创新的LLM驱动的指令合成方法，引入了"微观-分散-宏观"多级焦点化方法论。这种方法有效地指导LLM深入挖掘嵌入在无监督文本中的细粒度信息，从而增强合成指令的多样性和难度。在多个无监督语料库和不同模型架构上的综合实验验证了我们提出的方法的有效性和优越性。

💡 **微观-分散-宏观焦点化方法论**。 
	Self-Foveate采用了一种新颖的多级焦点化方法，有效地指导LLM深入挖掘嵌入在无监督文本中的细粒度信息。

🛠️ **增强的多样性和难度**。
  该框架生成的指令与基线方法相比具有优越的多样性和难度，使其成为训练更强大语言模型的理想选择。

🚀 **全面验证**。
    
  在多个无监督语料库和不同模型架构上的综合实验验证了我们提出的方法的有效性和优越性。

<div align="center"> <img src="assets/main_experiment.png" width = 80% /> </div>

## 📌 目录 <!-- omit in toc -->

- [Self-Foveate: 通过多级焦点化增强无监督文本合成指令的多样性和难度](#self-foveate-通过多级焦点化增强无监督文本合成指令的多样性和难度)
  - [安装](#安装)
  - [快速开始](#快速开始)
  - [评估](#评估)
  - [引用](#引用)

## 安装

1. 克隆此仓库并导航到Self-Foveate文件夹
```bash
git clone https://github.com/Mubuky/Self-Foveate.git
cd Self-Foveate
```

2. 安装依赖项（Python 3.11）
```bash
pip install -r requirements.txt
```

## 快速开始

**指令合成：**
```bash
python self_foveate.py --config ./config/[dataset].yaml
```

以下是运行论文中指令合成阶段的命令：
```bash
# 🏠 SQuAD_2.5k
python self_foveate.py --config ./config/SQuAD_2.5k.yaml
# ❓ HotpotQA_2.5k
python self_foveate.py --config ./config/HotpotQA_2.5k.yaml
# 📚 FilmWiki
python self_foveate.py --config ./config/FilmWiki.yaml
```

## 评估
等待更新...


## 许可证 <!-- omit in toc -->

[![代码许可证](https://img.shields.io/badge/Code%20License-MIT-green.svg)](LICENSE)

本项目采用MIT许可证 - 详情请参阅LICENSE文件。


## 引用

如果您觉得我们的代码/论文有帮助，请考虑引用我们的论文📝并给我们星标⭐️！

```bibtex
@inproceedings{li-etal-2025-self-foveate,
    title = "Self-Foveate: Enhancing Diversity and Difficulty of Synthesized Instructions from Unsupervised Text via Multi-Level Foveation",
    author = "Li, Mingzhe  and
      Lu, Xin  and
      Zhao, Yanyan",
    booktitle = "Findings of the Association for Computational Linguistics: ACL 2025",
    month = jul,
    year = "2025",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.findings-acl.380/",
    pages = "7274--7289"
}
```

## 联系方式

如果您有任何问题，请随时联系 [李明哲](mailto:mzli@ir.hit.edu.cn)
