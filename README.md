# Mathesis: Towards Formal Theorem Proving from Natural Languages

Most LLM-based theorem provers have long been constrained by the need for expert-written formal statements as inputs, limiting their applicability to real-world problems expressed in natural language. We tackle this gap with **Mathesis**, the first **end-to-end theorem proving** pipeline processing informal problem statements.
- To enhance the formalization ability of natural language problems, we introduce **Mathesis-Autoformalizer**, which is trained using a novel reinforcement learning approach that integrates local alignment via GRPO and global alignment via DPO. We refer to this technique as Hierarchical Preference Optimization.
- We propose **LeanScorer**, a novel evaluation method combining _LLM-based analysis_ with _Sugeno Fuzzy Integral_ for nuanced formalization assessment.
- We also propose a **Mathesis-Prover**, which generates formal proofs from the formalized statements.
- To evaluate the real-world applicability of end-to-end formal theorem proving, we introduce **Gaokao-Formal**, a benchmark of 488 complex problems from China’s national college entrance exam.

<p align="center">
    <br>
    <img src="figures/theorem_proving_results.jpg" width="600"/>
    <br>
</p>

## 🔥🔥 Updates
* 2025/06/10: We released our [paper](https://arxiv.org/pdf/2506.07047) on arXiv! 


## ⚠️⚠️ Ongoing Improvement
This end-to-end theorem proving pipeline marks a significant step forward. We will continue refining our models and techniques to improve performance. For applications requiring strict accuracy, expert review is highly recommended to ensure reliability.

<p align="center">
    <br>
    <img src="figures/pipeline.jpg" width="900"/>
    <br>
</p>

## Mathesis-Autoformalizer
- To formalize mathematical problem statements from natural language into formal Lean 4 code, we introduce Mathesis-Autoformalizer, the first autoformalization model trained with reinforcement learning. It generates syntactically valid and semantically faithful formal statements from natural language, making it well-suited for real-world settings where accurate formalization is critical.

## Leanscorer
- To enable a more fine-grained and reliable assessment, we propose LeanScorer, a novel framework yielding a continuous correctness score (0 to 1). This score allows for dynamic adjustment of decision thresholds according to task-specific precision/recall requirements.
<p align="center">
    <br>
    <img src="figures/leanscorer.jpg" width="900"/>
    <br>
</p>


## Citation
Please cite our paper if you use the data or code in this repo.
```
@misc{xuejun2025mathesisformaltheoremproving,
      title={Mathesis: Towards Formal Theorem Proving from Natural Languages}, 
      author={Yu Xuejun and Jianyuan Zhong and Zijin Feng and Pengyi Zhai and Roozbeh Yousefzadeh and Wei Chong Ng and Haoxiong Liu and Ziyi Shou and Jing Xiong and Yudong Zhou and Claudia Beth Ong and Austen Jeremy Sugiarto and Yaoxi Zhang and Wai Ming Tai and Huan Cao and Dongcai Lu and Jiacheng Sun and Qiang Xu and Shen Xin and Zhenguo Li},
      year={2025},
      eprint={2506.07047},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2506.07047}, 
}
```
