# Provisioning and deploying to instances

Ansible and the Tequila role set make it easy to provision new servers and
deploy changes to the mesolex project. This guide will walk you through
the process of deploying, first, and then tell you how to set up a new
server.

## Deploying mesolex

### Setup

Before deploying, be sure to install the deployment requirements, which
are not by default included in dev setup:

```
(mesolex)$ pip install -r requirements/deploy.txt
```

### Getting authorization to deploy

As a first step to deploying the mesolex project, ensure that you have
generated for yourself a ssh key and that some mesolex maintainer
has added your public key to the project's index of authorized developers,
`deployment/playbooks/group_vars/all/devs.yml`. Your key will be added
in an entry that looks like this:

```
- name: nmashton
  public_keys:
    - "ssh-rsa AAAAB3NzaC1yc2EAAAA[...]"

```

If you don't know how to create your ssh key, Github offers some helpful
advice [here](https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/).

### Deploying

Once the mesolex maintainer has added your key and has deployed to the
relevant server to add your key to its authorized users, deploying to an
environment (e.g. `staging`) uses `ansible-playbook` along with the
`site.yml` playbook, which will refresh every aspect of the project:

```
(mesolex)$ ansible-playbook -i deployment/environments/<environment>/inventory deployment/playbooks/site.yml
```

If you know for sure that nothing about the web server, database, etc
has changed, you can simply run `web.yml` to run the subset of Ansible
tasks that affects the Django project's source code.


## Provisioning a new mesolex instance

Getting a new mesolex instance ready for deployment is not too
difficult. It amounts to generating a few "secrets", adding a new
subdirectory to `deployment/environments/` with some necessary
config files, and then running the usual deployment playbooks a few times in a
step-by-step way.

These instructions assume that you are running the web server, database,
and search engine on a single machine and that you are not using multiple
workers and a load balancer. This should be sufficient to handle the
level of traffic that this project will probably receive.

### Creating your new environment: first steps

Create a new subdirectory of `deployment/environments/`, and add a file
`inventory` that looks like this, replacing `mesolex_staging` by an internal
name for your server (this can be whatever you like) and replacing
`206.189.224.150` by its IP:

```
mesolex_staging ansible_host=206.189.224.150

[web]
mesolex_staging

[db]
mesolex_staging

[search]
mesolex_staging

[worker]
```

Now create the configuration file for this environment in `deployment/environments/<your env>/group_vars/all/vars.yml`.
Set it up to look like this, substituting your domain name for `mesolex.nmashton.work`
and adding any additional domains as bullets under `letsencrypt_domains`:

```
---
env_name: staging
domain: mesolex.nmashton.work
letsencrypt_domains:
  - mesolex.nmashton.work

## NOTE: if you're basing your file off an existing environment,
## make sure to change these settings as follows at first:
cert_source: none
force_ssl: false

requirements_file: "{{ source_dir }}/requirements/base.txt"

source_is_local: false
gunicorn_num_workers: 1
```

### Generating secrets

Next you will want to generate some secrets for your project. Create a
file in the root directory called `.vault_pass` and fill it with some
lengthy string of gibberish that will be your Ansible encryption key.
(*NOTE:* never accidentally check this file into the repo!)

Then create a file `deployment/environments/<your env>/group_vars/all/secrets.yml`
to hold your environment's secret settings. Fill it in with some initial
secret information like so:

```
---
admin_email: 'your+email+address@example.com'

SECRET_KEY: 'a lengthy secure password'
SECRET_DB_PASSWORD: 'another equally secure and lengthy password'
```

Now you will need to generate a Github deploy key for the project.
This will allow the server to interact with Github during deployment.
To do this, run `make` in the project root like so (you may need to
edit the `Makefile` with the name of your target environment if it
is something other than `staging` or `production`):

```
(mesolex)$ make deployment/keys/staging.pub.ssh
```

This will generate two files: `staging.priv` (the private key) in the
root directory and `staging.pub.ssh` (the public key) in `deployment/keys/`.

Take the contents of `staging.pub.ssh` and add them to [the project's deploy keys](https://github.com/nmashton/mesolex/settings/keys),
assuming you have the necessary permissions to do so. (If you don't, ask
a maintainer for help.)

Now take the contents of `staging.priv` and add them to `secrets.yml` like
so:

```
SECRET_GITHUB_DEPLOY_KEY: |
  -----BEGIN RSA PRIVATE KEY-----
  asdfasdfasdf...
```

Now it's time to *encrypt* the contents of `secrets.yml`, which you can do
with `ansible-vault`:

```
(mesolex)$ ansible-vault encrypt deployment/environments/<your env>/group_vars/all/secrets.yml
```

It is now safe to check `secrets.yml` into the repo.

## Initial provisioning

Before doing anything else, you will need to ensure that your new server
has Python 2 installed, without which Ansible won't be able to do its thing.

Most likely your new server does not have a user and ssh key set up for you
yet, so you will have to use a premade `root` user to run the first few
commands. If you are using a Digital Ocean droplet, this user will be `root`.

Run the playbook to install Python 2 on your server:

```
(mesolex)$ ansible-playbook ansible-playbook -i deployment/environments/<your env>/inventory deployment/playbooks/bootstrap_python.yml -u root
```

Having done that, you should be able to run all other playbooks.
You can now run the entire `site.yml` playbook to deploy the entire project
with initial settings:

```
(mesolex)$ ansible-playbook ansible-playbook -i deployment/environments/<your env>/inventory deployment/playbooks/site.yml
```

## Setting up SSL and http auth

You will certainly want to enable SSL on your new instance, and if it's a
private environment (e.g. a new staging environment), you will also want
to enable HTTP auth to prevent your "work in progress" code from being
indexed by search engines.

To generate an SSL cert, we will use Letsencrypt. In the earlier step
"Creating your new environment", we explicitly disabled SSL. This is
because the easiest way to get Letsencrypt to generate a cert is to
enable SSL step by step.

In the first step, change `vars.yml` to have `cert_source: letsencrypt`.
(**NOTE** that `force_ssl` must still be `false` at this stage!)
Now rerun deployment, or simply run the `web.yml` playbook to speed
things up a little. If this succeeds, an SSL cert will have been
generated.

Once that has happened, it is safe (and advisable) to set `force_ssl: true`
in `vars.yml`. Now all traffic will be redirected to `https`.

If you want to enable HTTP auth, you will have to add it in `secrets.yml`.
(You can decrypt the secrets file by rerunning the `ansible-vault` command
given above with `decrypt` instead of `encrypt`.)

```
http_auth:
  - login: username
    password: password
```

Having added that, re-encrypt your secrets and deploy `web.yml` another time.
