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

- **`nuremics-apps`**: This repository contains examples of end-user applications built using the **NUREMICS®** framework. It is intended to be **forked** by developers to initiate their own `nuremics-apps` project and build custom applications tailored to their specific use cases.

Developers are encouraged to treat `nuremics` as the core engine, and to use `nuremics-apps` as a starting point for developing and maintaining their own scientific software built on top of the **NUREMICS®** framework.

## Project Philosophy

**NUREMICS®** is built with the ambition of bringing robust software engineering practices into Python-driven scientific research and development.

While Python has become the de facto standard for scientific computing, its use in R&D environments is often limited to ad-hoc scripts or notebooks. This leads to critical limitations: unclear definition of inputs, algorithms, and outputs; hard-coded parameters that hinder reproducibility; and inefficient workflows for exploring parameter spaces. As a result, scientific studies are often conducted in a “one-shot” manner, making them difficult to reproduce or extend. Output data is rarely traceable in a structured way, and codebases suffer from poor modularity, limited reusability, and frequent duplication. These challenges are compounded when teams grow, as scripts and notebooks are difficult to scale and maintain collaboratively, slowing down innovation and increasing the risk of undetected errors.

In regulated industries where scientific results directly support product development (e.g., MedTech, Biotech, Aerospace), such fragility can have severe consequences. This is also why many of these industries remain hesitant to adopt Python and its powerful open ecosystem, due to concerns about reliability and long-term maintainability.

In this landscape, **NUREMICS®** emerges as a unifying framework designed to address these challenges: it provides a rigorous development structure that empowers scientists, engineers, and researchers to deliver high-quality scientific outcomes, and take their research to the next level. By enabling the safe integration of tools from the Python ecosystem, **NUREMICS®** supports the engineering of domain-specific scientific software with the discipline, testability, and maintainability required in high-stakes industrial environments.

Inspired by **IEC 62304**, a standard originally developed for the engineering of medical device software, **NUREMICS®** promotes structured, layered software development through clearly defined architectural components: systems, items, and units. This organization fosters clarity, modularity, and maintainability, while remaining well-suited to the iterative, exploratory nature of scientific development in Python.

Although **NUREMICS®** does not aim for full compliance with **IEC 62304**, it selectively incorporates its most relevant principles, striking a pragmatic balance between engineering rigor and the agility required in fast-paced research environments.

## Architecture Overview

The software architecture of **NUREMICS®** is illustrated in the diagram below. As previously mentioned, it follows the layered structure recommended by the **IEC 62304** standard, distinguishing between _software systems_, _software items_, and _software units_. This representation provides a clear, high-level view of how the different software components of the project are organized, and how they interact within a structured yet flexible development framework. It also highlights the relationship between the core framework (`nuremics`) and its domain-specific applications (`nuremics-apps`), emphasizing the modular and extensible nature of the overall architecture.

In the context of **NUREMICS®**:

- A _software unit_ corresponds to a single, testable function. It is the smallest building block of logic.

- A _software item_ typically takes the form of a Python class that encapsulates related functions (units) to serve a specific purpose.

- A _software system_ refers to a complete application designed to be executed by an end-user, replacing traditional scripts or notebooks.

<img src="https://raw.githubusercontent.com/julien-siguenza/nuremics-data/main/assets/architecture.svg" alt="NUREMICS Architecture" width="100%">

In practice, the core framework `nuremics` is composed of three foundational _software items_:

- The `Process` class defines a generic process component. It provides a flexible base structure that can be extended to implement domain-specific processes within `nuremics-apps`.

- The `Workflow` class orchestrates the execution of multiple processes in a defined sequential order. It encapsulates the coordination logic and manages the progression of tasks throughout the workflow.

- The `Application` class is the top-level component. It instantiates and executes a workflow, acting as the main entry point for any end-user application developed within `nuremics-apps`.

In `nuremics-apps`, two main types of software components are developed to build domain-specific applications:

- **Procs** (_software items_) — such as `Proc1, Proc2, ..., ProcX` — are implemented by subclassing the core `Process` class. Each **Proc** is defined as a class that encapsulates several functions (_software units_), typically executed sequentially within its `__call__` method. This design enables the creation of independent, reusable **Procs** that can be executed on their own or integrated into larger workflows.

- **Apps** (_software systems_) — such as `APP1, APP2, ..., APPX` — are the end-user-facing software applications. They import and assemble the required **Procs**, executing them in a defined order through the `Workflow` class, by instantiating the `Application` class. This modular architecture promotes flexibility and reusability, allowing the same **Procs** to be used across multiple **Apps** tailored to different scientific purposes.

