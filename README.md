<img src="https://raw.githubusercontent.com/nuremics/nuremics.github.io/main/images/banner.jpg" width="100%">
<p align="left">
  <img src="https://img.shields.io/badge/Python-3.9+-ffcd3b?style=flat&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/attrs-22.1.0+-000000?style=flat" />
  <img src="https://img.shields.io/badge/Pandas-2.1.1+-0b0153?style=flat&logo=pandas&logoColor=white" />
  <img src="https://img.shields.io/badge/NumPy-1.26.0+-4dabcf?style=flat&logo=numpy&logoColor=white" />
  <img src="https://img.shields.io/badge/termcolor-1.1.0+-0dbc5a?style=flat" />
  <img src="https://img.shields.io/badge/platformdirs-3.5+-364f87?style=flat" />
  <a href="https://nuremics.github.io/coverage"
     target="_blank"
     rel="noopener noreferrer">
    <img src="https://img.shields.io/badge/Coverage-83%25-magenta?style=flat"/>
  </a>
</p>

**nuRemics is an open-source Python framework for building software-grade scientific tools.**

🔬 Scientific agility — engineering rigor.<br>
🧩 Modular by design — no more siloed tools.<br>
📊 Parametric exploration — iterate without limits.<br>
📋 Full traceability — every experiment accounted for.<br>
📈 Built to scale — from lab to industry. <br>
🌐 Community-driven — innovation thrives together.

## Overview

The **nuRemics** framework provides a dedicated environment to build custom software tools designed for the automated production of scientific results at scale, ensuring systematic reproducibility and full traceability across every execution. This is achieved through a clear separation of concerns, organized into the following layered structure:
<br>

<p align="center">
  <img src="https://raw.githubusercontent.com/nuremics/nuremics.github.io/main/images/nuRemics_Overview.svg" width="80%">
</p>

**APP**

It is the execution engine where the core scientific logic is formalized and implemented in a codebase. It operates as a structured workflow composed of autonomous software processes (e.g., Process1-3) executed in a sequential order. Each software process encapsulates a specific stage of the computation and acts as an independent functional item.

**INPUTS**

It defines the entry points required by the application to function (e.g., Input1–6) and ensures that each input is routed to its respective software process, in order to satisfy the corresponding data requirements.

**OUTPUTS**

It defines the delivery points where results are produced during execution (e.g., Output1–4). Each software process generates its own outputs, which are either stored as final results or re-routed as inputs of subsequent software processes within the workflow.

**CONFIGURATION**

It orchestrates how the application is controlled by the operator across different study scenarios (e.g., Study1–2). For each study, the operator defines which inputs are _Fixed_ (constant throughout the study) and which are _Variable_ (changing between individual tests). This enables automated batch execution of multiple tests (e.g., Test1–3) by systematically updating the inputs.

**TRACEABILITY**

It automatically generates a structured directory tree (Study > Process > Test) where each output is stored within a hierarchy that directly links it back to the specific configuration that produced it. This provides a permanent, auditable record of every production run.

## Getting Started

🔗 [Get started with nuRemics](https://nuremics.github.io/getting-started)