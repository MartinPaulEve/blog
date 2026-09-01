---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2023/10/20/connecting-to-aws-opensearch-serverless-using-python
date: 2023-10-20
doi: https://doi.org/10.59348/ay3y8-kk905
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
title: Connecting to AWS OpenSearch Serverless using Python
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lxic6nt2s"
categories:
- Programming
---

I recently wanted to use ElasticSearch (or OpenSearch as Amazon terms it from the fork) in an AWS environment, using Python. When I tried to connect I got a very painful 403 Forbidden error. Specifically: opensearchpy.exceptions.AuthorizationException: AuthorizationException(403, 'Forbidden').

The answer I needed was eventually here: https://opensearch.org/docs/latest/clients/python-low-level/. The key point is that, when using serverless, the service is not "es" but "aoss" (Amazon OpenSearch Serverless.

My ingest code (that now works) looks like this:

	def push_to_aws():
	    host = f"YOUR_DOMAIN.us-east-1.aoss.amazonaws.com"
	    credentials = boto3.Session().get_credentials()
	    region = "us-east-1" 
	    
	    # Sign the credentials
	    auth = AWSV4SignerAuth(credentials, region, service="aoss")

	    # The OpenSearch client
	    client = OpenSearch(
	        hosts=[{"host": host, "port": 443}],
	        http_auth=auth,
	        use_ssl=True,
	        verify_certs=True,
	        connection_class=RequestsHttpConnection,
	    )

	    my_index = "gen"

	    try:
	        response = client.indices.create(my_index)
	        print("\nCreating index:")
	        print(response)
	    except Exception as e:
	        print(e)

	    files = glob.glob("/home/martin/json_directory/*.json")

	    for file in files:
	        with open(file, "r") as f:
	            print(f"Processing {file}")
	            data = payload_constructor(data=json.load(f), action={"index": {}})

	            response = client.bulk(body=data, index=my_index)