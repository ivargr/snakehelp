

# Snakehelp

A small Python package for making writing Snakemake pipelines easier to write, easier to maintain and with fewer bugs.

## Motivation

Snakemake-pipelines often end up with long wildcards paths, which are hard to read, often copied between and hard to debug when something doesn't work:

```snakemake

rule simulate:
    output:
        data = "data/{param1}/{param2}/{param3}/{param4}/data.csv"
```

Often the `{param1}/{param2}/..` and so on are copy-pasted and hardcoded into several rules, so that when
you want to add a new parameter,



