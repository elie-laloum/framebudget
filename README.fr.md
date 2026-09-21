<p align="center"><a href="README.md">English</a> · <strong>Français</strong></p>

<p align="center"><img src="assets/hero.fr.svg" alt="FrameBudget — Trouver les réglages adaptés à vos contraintes." width="100%"></p>

# FrameBudget

**Trouvez l'encodage adapté à vos contraintes.**

Un projet d'optimiseur FFmpeg open source pour explorer les compromis entre taille de fichier, qualité mesurée et temps d'encodage.

> **En développement.** Ce dépôt contient la spécification et la documentation initiales. Aucune version exécutable n’est encore publiée.


**Dépôt d’origine : [GitLab](https://gitlab.elielaloum.com/elielaloum/framebudget)** · [Miroir public GitHub](https://github.com/elie-laloum/framebudget). Le dépôt GitLab est privé ; son accès nécessite une autorisation. Les modifications du code sont intégrées dans GitLab puis synchronisées vers GitHub.


## Rendez les décisions d'encodage compréhensibles

Choisissez une cible de qualité et un budget de recherche. FrameBudget doit tester des réglages sur des segments représentatifs, comparer les résultats et expliquer le compromis retenu avant d'encoder le fichier complet.

```text
Inspection → Échantillons → Exploration → Comparaison → Encodage → Vérification
```

## Périmètre initial

- CLI Python pilotant FFmpeg et ffprobe.
- Vidéo SDR, résolution conservée et encodage libx264.
- Recherche bornée parmi des valeurs de CRF et des presets.
- Évaluation VMAF sur échantillons et vérification complète de qualité facultative.
- Rapports JSON et HTML : réglages, mesures, estimations et décisions.

Le budget de recherche limite l'exploration ; il ne garantit pas la durée totale d'encodage. La qualité des échantillons ne garantit pas celle de toute la vidéo. Si aucun candidat ne respecte les contraintes, l'outil doit l'indiquer.

## Ce qui doit faire son intérêt

[ab-av1](https://github.com/alexheretic/ab-av1) propose déjà une recherche de CRF et des estimations de taille et de temps. L'angle proposé pour FrameBudget est une exploration sous budget avec comparaison explicite de la qualité, de la taille et du temps. Cette différence doit être démontrée par des comparaisons reproductibles.

## La démonstration à livrer

Un corpus vidéo redistribuable, les résultats des candidats, un graphique des compromis, les réglages choisis et un fichier final vérifié. Documenter le matériel, les versions, les échantillons et le coût total de recherche. [VMAF](https://github.com/Netflix/vmaf) est une métrique, pas une garantie d'identité visuelle.

## Conditions de publication

Préserver les originaux, vérifier le décodage et la durée, documenter le traitement audio et des sous-titres, distinguer mesures et estimations. Étendre au HDR et à d'autres encodeurs après validation du périmètre initial.

## Contribuer au projet

Premières contributions utiles : vidéos redistribuables, reproductions des benchmarks et scènes difficiles. Les instructions d'installation suivront la vérification de la configuration FFmpeg prise en charge.


---

[Feuille de route](ROADMAP.md) · [Contribuer](CONTRIBUTING.md) · [Licence MIT](LICENSE)
