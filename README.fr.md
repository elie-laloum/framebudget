<p align="right"><a href="README.md">English</a></p>
<img src="assets/cover.svg" alt="FrameBudget" width="100%">

<!-- project badges -->
<p>
<a href="README.md"><img src="https://img.shields.io/badge/version-0.1.0-24334b?style=flat-square" alt="Version 0.1.0"></a>
<a href="https://github.com/elie-laloum/framebudget/actions/workflows/ci.yml"><img src="https://github.com/elie-laloum/framebudget/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-ffcf83?style=flat-square&amp;labelColor=172033" alt="MIT"></a>
<a href="README.md#see-it-in-action"><img src="https://img.shields.io/badge/demo-watch-ffcf83?style=flat-square&amp;labelColor=172033" alt="Watch the demo"></a>
</p>
<p>
<a href="README.md#quick-start"><img src="https://img.shields.io/badge/-Python%203.10%2B-ffcf83?style=flat-square&amp;labelColor=172033&amp;logo=python&amp;logoColor=white" alt="Python 3.10+"></a>
<a href="README.md#quick-start"><img src="https://img.shields.io/badge/-FFmpeg-ffcf83?style=flat-square&amp;labelColor=172033&amp;logo=ffmpeg&amp;logoColor=white" alt="FFmpeg"></a>
<a href="README.md#quick-start"><img src="https://img.shields.io/badge/-VMAF-ffcf83?style=flat-square&amp;labelColor=172033" alt="VMAF"></a>
</p>
<!-- /project badges -->

# FrameBudget

**Comparez des réglages H.264 sur plusieurs extraits, choisissez un compromis taille–qualité mesuré et vérifiez l’encodage final.**

## Voir la démo

<a href="assets/demo.mp4"><img src="assets/demo.gif" alt="FrameBudget — démonstration enregistrée" width="100%"></a>

<sub>Démo réellement exécutée, rejouée avec des annotations et un rythme adapté à la lecture.</sub>

[Vidéo MP4](assets/demo.mp4) · [Reproduire la démo](docs/demo.md)

## Essayer la version 0.1

```sh
git clone https://github.com/elie-laloum/framebudget.git
cd framebudget
python -m pip install .
python -m unittest discover -s tests
python examples/demo.py
```

La démonstration génère une vidéo de trois secondes, compare trois réglages avec FFmpeg et VMAF, puis vérifie la qualité du fichier final.

## Utilisation et périmètre

L’outil explore une grille CRF/preset, mesure VMAF ou PSNR et produit un rapport JSON/HTML. FFmpeg, ffprobe et libx264 sont nécessaires ; VMAF nécessite libvmaf. La version 0.1 vise les vidéos SDR avec un seul flux vidéo et une sortie MKV. Les extraits ne garantissent pas la qualité du fichier entier : activez `--verify-quality` pour la mesurer.

[Configuration complète et contrat de l’API](README.md#use-it-on-your-project) · [Limites détaillées](README.md#boundaries) · [Contribuer](CONTRIBUTING.md)

La documentation technique de référence est en anglais. Cette traduction présente le démarrage et le périmètre de la version actuelle.

[GitLab origin](https://gitlab.elielaloum.com/elielaloum/framebudget) · [GitHub mirror](https://github.com/elie-laloum/framebudget)

Le dépôt GitLab privé contient la source de référence ; GitHub en est le miroir public.
