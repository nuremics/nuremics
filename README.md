<img src="https://raw.githubusercontent.com/nuremics/nuremics.github.io/main/images/banner.jpg" width="100%">
<p align="left">
  <img src="https://img.shields.io/badge/Python-3.12+-ffcd3b?style=flat&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/attrs-24.1.0+-000000?style=flat" />
  <img src="https://img.shields.io/badge/Pandas-2.2.2+-0b0153?style=flat&logo=pandas&logoColor=white" />
  <img src="https://img.shields.io/badge/NumPy-2.0.1+-4dabcf?style=flat&logo=numpy&logoColor=white" />
  <img src="https://img.shields.io/badge/termcolor-3.0.1+-0dbc5a?style=flat" />
  <img src="https://img.shields.io/badge/GitPython-3.1.44+-f05030?style=flat&logo=git&logoColor=white" />
  <img src="https://img.shields.io/badge/pytest-8.4.0+-009fe3?style=flat&logo=pytest&logoColor=white" />
  <a href="https://nuremics.github.io/coverage">
    <img src="https://img.shields.io/badge/Coverage-84%25-magenta?style=flat"/>
  </a>
</p>

# NUREMICS®

**NUREMICS is an open-source Python framework for developing software-grade scientific workflows.**

🧠 Code like a scientist — build like an engineer.<br>
🧩 Modular workflows — no more tangled scripts.<br>
🧪 Parametric exploration — configuration over code.<br>
💾 Full traceability — everything written to disk.<br>
🛠️ Industrial mindset — R&D speed, software rigor.

[![Regarder la vidéo](https://img.youtube.com/vi/GbbZldfJHy0/0.jpg)](https://youtu.be/GbbZldfJHy0)

## Foreword

The **NUREMICS** project is organized into two complementary repositories:

- **`nuremics`**  _(current repository)_: This repository is the core Python library, installable via `pip install`. It provides the foundational components to create modular and extensible software workflows.

- **`nuremics-labs`**:
This repository contains examples of end-user applications built using the **NUREMICS** framework. It is intended to be **forked** by developers to initiate their own `nuremics-labs` project and build custom applications tailored to their specific use cases.

Developers are encouraged to treat `nuremics` as the core engine, and to use `nuremics-labs` as a starting point for developing and maintaining their own scientific software built on top of the **NUREMICS** framework.

## Project Philosophy

**NUREMICS** is built with the ambition of bringing robust software engineering practices into Python-driven scientific research and development.

While Python has become the de facto standard for scientific programming, its use in R&D environments is often limited to ad-hoc scripts or notebooks. This leads to critical limitations: unclear definition of inputs, algorithms, and outputs; hard-coded parameters that hinder reproducibility; and inefficient workflows for exploring parameter spaces. As a result, scientific studies are often conducted in a “one-shot” manner, making them difficult to reproduce or extend. Output data is rarely traceable in a structured way, and codebases suffer from poor modularity, limited reusability, and frequent duplication. These challenges are compounded when teams grow, as scripts and notebooks are difficult to scale and maintain collaboratively, slowing down innovation and increasing the risk of undetected errors.

In regulated industries where scientific results directly support product development (e.g., MedTech, Biotech, Aerospace), such fragility can have severe consequences. This is also why many of these industries remain hesitant to adopt Python and its powerful open ecosystem, due to concerns about reliability and long-term maintainability.

In this landscape, **NUREMICS** emerges as a unifying framework designed to address these challenges: it provides a rigorous development structure that empowers scientists, engineers, and researchers to deliver high-quality scientific outcomes, and take their research to the next level. By enabling the safe integration of tools from the Python ecosystem, **NUREMICS** supports the engineering of domain-specific software tailored for scientific exploration and reproducibility, while upholding the discipline and maintainability required in high-stakes industrial environments.

Inspired by **IEC 62304**, a standard originally developed for the engineering of medical device software, **NUREMICS** promotes structured, layered software development through clearly defined architectural components: systems, items, and units. This organization fosters clarity, modularity, and maintainability, while remaining well-suited to the iterative, exploratory nature of scientific development in Python. Although **NUREMICS** does not aim for full compliance with **IEC 62304**, it selectively incorporates its most relevant principles, striking a pragmatic balance between engineering rigor and the agility required in fast-paced research environments.

## Getting Started

To start using the **NUREMICS** framework, head over to the [`nuremics-labs`](https://github.com/nuremics/nuremics-labs) repository.