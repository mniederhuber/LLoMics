#!/bin/bash
#SBATCH -t 8:00:00
#SBATCH --mem=16G
#SBATCH -p interact
#SBATCH -n 8

module load anaconda
conda activate yobokop

host=$(hostname)
echo "Host: $host"

jupyter notebook --no-browser --NotebookApp.allow_origin='*' --NotebookApp.ip='0.0.0.0'
#jupyter lab --no-browser --ServerApp.allow_origin='*' --ServerApp.ip='0.0.0.0' --ServerApp.max_buffer_size=8589934592
