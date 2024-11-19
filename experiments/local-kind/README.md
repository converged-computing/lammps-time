# LAMMPS in Kind

Let's run our LAMMPS containers in kind, meaning we will run the experiment across nodes.

## 1. Create a Cluster

```bash
kind create cluster --config ./kind-config.yaml
```

Install the Flux Operator. Each lammps experiment will be the base container with flux.

```bash
kubectl apply -f https://raw.githubusercontent.com/flux-framework/flux-operator/refs/heads/main/examples/dist/flux-operator.yaml
```

Then run the experiments!

```bash
# Default problem size 4 x 4 x 4 is just under 2 minutes
python run-experiment.py
```

Then parse the single result files into output files for each.

```bash
python parse-results.py
```

This will generate the output and recordings directories in [results](results). Next, do the analyses.

```bash
# Generate the distance data frame and levenstein distance clustermap image
compatlib analyze-recording -d ./results --cmap viridis $(find ./results/recordings -name *.out)

# Generate a trie that shows access paths (not order or pattern) and overall count matrix
compatlib plot-recording -d ./results $(find ./results/recordings -name *.out)

# Run markov models, generating a pdf of residuals for each
compatlib run-models -d ./results $(find ./results/recordings -name *.out)
```
```console
Markov Model Results
  Leave one out correct: 4999
    Leave one out wrong: 1148
          correct/total: 0.8132422319830812
Frequency Results
  Leave one out correct: 617
    Leave one out wrong: 5533
          correct/total: 0.10032520325203252
```
