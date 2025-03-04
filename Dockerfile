# We use a Miniconda-based image
FROM continuumio/miniconda3:latest

# We need to set up a working directory
WORKDIR /app

# We need to copy the code + environment.yml
COPY . .

# Create the Conda environment if environment.yml exists
RUN if [ -f environment.yml ]; then conda env create -f environment.yml; fi

# Make directories for PDFs and outputs
RUN mkdir -p /app/papers /app/grobid_output

# Make volumes so PDFs and outputs can be shared outside container
VOLUME ["/app/papers", "/app/grobid_output"]

# This will add the environment bin folder to PATH
# So 'python' and libraries will come from grobid_env
ENV PATH /opt/conda/envs/grobid_env/bin:$PATH

# run the script
CMD ["bash", "-c", "python script.py"]
