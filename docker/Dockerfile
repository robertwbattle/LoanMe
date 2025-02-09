# Use Ubuntu Jammy as the base image
FROM ubuntu:22.04

# Set environment variables to ensure non-interactive installs
ENV DEBIAN_FRONTEND=noninteractive

# Update apt and install Python 3, Git, and other dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip git && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Clone the repository from GitHub
RUN git clone https://github.com/robertwbattle/LoanMe.git

# Change into the repo directory
WORKDIR /app/LoanMe

# Install any Python dependencies if they exist
# Uncomment the following line if there's a requirements.txt
# RUN pip3 install -r requirements.txt
