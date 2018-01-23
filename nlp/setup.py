import subprocess
import nltk

print(">>Downloading training data...\n")
subprocess.call(["mkdir", "data"])
subprocess.call(["mkdir", "models"])
subprocess.call(["wget", "http://mlg.ucd.ie/files/datasets/bbc-fulltext.zip"],
                cwd="./data")

print("\n>>Need root privelages to install unzip...\n")
subprocess.call(["sudo", "apt-get", "install", "unzip"])
subprocess.call(["unzip", "bbc-fulltext.zip"], cwd="./data")

print("\n>>Downloading necessary NLTK packages...\n")
nltk.download("stopwords")
nltk.download("wordnet")
