<p align="right"><a href="README.md">English</a></p>
<img src="assets/hero.svg" alt="FrameBudget" width="100%">

# FrameBudget

**Comparez des réglages H.264 sur plusieurs extraits, choisissez un compromis taille–qualité mesuré et vérifiez l’encodage final.**

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
