---
archive: https://wayback.archive-it.org/22123/20241101171236/https://eve.gd/2025/01/08/getting-knowledge-commons-works-running-locally
date: 2025-01-08
doi: https://doi.org/10.59348/gzztd-62q63
roguescholar: https://rogue-scholar.org/records/c1n6w-v3e34
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lwcrllj2h
image:
  feature: header_kcw.png
layout: post
ogImage: images/header_kcw.png
title: Getting Knowledge Commons Works running locally
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lwcrllj2h"
categories:
- Scholarly Communications
- Programming
kcworks: https://works.hcommons.org/records/sfg6g-mah16
---

This week, I have started work at Michigan State University, as interim technical lead on the Knowledge Commons project. I'll probably say more about this at some point soon.

However, a huge part of onboarding at new digital/software places is getting your head around the stack and trying to get a development environment setup and ready to use. Often, this means relying on documentation that has fallen out of sync and/or trying to intuit things that some other developer thought was obvious (not blaming anyone, there, just noting it). So, in the spirit of documenting things for anyone else trying to do this, here's my notes on getting an instance of Knowledge Commons Works (the repository component) up and running locally.

First: the quick start instructions are fairly good.[^1] However, what isn't clear is what you need in the .env file as a bare minimum. Mine looks like this:

	INVENIO_INSTANCE_PATH=/opt/invenio/var/instance
	INVENIO_RECORD_IMPORTER_LOCAL_DATA_DIR=/
	INVENIO_RECORD_IMPORTER_DATA_DIR=/opt/invenio/var/import_data
	INVENIO_SEARCH_DOMAIN='search:9200'
	INVENIO_SITE_UI_URL="https://localhost"
	INVENIO_SITE_API_URL="https://localhost/api"
	REDIS_DOMAIN='cache:6379'
	INVENIO_SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://kcworks:PASSWORDHERE@db/kcworks" # DON'T FORGET TO CHANGE THE PASSWORD HERE
	POSTGRES_USER=kcworks
	POSTGRES_DB=kcworks
	INVENIO_CSRF_SECRET_SALT='GENERATE_IT_AS_PER_INSTRUCTIONS'
	INVENIO_SECURITY_LOGIN_SALT='GENERATE_IT_AS_PER_INSTRUCTIONS'
	INVENIO_SECRET_KEY='SECRET_KEY_VERY_SECRET'
	COMMONS_API_TOKEN=mytoken  # this must be obtained from the Commons administrators - just leave as is
	COMMONS_SEARCH_API_TOKEN=mytoken  # this must be obtained from the Commons administrators - just leave as is
	INVENIO_DATACITE_PASSWORD=myinveniodatacitepassword  # this must be obtained from the Commons administrators - just leave as is
	API_TOKEN=myapitoken # just leave as is
	PYTHON_LOCAL_GIT_PACKAGES_PATH=/home/martin/Documents/Programming/MESH/knowledge-commons-works # set this to the base directory
	PYTHON_LOCAL_SITE_PACKAGES_PATH=~/.local/share/virtualenvs/knowledge-commons-works-4DIkhDKF/lib/python3.12/site-packages # you need this for dev
	POSTGRES_PASSWORD=PASSWORDHERE
	PGADMIN_DEFAULT_EMAIL=martin@eve.gd
	PGADMIN_DEFAULT_PASSWORD=PASSWORDHERE
	INVENIO_LOCAL_INSTANCE_PATH=/opt/invenio/var/instance	


In order to populate the virtualenv, I had to make some changes to the Pipfile so that it would run on my machine:

	[[source]]
	name = "pypi"
	url = "https://pypi.org/simple"
	verify_ssl = true
	[dev-packages]
	check-manifest = ">=0.25"
	halo = "*"
	jsonlines = "*"
	requests-mock = "*"
	selenium = "*"
	docker-services-cli = "*"
	[packages]
	aiohttp = "*"
	async-timeout = ">=4.0.3"
	cchardet = "*"
	flask-admin = "==1.6.1"
	flask-babelex = "*"
	flask-breadcrumbs = "*"
	flask-principal = "*"
	greenlet = {}
	halo = "*"
	invenio-app-rdm = { extras = ["opensearch2"]}
	invenio-communities = {editable = true, path = "./site/kcworks/dependencies/invenio-communities"}
	invenio-group-collections-kcworks = {editable = true, path = "./site/kcworks/dependencies/invenio-group-collections-kcworks"}
	invenio-modular-deposit-form = {editable = true, path = "./site/kcworks/dependencies/invenio-modular-deposit-form"}
	invenio-modular-detail-page = {editable = true, path = "./site/kcworks/dependencies/invenio-modular-detail-page"}
	invenio-rdm-records = {editable = true, path = "./site/kcworks/dependencies/invenio-rdm-records"}
	invenio-record-importer-kcworks = {editable = true, path = "./site/kcworks/dependencies/invenio-record-importer-kcworks"}
	invenio-records-resources = {editable = true, path = "./site/kcworks/dependencies/invenio-records-resources"}
	invenio-remote-api-provisioner = {editable = true, path = "./site/kcworks/dependencies/invenio-remote-api-provisioner"}
	invenio-remote-user-data-kcworks = {editable = true, path = "./site/kcworks/dependencies/invenio-remote-user-data-kcworks"}
	invenio-s3 = "*"
	invenio-saml = "*"
	invenio-subjects-fast = "*"
	invenio-utilities-tuw = "*"
	invenio-vocabularies = {editable = true, path = "./site/kcworks/dependencies/invenio-vocabularies"}
	isbnlib = "*"
	langdetect = "*"
	numpy = "*"
	pip = "*"
	pytest-invenio = "*"
	python-dotenv = "*"
	python-iso639 = "*"
	python-stdnum = "*"
	selenium = "*"
	sqlalchemy = { extras = ["asyncio"]}
	timefhuman = "*"
	titlecase = "*"
	tqdm = "*"
	unidecode = "*"
	uwsgi = ">=2.0"
	uwsgi-tools = ">=1.1.1"
	uwsgitop = ">=0.11"
	xmlsec = "<1.3.14"
	kcworks = {file = "site", editable = true}
	[requires]
	python_version = "3.9"
	[pipenv]
	allow_prereleases = true

The main change here was:

	cchardet = "*"

This allowed me to run:

	pipenv install --dev --python=3.12

Then you need to:

    docker-compose --file docker-compose.yml up -d

and

	docker exec -it kcworks-ui bash

Once you are in the container, you should be able to run:

	bash ./scripts/setup-services.sh

and select local storage, which will get everything setup. If you get database access errors, take a close look at the .env file and ensure that the INVENIO_SQLALCHEMY_DATABASE_URI has the password set. I didn't realise for quite some time that you have to update the schema here.



[^1]: See [https://github.com/MESH-Research/knowledge-commons-works](https://github.com/MESH-Research/knowledge-commons-works)