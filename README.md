# SECO—Generation of Punning Riddles in Portuguese

This repository contains a partial implementation of the SECO system, described in the papers "Exploring Lexical-Semantic Knowledge in the Generation of Novel Riddles in Portuguese" and "Explorando a Geração Automática de Adivinhas em Português". We include exclusively the _generation_ of riddles based on Antonymy pairs.

## How to install

If you want to use [uv](https://astral.sh/blog/uv), you can install the requirements with the following command:

```bash
uv sync
```

Otherwise, you can install the requirements with pip:

```bash
pip install -r requirements.txt
```

Please be aware to use Python 3.9.

## How to run

To generate all possible riddles, you can run the following command:

```bash
python main.py \
    -a aglut_lexico_v2.txt \
    -f formas_cetempublico.txt \
    -l triplos_redun2_10recs.txt \
    -m MorphoBR \
    -vv
```

Plase be aware that you need to have some files files locally to run the system:

- The list of nominal compounds by [Ramisch et al. (2016)](https://aclanthology.org/P16-2026/): `aglut_lexico_v2.txt`;
- A word frequency list from CETEMPúblico: [`formas_cetempublico.txt`](https://www.linguateca.pt/acesso/corpus.php?corpus=CETEMPUBLICO);
- A list of triplets with lexical relations from Onto.[]()PT: [`triplos_redun2_10recs.txt`](http://ontopt.dei.uc.pt/index.php?sec=download_outros);
- The morphological analysis dictionary [`MorphoBR`](https://github.com/LR-POR/MorphoBr).

With this, you should have all possible riddles generated to a `results.json` file.

## How to cite

If you use this code, please cite the following paper:

```bibtex
@inproceedings{InacioGoncaloOliveira2024a,
    title     = {Generation of {{Punning Riddles}} in {{Portuguese}} with {{Prompt Chaining}}},
    booktitle = {Proceedings of the 15th {{International Conference}} on {{Computational Creativity}} ({{ICCC}}'24)},
    author    = {In{\'a}cio, Marcio and Gon{\c c}alo Oliveira, Hugo},
    year      = {2024},
    month     = jun,
    publisher = {Association for Computational Creativity (ACC)},
    address   = {J{\"o}nk{\"o}ping},
    url       = {https://computationalcreativity.net/iccc24/full-papers/ICCC24\_paper\_143.pdf}
}
```
