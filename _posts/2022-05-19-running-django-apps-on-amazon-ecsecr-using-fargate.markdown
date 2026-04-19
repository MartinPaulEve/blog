---
title: "Running Django apps on AWS Fargate with a serverless RDS"
layout: post
image: 
    feature: geek.png
doi: "https://doi.org/10.59348/k6z7j-a6z38"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2022/05/19/running-django-apps-on-amazon-ecsecr-using-fargate"
---
There are several tutorials out there on how to get Django apps dockerized and deployed onto AWS Fargate. None of them worked for me. So I have put together [a project demonstrating how to do this](https://github.com/MartinPaulEve/django-fargate). It's available [on Github](https://github.com/MartinPaulEve/django-fargate).

The scenario I wanted to create was something like this:

![Infrastructure](/images/containerized_django_on_aws.png)

I wanted the infrastructure to have:

* Load balancing
* SSL (with termination at the load balancer)
* Serverless auto-scaling
* Serverless database
* Containerized Django

There were loads of "gotchas" along the way. For instance, getting two containers to run and interact with each other on the same network interface. The fact that you can't use docker-compose.yml "commands" to start the container. The load balancer wouldn't allow an HTTP target group for an HTTPS listener in extant modules. Getting the database to be accessible proved to be a networking pain. Setting the database password to a randomly generated string didn't work. The list goes on.

In any case, the project now seems to work!





