<img src="https://raw.githubusercontent.com/julien-siguenza/nuremics-data/main/assets/banner.jpg" alt="NUREMICS Banner" width="100%">

# NUREMICS®

**NUREMICS®** is an open-source Python™ framework for developing customizable scientific workflows.

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/attrs-24.1.0-blueviolet?style=flat" />
  <img src="https://img.shields.io/badge/Pandas-2.2.2-150458?style=flat&logo=pandas&logoColor=white" />
  <img src="https://img.shields.io/badge/NumPy-2.0.1-013243?style=flat&logo=numpy&logoColor=white" />
  <img src="https://img.shields.io/badge/termcolor-3.0.1-8A2BE2?style=flat" />
</p>

## Foreword

The **NUREMICS®** project is organized into two complementary repositories:

- **`nuremics`**  _(current repository)_: This repository is the core Python library, installable via `pip install`. It provides the foundational components to create modular and extensible software workflows.

- **[`nuremics-apps`](https://github.com/nuremics/nuremics-apps)**: This repository contains examples of end-user applications built using the **NUREMICS®** framework. It is intended to be **forked** by developers to initiate their own `nuremics-apps` project and build custom applications tailored to their specific use cases.

Developers are encouraged to treat `nuremics` as the core engine, and to use `nuremics-apps` as a starting point for developing and maintaining their own scientific software built on top of the **NUREMICS®** framework.

## Project Philosophy

**NUREMICS®** is built with the ambition of bringing robust software engineering practices into Python-driven scientific research and development.

While traditional R&D environments often favor rapid iteration at the expense of software quality and sustainability, many teams find themselves constrained by ad-hoc, script-based workflows that limit both scientific exploration and the ability to scale. **NUREMICS®** was designed to address this challenge by providing a framework that enables scientists, engineers, and researchers to develop faster, explore deeper, and produce more robust, reproducible, scalable, and insightful scientific outcomes.

Inspired by **IEC 62304**, a standard originally developed for the engineering of medical device software, **NUREMICS®** promotes structured, layered software development through clearly defined architectural components: systems, items, and units. This organization fosters clarity, modularity, and maintainability, while remaining well-suited to the iterative, exploratory nature of scientific development in Python.

Although **NUREMICS®** does not aim for full compliance with **IEC 62304**, it selectively incorporates its most relevant principles, offering a pragmatic balance between engineering rigor and the flexibility demanded by research environments.

## Architecture Overview

The software architecture of **NUREMICS®** is illustrated in the diagram below. As previously mentioned, it follows the layered structure recommended by the **IEC 62304** standard, distinguishing between _software systems_, _software items_, and _software units_. This representation provides a clear, high-level view of how the different software components of the project are organized, and how they interact within a structured yet flexible development framework. It also highlights the relationship between the core framework (`nuremics`) and its domain-specific applications (`nuremics-apps`), emphasizing the modular and extensible nature of the overall architecture.

In the context of **NUREMICS®**:

- A _software unit_ corresponds to a single, testable function. It is the smallest building block of logic.

- A _software item_ typically takes the form of a Python class that encapsulates related functions (units) to serve a specific purpose.

- A _software system_ refers to a complete application designed to be executed by an end user, replacing traditional scripts or notebooks.

<img src="https://raw.githubusercontent.com/julien-siguenza/nuremics-data/main/assets/architecture.svg" alt="NUREMICS Architecture" width="100%">

In practice, the core framework `nuremics` is composed of three foundational _software items_:

- The `Process` class defines a generic process component. It provides a flexible base structure that can be extended to implement domain-specific processes within `nuremics-apps`.

- The `Workflow` class orchestrates the execution of multiple processes in a defined sequential order. It encapsulates the coordination logic and manages the progression of tasks throughout the workflow.

- The `Application` class is the top-level component. It instantiates and executes a workflow, acting as the main entry point for any end user application developed within `nuremics-apps`.

In `nuremics-apps`, two main types of software components are developed to build domain-specific applications:

- **Processes** (_software items_) — such as `Proc1, Proc2, ..., ProcX` — are implemented by subclassing the core `Process` class. Each process is defined as a class that encapsulates several functions (_software units_), typically executed sequentially within its `__call__` method. This design enables the creation of independent, reusable process items that can be executed on their own or integrated into larger workflows.

- **Applications** (_software systems_) — such as `APP1, APP2, ..., APPX` — import and assemble the required process items, executing them in a defined order within a `Workflow`, by instantiating the `Application` class. This modular architecture promotes flexibility and reusability, allowing the same process items to be used across multiple applications.

## Get Started

To begin your coding journey with the **NUREMICS®** framework, you can now head over to the [`nuremics-apps`](https://github.com/nuremics/nuremics-apps) repository. There, you'll learn how to build domain-specific processes and applications, and how to use them as an end user.