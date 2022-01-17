# Potential of Reinforcement Learninig in Flexible Modular Production System in Theory and Practise 

Author: Helen Haase <br>
Tutor : Bruno Baruque Zanón <br>
Departamento Ingenería Informática, Ciencia de la Computacíon e Inteligencia Artificial, Universidad de Burgos <br>

--------

## Description

This work focuses on investigating strategies to solve a Flexible Job Shop Problem scheduling problem regarding a Flexible Manufacturing System and developing a Reinforcment Learning based prototype as proof of concept to show optimization possibilities of hyperparameter tuning. <br>


The theoretical part of this work shows different strategies, that have been used to try and solve the scheduling problems by going through the search space with different techniques. These approaches comprise exhaustive and approximate algorithms as well as Reinforcement Learning. <br>

In the practical section a prototype is built, than can be seen as demonstration of a possible solution with Reinforcement Learning. It includes a production system modelled in Siemens Plant Simulation and Proximal Policy Optimization as well as a double Deep Q-Network agent, that are trained and compared. Experiments show the relevance of hyperparameter tuning and the resulting performances.

-------
## Overview of the Directory Structure

    
    📦data
    ┣ 📂experiments_training_duration_run_1
    ┃ ┣ 📂dem-100-df-0.99-lr-0.001-eps-20-expl-0.001-bat-1-mayer-act-1-ppo
    ┃ ┃ ┣ c
    ┃ ┃ ┣ 📜agent-0.index
    ┃ ┃ ┣ 📜agent.json
    ┃ ┃ ┣ 📜checkpoint
    ┃ ┃ ┣ 📜dem-100-df-0.99-lr-0.001-eps-20-expl-0.001-bat-1-mayer-act-1-ppo.xml
    ┃ ┃ ┗ 📜results.txt
    ┃ ┣ 📂[...]
    ┣ 📂[...]
    📦documentation
    ┣ 📂pdfs
    ┃ ┣ 📜report.pdf
    ┃ ┣ 📜annex_A.pdf
    ┃ ┗ 📜annex_B.pdf
    ┣ 📂texfiles
    ┃ ┗[...]
    📦src
    ┣ 📂simulation
    ┃ ┣ 📜simulation_models.spp
    ┃ ┣ 📜simulation_models.spp.bak
    ┃ ┗ 📜filehandler.bat
    ┣ 📂agent
    ┃ ┣ 📜main.py
    ┃ ┣ 📜SPSEnvironemnt.py
    ┃ ┣ 📜globalConstants.py
    ┃ ┣ 📜DataExchanger.py
    ┃ ┣ 📜ExperimentCreator.py
    ┃ ┣ 📜GenerateExperiments.py
    ┃ ┗ 📜dynamicConfigurations.py
    ┣ 📂experiments
    ┃ ┃ ┣ 📂dem-100-df-0.99-lr-0.001-eps-100-expl-0.01-bat-1-mayer_+_10000_-5-act-1-ppo
    ┃ ┃ ┣ 📂dem-100-df-0.99-lr-0.001-eps-100-expl-0-bat-1-mayer_+_10000_-5-act-1-ppo
    ┃ ┃ ┗ 📜experiment.txt
    ┣ 📂communication
    ┣ 📂analysis
    ┃ ┗ 📜plotter.ipynb
    📜Readme.md

    
---
## Requirements and Installation 

Siemens Plant Simulation suggests the following minimal requirements: 

| Type | Requirement |
|---|---|
| Operating System | Windows 8.1/10 |
| Memory (RAM)     | 4GB                |
| Hard Disc Space  | 2GB                |
| Processor        | x84-64 Processor   |
        
Since the software performs a lot of writing and reading commands as well as a computational heavy algorithm, it is recommended to use a computer with at least a 8GB RAM. 

For information about the installation, please refer to chapter 5 of Annex A.
