import subprocess
import json
import glob
import urllib.request
import os

if not os.path.exists("output"):
    os.makedirs("output")
 
def GetImage(id, image, tag):
    print("Image:", image, tag)
    subprocess.run([
        "skopeo", 
        "--override-arch",
        "amd64",
        "--override-os",
        "linux",
        "copy",
        f"docker://{image}:{tag}",
        f"docker-archive:output/skycore_image_{id}_{tag}.tar:{image}:{tag}"]) 

def GetManifest(filename, url):
    print("Manifest:", url)
    urllib.request.urlretrieve(url, f"output/skycore_manifest_{filename}")

def GetHelmChart(name, repo, chart, version):
    print("Helm Chart:", repo, chart, version)
    if (repo.startswith("oci://")):
        subprocess.run([
            "helm", 
            "pull",
            "--version",
            version,
            f"{repo}/{chart}",
            "-d",
            "output/"
            ]) 

    else:
        subprocess.run([
            "helm", 
            "pull",
            "--version",
            version,
            chart,
            "-d",
            "output/",
            "--repo",
            repo
            ]) 
    filename = f"output/skycore_chart_{name}_{chart}_{version}.tgz"
    os.rename(f"output/{chart}-{version}.tgz", filename)
 
files = glob.glob("operators/*")
for filepath in files:
    # Opening JSON file
    file = open(filepath)
    operator = json.load(file)
    for image in operator['images']:
        GetImage(image['id'], image['image'], image['tag'])
    for manifest in operator['manifests']:
        GetManifest(manifest['filename'], manifest['url'])
    for chart in operator['charts']:
        GetHelmChart(operator['name'], chart['repo'], chart['chart'], chart['version'])
    # Closing file
    file.close()
 
