#####:candy:
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
      file.sh or *.sh
      file.py or *.py
```

### Categories
- [builds](https://google.com)
- [deploys](https://google.com)

#### Builds

##### go build
##### docker bake


#### Deploys
##### kubernetes