## Design Patterns

Let’s briefly introduce the core design patterns behind **Procs** and **Apps** in **NUREMICS®**.

### Proc

A **Proc** can be seen as an algorithmic box which processes some input data and produces corresponding output data.

The input data typically fall into two main categories:

- **Input parameters**: Scalar values such as `float`, `int`, `bool`, or `str`.

- **Input paths**: Files or folders provided as `Path` objects (from Python's `pathlib` module), pointing to structured data on disk.

```mermaid
erDiagram
  **Parameters** ||--|| **Inputs** : provides
  **Paths** ||--|| **Inputs** : provides

  **Parameters** {
    float param1
    int param2
    bool param3
  }
  **Paths** {
    file path1 "txt"
  }
```

As previously mentioned, the algorithmic box of the **Proc** is a class composed of functions (units) called sequentially with its `__call__` method.

```mermaid
erDiagram
  **Parameters** ||--|| **Inputs** : provides
  **Paths** ||--|| **Inputs** : provides
  **Inputs** ||--|| **MyProc** : feeds

  **Parameters** {
    float param1
    int param2
    bool param3
  }
  **Paths** {
    file path1 "txt"
  }
  **MyProc** {
    function operation1()
    function operation2()
    function operation3()
    function operation4()
  }
```

Output data are typically expressed as `Path` objects as well, corresponding to files or folders written to disk during the execution of the **Proc**.

```mermaid
erDiagram
  **Parameters** ||--|| **Inputs** : provides
  **Paths** ||--|| **Inputs** : provides
  **Inputs** ||--|| **MyProc** : feeds
  **MyProc** ||--|| **Outputs** : generates

  **Parameters** {
    float param1
    int param2
    bool param3
  }
  **Paths** {
    file path1 "txt"
  }
  **MyProc** {
    function operation1()
    function operation2()
    function operation3()
    function operation4()
  }
  **Outputs** {
    file out1 "csv"
    folder out2 "_"
  }
```

For the sake of example, let's define another **Proc** considering the same structure.

```mermaid
erDiagram
  **Parameters** ||--|| **Inputs** : provides
  **Paths** ||--|| **Inputs** : provides
  **Inputs** ||--|| **AnotherProc** : feeds
  **AnotherProc** ||--|| **Outputs** : generates

  **Parameters** {
    int param1
    str param2
  }
  **Paths** {
    file path1 "csv"
    folder path2 "_"
  }
  **AnotherProc** {
    function operation1()
    function operation2()
    function operation3()
  }
  **Outputs** {
    file out1 "vtk"
  }
```

### App

A final end-user **App** can be built by plugging together previously implemented **Procs**, and specifying their sequential order of execution within the workflow.

```mermaid
flowchart BT
  **MyProc** e1@--1--o **MY_APP**
  **AnotherProc** e2@--2--o **MY_APP**
  e1@{ animate: true }
  e2@{ animate: true }
```

Each **Proc** integrated into the **App** defines its own set of inputs and outputs, specific to its internal algorithmic logic. When these **Procs** are assembled into a workflow, the **App** itself exposes a higher-level set of inputs and outputs. These define the I/O interface presented to the end-user, who provides the necessary input data and retrieves the final results upon execution.

The assembly step is performed through a mapping between the internal I/O data of each **Proc** and the global I/O interface of the **App**. This mapping mechanism serves multiple purposes:

- It defines which data are exposed to the end-user (and how they are displayed) and which remain internal to the workflow.

- It manages the data dependencies between **Procs**, when the output of one **Proc** is used as input for another.

This notably ensures a coherent and seamless management of data across the workflow, while delivering a clean and focused I/O interface tailored to the user's needs.

The mapping between a **Proc** and the **App** starts by specifying which **Proc** input parameters are exposed to the end-user, and how they are labeled in the **App** input interface.

```mermaid
erDiagram
  **MY_APP** ||--|| **user_params** : mapping
  **user_params** ||--|| **MyProc** : mapping

  **user_params** {
    float param1 "parameter1"
    bool param3 "parameter2"
  }
```

The **Proc** input parameters that remain internal to the workflow are assigned fixed values directly within the mapping definition, without being exposed to the end-user.

```mermaid
erDiagram
  **MY_APP** ||--|| **user_params** : mapping
  **MY_APP** ||--|| **hard_params** : mapping
  **user_params** ||--|| **MyProc**: mapping
  **hard_params** ||--|| **MyProc**: mapping

  **user_params** {
    float param1 "parameter1"
    bool param3 "parameter2"
  }
  **hard_params** {
    int param2 "14"
  }
```

The **Proc** input paths that need to be provided by the end-user are specified by defining the expected file or folder names within the **App** input interface.

```mermaid
erDiagram
  **MY_APP** ||--|| **user_params** : mapping
  **MY_APP** ||--|| **hard_params** : mapping
  **MY_APP** ||--|| **user_paths** : mapping
  **user_params** ||--|| **MyProc** : mapping
  **hard_params** ||--|| **MyProc** : mapping
  **user_paths** ||--|| **MyProc** : mapping

  **user_params** {
    float param1 "parameter1"
    bool param3 "parameter2"
  }
  **hard_params** {
    int param2 "14"
  }
  **user_paths** {
    file path1 "input1.txt"
  }
```

The **Proc** input paths can also be mapped to output paths produced by a previous **Proc** within the workflow (although this does not apply here, as we are currently focusing on the first **Proc** in the workflow).

```mermaid
erDiagram
  **MY_APP** ||--|| **user_params** : mapping
  **MY_APP** ||--|| **hard_params** : mapping
  **MY_APP** ||--|| **user_paths** : mapping
  **MY_APP** ||--|| **required_paths** : mapping
  **user_params** ||--|| **MyProc** : mapping
  **hard_params** ||--|| **MyProc** : mapping
  **user_paths** ||--|| **MyProc** : mapping
  **required_paths** ||--|| **MyProc** : mapping

  **user_params** {
    float param1 "parameter1"
    bool param3 "parameter2"
  }
  **hard_params** {
    int param2 "14"
  }
  **user_paths** {
    file path1 "input1.txt"
  }
  **required_paths** {
    _ _ "_"
  }
```

Finally, the **Proc** output paths are specified by indicating the name of the file(s) or folder(s) that will be written by the **Proc** during the workflow execution.

```mermaid
erDiagram
  **MY_APP** ||--|| **user_params** : mapping
  **MY_APP** ||--|| **hard_params** : mapping
  **MY_APP** ||--|| **user_paths** : mapping
  **MY_APP** ||--|| **required_paths** : mapping
  **MY_APP** ||--|| **output_paths** : mapping
  **user_params** ||--|| **MyProc** : mapping
  **hard_params** ||--|| **MyProc** : mapping
  **user_paths** ||--|| **MyProc** : mapping
  **required_paths** ||--|| **MyProc** : mapping
  **output_paths** ||--|| **MyProc** : mapping

  **user_params** {
    float param1 "parameter1"
    bool param3 "parameter2"
  }
  **hard_params** {
    int param2 "14"
  }
  **user_paths** {
    file path1 "input1.txt"
  }
  **required_paths** {
    _ _ "_"
  }
  **output_paths** {
    file out1 "output1.csv"
    folder out2 "output2"
  }
```

Let's now assemble the second **Proc** to be executed by the **App** within the workflow, by establishing a dependency: the output data produced by the first **Proc** will serve as input data for this second one.

```mermaid
erDiagram
  **MY_APP** ||--|| **user_params** : mapping
  **MY_APP** ||--|| **hard_params** : mapping
  **MY_APP** ||--|| **user_paths** : mapping
  **MY_APP** ||--|| **required_paths** : mapping
  **MY_APP** ||--|| **output_paths** : mapping
  **user_params** ||--|| **AnotherProc** : mapping
  **hard_params** ||--|| **AnotherProc** : mapping
  **user_paths** ||--|| **AnotherProc** : mapping
  **required_paths** ||--|| **AnotherProc** : mapping
  **output_paths** ||--|| **AnotherProc** : mapping

  **user_params** {
    int param1 "parameter3"
    str param2 "parameter4"
  }
  **hard_params** {
    _ _ "_"
  }
  **user_paths** {
    folder path2 "input2"
  }
  **required_paths** {
    file path1 "output1.csv"
  }
  **output_paths** {
    file out1 "output3.vtk"
  }
```

Once all **Procs** have been assembled into the **App**, the final I/O interface presented to the end-user emerges.

```mermaid
flowchart LR
  subgraph **INPUTS**
    direction TB

    subgraph **Paths**
      direction LR
      path1["input1.txt _(file)_"]
      path2["input2 _(folder)_"]
    end

    subgraph **Parameters**
      direction LR
      param1["parameter1 _(float)_"]
      param2["parameter2 _(bool)_"]
      param3["parameter3 _(int)_"]
      param4["parameter4 _(str)_"]
    end
  end

  subgraph **OUTPUTS**
    direction RL
    out1["output1.csv _(file)_"]
    out2["output2 _(folder)_"]
    out3["output3.vtk _(file)_"]
  end

  **INPUTS** --> MY_APP["**MY_APP**"]
  MY_APP --> **OUTPUTS**
```

## Usability

The **Apps** built with **NUREMICS®** come with a lean and pragmatic user interface by design. No flashy GUI, but instead, the focus is on simplicity and efficiency:

- An input database that the operator completes by editing configuration files and uploading the required input files and folders.

- A terminal interface that provides informative feedback at each execution, clearly indicating what the **App** is doing and what actions are expected from the operator.

- An output database that stores all results in a well-structured and traceable folder hierarchy.

```mermaid
sequenceDiagram
    actor Operator
    Operator->>MY_APP: Execution
    MY_APP->>INPUTS: Initialize database
    MY_APP->>Operator: Terminal feedback
    Operator->>INPUTS: Complete database
    Operator->>MY_APP: Execution
    MY_APP->>INPUTS: Read database
    MY_APP->>OUTPUTS: Write database
    MY_APP->>Operator: Terminal feedback
    Operator->>OUTPUTS: Access results
```

This streamlined approach prioritizes clarity, control, and reproducibility, making each **App** built with **NUREMICS®** well-suited for both direct interaction by end-users and seamless integration into larger software ecosystems. In such environments, **NUREMICS®** can operate as a backend computational engine, interacting programmatically with other tools (such as web applications) that provide their own user interfaces.

### Configuration

When running an **App**, the operator first defines a set of studies aimed at exploring the **INPUTS** space and analyzing the outcomes in the **OUTPUTS** space.

```mermaid
flowchart LR
    Study1
    Study2
```

The operator then configures each study by selecting which inputs stay constant _(Fixed)_ and which ones change _(Variable)_ across the various experiments.

```mermaid
flowchart LR

  subgraph Fixed1["**Fixed**"]
    direction TB

    subgraph Paths_Fixed1["**Paths**"]
      direction LR
      path1_1["input1.txt"]
    end

    subgraph Parameter_Fixed1["**Parameters**"]
      direction LR
      param1_1["parameter1"]
      param2_1["parameter2"]
      param4_1["parameter4"]
    end
  end

  subgraph Variable1["**Variable**"]
    direction TB

    subgraph Paths_Variable1["**Paths**"]
      direction LR
      path2_1["input2"]
    end

    subgraph Parameter_Variable1["**Parameters**"]
      direction LR
      param3_1["parameter3"]
    end
  end

  Study1 --> Fixed1
  Study1 --> Variable1

  subgraph Fixed2["**Fixed**"]
    direction TB

    subgraph Paths_Fixed2["**Paths**"]
      direction LR
      path1_2["input1.txt"]
      path2_2["input2"]
    end

    subgraph Parameter_Fixed2["**Parameters**"]
      direction LR
      param3_2["parameter3"]
      param4_2["parameter4"]
    end
  end

  subgraph Variable2["**Variable**"]
    direction TB

    subgraph Paths_Variable2["**Paths**"]
      direction LR
      no_path["_"]
    end

    subgraph Parameter_Variable2["**Parameters**"]
      direction LR
      param1_2["parameter1"]
      param2_2["parameter2"]
    end
  end

  Study2 --> Fixed2
  Study2 --> Variable2
```

### Settings

To conduct experiments, the operator assigns values for both fixed and variable inputs: fixed inputs remain constant across all experiments _(Common)_, while variable inputs are adjusted from one experiment to another _(Test1, Test2, ...)_.

```mermaid
flowchart LR
    Study1 --> Study1_Common["Common"]
    Study1 --> Study1_Test1["Test1"]
    Study1 --> Study1_Test2["Test2"]
    Study1 --> Study1_Test3["..."]
    
    Study1_Common --> common1_param1["parameter1 = ..."]
    Study1_Common --> common1_param2["parameter2 = ..."]
    Study1_Common --> common1_param4["parameter4 = ..."]
    Study1_Common --> common1_input1["input1.txt _(uploaded)_"]

    Study1_Test1 --> test1_param3["parameter3 = ..."]
    Study1_Test1 --> test1_input2["input2 _(uploaded)_"]

    Study1_Test2 --> test2_param3["parameter3 = ..."]
    Study1_Test2 --> test2_input2["input2 _(uploaded)_"]

    Study1_Test3 --> test4_param3["parameter3 = ..."]
    Study1_Test3 --> test4_input2["input2 _(uploaded)_"]

    Study2 --> Study2_Common["Common"]
    Study2 --> Study2_Test1["Test1"]
    Study2 --> Study2_Test2["Test2"]
    Study2 --> Study2_Test3["..."]
    
    Study2_Common --> common2_param3["parameter3 = ..."]
    Study2_Common --> common2_param4["parameter4 = ..."]
    Study2_Common --> common2_input1["input1.txt _(uploaded)_"]
    Study2_Common --> common2_input2["input2 _(uploaded)_"]

    Study2_Test1 --> test1_param1["parameter1 = ..."]
    Study2_Test1 --> test1_param2["parameter2 = ..."]

    Study2_Test2 --> test2_param1["parameter1 = ..."]
    Study2_Test2 --> test2_param2["parameter2 = ..."]

    Study2_Test3 --> test4_param1["parameter1 = ..."]
    Study2_Test3 --> test4_param2["parameter2 = ..."]
```

### Results

At the end of the execution, results are stored in a structured output tree, ready for review or further processing. The outputs are first organized by **Proc**, each of them writing its own result data. Within each **Proc**, the results are further subdivided by experiment _(Test1, Test2, ...)_, ensuring a clear separation and traceability of outcomes across the entire study.

This organization is automatically determined based on how the study is configured by the operator. **NUREMICS®** analyzes which input data are marked as _fixed_ or _variable_, and how they connect to the internal workflow of the **App**. If a **Proc** directly depends on _variable_ inputs, or indirectly through upstream dependencies, it will generate distinct outputs for each experiment. Otherwise, it will produce shared outputs only once.

This logic ensures that only the necessary parts of the workflow are repeated during experimentation, and that the output structure faithfully reflects the configuration of the study along with the internal dependencies within the workflow.

```mermaid
flowchart LR
    Study1 --> Study1_MyProc["MyProc"]
    Study1 --> Study1_AnotherProc["AnotherProc"]

    Study1_MyProc --> Study1_MyProc_Common_output1["output1.csv"]
    Study1_MyProc --> Study1_MyProc_Common_output2["output2"]

    Study1_AnotherProc --> Study1_AnotherProc_Test1["Test1"]
    Study1_AnotherProc --> Study1_AnotherProc_Test2["Test2"]
    Study1_AnotherProc --> Study1_AnotherProc_Test3["..."]

    Study1_AnotherProc_Test1 --> Study1_AnotherProc_Test1_output3["output3.vtk"]
    Study1_AnotherProc_Test2 --> Study1_AnotherProc_Test2_output3["output3.vtk"]
    Study1_AnotherProc_Test3 --> Study1_AnotherProc_Test3_output3["output3.vtk"]




    Study2 --> Study2_MyProc["MyProc"]
    Study2 --> Study2_AnotherProc["AnotherProc"]

    Study2_MyProc --> Study2_MyProc_Test1["Test1"]
    Study2_MyProc --> Study2_MyProc_Test2["Test2"]
    Study2_MyProc --> Study2_MyProc_Test3["..."]

    Study2_MyProc_Test1 --> Study2_MyProc_Test1_output1["output1.csv"]
    Study2_MyProc_Test1 --> Study2_MyProc_Test1_output2["output2"]
    Study2_MyProc_Test2 --> Study2_MyProc_Test2_output1["output1.csv"]
    Study2_MyProc_Test2 --> Study2_MyProc_Test2_output2["output2"]
    Study2_MyProc_Test3 --> Study2_MyProc_Test3_output1["output1.csv"]
    Study2_MyProc_Test3 --> Study2_MyProc_Test3_output2["output2"]

    Study2_AnotherProc --> Study2_AnotherProc_Test1["Test1"]
    Study2_AnotherProc --> Study2_AnotherProc_Test2["Test2"]
    Study2_AnotherProc --> Study2_AnotherProc_Test3["..."]

    Study2_AnotherProc_Test1 --> Study2_AnotherProc_Test1_output3["output3.vtk"]
    Study2_AnotherProc_Test2 --> Study2_AnotherProc_Test2_output3["output3.vtk"]
    Study2_AnotherProc_Test3 --> Study2_AnotherProc_Test3_output3["output3.vtk"]
```

## Get Started

Now that you've explored the foundational concepts behind the **NUREMICS®** framework, it's time to go deeper into the matrix.

You can now head over to the [`nuremics-apps`](https://github.com/nuremics/nuremics-apps) repository, where the real adventure begins: you'll learn how to define domain-specific **Procs**, assemble them into complete **Apps**, and run them as an end-user.

Welcome to the code 🧬