# CredPred

The CrePred web application predicts credit scores for loan applicants, explaining the result, providing tips to improve the credit score, and recommending institutions where the user can apply for a loan along with the loan acceptance rate.

## How to start the project
> 👉 **Step 1** - Download Docker and start the docker app

If you do not have docker in you computer, please go to https://www.docker.com/products/docker-desktop/ to download docker desktop and install on you computer.

If you have docker in you computer, skip the download step and start the docker app.

> 👉 **Step 2** - Download the code from the GH repository (using `GIT`) 

```bash
$ git clone https://github.com/HengBrandon/wil_project_18.git
$ cd wil_project_18
```

> 👉 **Step 3** - Download trained model 

Download the model from this link: https://drive.google.com/file/d/1SJ24lsX5ctd_wBnDG4XbCd6-AT8IPXHV/view

And paste the model into
```
wil_project_18/home/models
```

<br />

> 👉 **Step 4** - Start the APP in `Docker`

```bash
$ chmod +x entrypoint.sh
$ docker-compose up --build 
```

Visit `http://localhost:5085` in your browser. The app should be up & running.
