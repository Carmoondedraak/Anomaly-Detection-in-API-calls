# Demo Scripts
This folder collects an ordered list of demos, that can be run one after the other to show all relevan SCN functionalities.

Each folder contains also a link to a recording.

Follow the step below to setup your environment

## Deploy a SCN instance

Deploy a dev instance of SCN through Jenkins or obtain access to one.

Currently tested with the following branch:
https://engci-private-sjc.cisco.com/jenkins/eti-sre/job/k8sec/job/k8sec-server-dev/job/aduminuc-app-demo/

Build with parameters:
  * Unselect "build and push"
  * Select "deploy manual clean"
  * Insert a namespace or leave it blank to use your CEC id (e.g. aduminuc)
  * Select "demo app script" as post deploy action

  Your instance will be availabe at https://[namespace].demo.portshift.co/ (e.g. https://aduminuc.demo.portshift.co/)

## Connect to a k8s cluster
  Get access to a clean k8s cluster. That should be connected in one of the context available from your kubectl, i.e. present in the outout of 
  ```
  kubectl config get-contexts
  ```

## Adjust config.sh to your needs

  Make sure config.sh reflects your setup

## Install needed libraries 
1. Make sure to have python3 installed
1. Run `make clean setup`

## Run your demos
Enter the demo folder in order and either follow the instructions or run the script `execute.sh`

# Demo recordings
Demos are available at the following location:
https://cisco.sharepoint.com/sites/ApplicationSecurityVenture/Shared%20Documents/Forms/AllItems.aspx?csf=1&web=1&e=4hjjy2&cid=721f0c6d%2Dc076%2D4162%2D9e84%2Dd745506daef8&RootFolder=%2Fsites%2FApplicationSecurityVenture%2FShared%20Documents%2FDemo%20recordings%2FMVP2%20%2D%20API%20Security%20Demo%20Recordings&FolderCTID=0x012000AC210AF0E9BDC44DA9879680FB3FAA64



