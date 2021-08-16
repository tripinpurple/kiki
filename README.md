# :candy:
as it goes "Bilo kuda, Ki-Ki svuda!"
## kontinuirana integracija <br> kontinuirana implementacija

or kiki for short

### Description:
kiki is a CI/CD collection of tools, written in python<br>
the main focus is to cut down on build and deploy time, by building only the files that have been modified as well as deploying the same ones

### Requirements:

Github Actions:
- [tj-actions/changed-files](https://google.com)

```
- name: Get specific changed files
  id: changed-files-specific
  uses: tj-actions/changed-files@master
  with:
    files: |
      services/*/
   
- name: List all modified files
  shell: bash
  run: |
    echo ${{ steps.changed-files.outputs.all_modified_files }}
```

### Categories
- [builds](build/)
- [deploys](deploy/)

#### Builds / docker bake
[bake-json.py](build/bake/bake-json.py)
```
Usage: bake-json.py [app] [service/path service/path] [registry] [tag]
```

#### Deploys / kubernetes
[kube.py](deploy/kube/kube.py)
```
Usage: kube.py [app] [service/path service/path] [registry] [tag] [namespace]
```