<img src="https://raw.githubusercontent.com/julien-siguenza/nuremics-data/main/assets/banner.jpg" alt="NUREMICS Banner" width="100%">

# NUREMICS®

**NUREMICS®** is an open-source Python™ framework for developing customizable scientific workflows.

## Foreword

The **NUREMICS®** project is organized into two complementary repositories:

- **`nuremics`**  _(current repository)_: This repository is the core Python library, installable via `pip install`. It provides the foundational components to create modular and extensible software workflows.

- **[`nuremics-apps`](https://github.com/nuremics/nuremics-apps)**: This repository contains examples of end-user applications built using the **NUREMICS®** framework. It is intended to be **forked** by developers to initiate their own `nuremics-apps` project and build custom applications tailored to their specific use cases.

Readers are encouraged to begin their exploration of the **NUREMICS®** project with the `nuremics` repository to understand the core framework and its foundational building blocks, before diving into the examples and applications provided in `nuremics-apps`.

Developers are invited to treat `nuremics` as the core engine, and to use `nuremics-apps` as a starting point for developing and maintaining their own scientific software built on top of the **NUREMICS®** framework.

## Project Philosophy

**NUREMICS®** is built with the ambition of bringing robust software engineering practices into Python-driven scientific research and development.

While traditional R&D environments often favor rapid iteration at the expense of software quality and sustainability, many teams find themselves constrained by ad-hoc, script-based workflows that limit both scientific exploration and the ability to scale. **NUREMICS®** was designed to address this challenge by providing a framework that enables scientists, engineers, and researchers to develop faster, explore deeper, and produce more robust, reproducible, scalable, and insightful scientific outcomes.

Inspired by **IEC 62304**, a standard originally developed for the engineering of medical device software, **NUREMICS®** promotes structured, layered software development through clearly defined architectural components: systems, items, and units. This organization fosters clarity, modularity, and maintainability, while remaining well-suited to the iterative, exploratory nature of scientific development in Python.

Although **NUREMICS®** does not aim for full compliance with **IEC 62304**, it selectively incorporates its most relevant principles, offering a pragmatic balance between engineering rigor and the flexibility demanded by research environments.

## Architecture Overview

<img src="https://raw.githubusercontent.com/julien-siguenza/nuremics-data/main/assets/architecture.svg" alt="NUREMICS Architecture" width="100%">